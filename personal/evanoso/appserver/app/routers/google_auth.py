"""Google Identity Services sign-in; Google never replaces the account PIN."""
import os
import secrets
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.security import hash_password, check_password
from app.core.otp import digest, throttle
from app.core.audit import record_audit_event
from app.models.google_identity import GoogleIdentity, GoogleChallenge
from app.models.user import User
from app.models.role import Role
from app.models.account import Account
from app.models.account_type import AccountType
from app.routers.auth import begin_login

router = APIRouter(prefix='/auth/google', tags=['Google sign-in'])

def client_id():
    value = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
    if not value:
        raise HTTPException(503, 'Google sign-in is not configured yet. Use email and password to sign up or sign in.')
    return value


def verify_google_token(credential, audience):
    # The official library verifies Google's signature, audience, expiry and issuer.
    try:
        from google.oauth2 import id_token
        from google.auth.transport.requests import Request as GoogleRequest
        from google.auth.exceptions import TransportError, GoogleAuthError
    except ImportError:
        raise HTTPException(503, 'Google sign-in is temporarily unavailable.')
    try:
        return id_token.verify_oauth2_token(credential, GoogleRequest(), audience)
    except TransportError:
        raise HTTPException(503, 'Could not reach Google. Please try again.')
    except (ValueError, GoogleAuthError):
        raise HTTPException(400, 'Google could not verify this sign-in. Please try again.')


@router.get('/config')
def config(request: Request, response: Response, db: Session = Depends(get_db)):
    audience = client_id()
    throttle(db, 'google-start:' + (request.client.host if request.client else 'unknown'))
    nonce = secrets.token_urlsafe(32)
    db.add(GoogleChallenge(token_hash=digest(nonce), expires_at=datetime.utcnow() + timedelta(minutes=10)))
    db.commit()
    response.headers['Cache-Control'] = 'no-store'
    return {'client_id': audience, 'nonce': nonce}


class GoogleInput(BaseModel):
    credential: str = Field(min_length=20, max_length=10000)
    nonce: str = Field(min_length=20, max_length=100)
    password: str | None = Field(default=None, max_length=200)


@router.post('/verify')
def verify(data: GoogleInput, request: Request, response: Response, db: Session = Depends(get_db)):
    audience = client_id()
    throttle(db, 'google-verify:' + (request.client.host if request.client else 'unknown'))
    claims = verify_google_token(data.credential, audience)
    if (not claims.get('sub') or len(claims['sub']) > 255 or claims.get('email_verified') is not True
            or not claims.get('email') or claims.get('nonce') != data.nonce):
        raise HTTPException(400, 'Google sign-in could not be verified. Please try again.')
    # Account-level limits also apply when linking an existing login.
    throttle(db, 'google-account:' + claims['sub'])
    challenge = db.query(GoogleChallenge).filter(GoogleChallenge.token_hash == digest(data.nonce)).with_for_update().first()
    if not challenge or challenge.used_at or challenge.expires_at <= datetime.utcnow():
        raise HTTPException(400, 'Google sign-in expired. Reload the page and try again.')
    identity = db.get(GoogleIdentity, claims['sub'])
    user = db.get(User, identity.user_id) if identity else db.query(User).filter(func.lower(User.email) == claims['email'].lower()).first()
    if user and user.account_status != 'ACTIVE':
        raise HTTPException(403, 'Account is not active')
    if user and not identity:
        if not data.password:
            return {'password_required': True}
        if not check_password(data.password, user.hashed_password):
            raise HTTPException(400, 'Incorrect password. Enter this account’s existing password to connect Google.')
        if db.query(GoogleIdentity).filter(GoogleIdentity.user_id == user.id).first():
            raise HTTPException(409, 'This account is already connected to a different Google account.')
    try:
        if not user:
            role = db.query(Role).filter(Role.role_code == 'CUSTOMER').first()
            account_type = db.query(AccountType).filter(AccountType.type_code == 'FAMILY_SAVINGS').first()
            if not role or not account_type:
                raise HTTPException(503, 'Account creation is temporarily unavailable.')
            user = User(username='google_' + uuid4().hex, email=claims['email'],
                        first_name=(claims.get('given_name') or claims.get('name') or 'Google')[:100],
                        last_name=(claims.get('family_name') or 'User')[:100],
                        hashed_password=hash_password(secrets.token_urlsafe(40)),
                        role_id=role.id, account_status='ACTIVE')
            db.add(user)
            db.flush()
            account = Account(customer_id=user.id, account_type_id=account_type.id,
                              account_number='BEM' + uuid4().hex[:20].upper(),
                              available_balance=0, ledger_balance=0, currency_code='PHP', status='ACTIVE')
            db.add(account)
            db.flush()
            record_audit_event(db, request, 'CREATE', 'accounts', account.id,
                               new_value={'customer_id': user.id, 'account_number': account.account_number, 'opening_balance': '0.00'})
        if not identity:
            db.add(GoogleIdentity(subject=claims['sub'], user_id=user.id))
        challenge.used_at = datetime.utcnow()
        response.headers['Cache-Control'] = 'no-store'
        return begin_login(user, db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Account details changed. Please try signing in again.')
