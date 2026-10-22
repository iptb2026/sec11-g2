from datetime import datetime, timedelta
import pyotp
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.security import get_current_user, oauth2_scheme, check_password
from app.core.otp import secret_cipher, digest, verify_code, recovery_codes, throttle, ensure_unlocked
from app.core.db_utils import commit_or_409
from app.models.user import User
from app.models.pin import PinChallenge
from app.models.otp import OtpCredential, OtpChallenge
from app.models.session import UserSession
from app.routers.auth import begin_pin

router = APIRouter(prefix="/auth/otp", tags=["Authenticator OTP"])


class PasswordInput(BaseModel):
    password: str = Field(max_length=200)


class CodeInput(BaseModel):
    code: str = Field(min_length=6, max_length=32)


class VerifyInput(CodeInput):
    challenge_token: str = Field(min_length=20, max_length=100)


class DisableInput(PasswordInput, CodeInput):
    pass


def current_user(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(User).filter(User.username == username).first()


def credential_for(db, user):
    return db.query(OtpCredential).filter(OtpCredential.user_id == user.id).with_for_update().first()


def check_current_password(db, user, password):
    throttle(db, "reauth:" + user.username)
    if not check_password(password, user.hashed_password):
        raise HTTPException(400, "Current password is incorrect")


def revoke_other_sessions(db, user, token):
    db.query(PinChallenge).filter(PinChallenge.user_id == user.id, PinChallenge.used_at.is_(None)).update({"used_at": datetime.utcnow()})
    db.query(UserSession).filter(UserSession.user_id == user.id, UserSession.jwt_token != token, UserSession.revoked_at.is_(None)).update({"revoked_at": datetime.utcnow()})
    db.query(OtpChallenge).filter(OtpChallenge.user_id == user.id, OtpChallenge.used_at.is_(None)).update({"used_at": datetime.utcnow()})


@router.get("/status")
def status(user: User = Depends(current_user), db: Session = Depends(get_db)):
    credential = credential_for(db, user)
    return {"enabled": bool(credential and credential.enabled), "recovery_codes_remaining": len(credential.recovery_hashes or []) if credential and credential.enabled else 0}


@router.post("/setup")
def setup(data: PasswordInput, response: Response, user: User = Depends(current_user), db: Session = Depends(get_db)):
    check_current_password(db, user, data.password)
    credential = credential_for(db, user)
    if credential and credential.enabled:
        raise HTTPException(409, "Authenticator verification is already enabled")
    if credential:
        ensure_unlocked(credential)
    else:
        credential = OtpCredential(user_id=user.id)
        db.add(credential)
    secret = pyotp.random_base32()
    credential.encrypted_secret = secret_cipher().encrypt(secret.encode()).decode()
    credential.setup_expires_at = datetime.utcnow() + timedelta(minutes=10)
    credential.last_counter = -1
    commit_or_409(db, "Authenticator setup is already in progress. Please retry.")
    response.headers["Cache-Control"] = "no-store"
    return {"secret": secret, "provisioning_uri": pyotp.TOTP(secret).provisioning_uri(name=user.username, issuer_name="Bembank"), "expires_in": 600}


@router.post("/confirm")
def confirm(data: CodeInput, response: Response, user: User = Depends(current_user), token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credential = credential_for(db, user)
    if not credential or credential.enabled or not credential.setup_expires_at or credential.setup_expires_at <= datetime.utcnow():
        raise HTTPException(400, "Setup has expired or is already complete. Start setup again if needed.")
    verify_code(db, credential, data.code, allow_recovery=False)
    codes, hashes = recovery_codes()
    credential.enabled = True
    credential.setup_expires_at = None
    credential.recovery_hashes = hashes
    revoke_other_sessions(db, user, token)
    db.commit()
    response.headers["Cache-Control"] = "no-store"
    return {"enabled": True, "recovery_codes": codes}


@router.post("/verify")
def verify(data: VerifyInput, request: Request, response: Response, db: Session = Depends(get_db)):
    challenge = db.query(OtpChallenge).filter(OtpChallenge.token_hash == digest(data.challenge_token)).first()
    if not challenge:
        raise HTTPException(400, "Sign-in request expired. Enter your username and password again.")
    # Lock the credential first so concurrent challenges cannot reuse the same code.
    credential = db.query(OtpCredential).filter(OtpCredential.user_id == challenge.user_id).with_for_update().first()
    challenge = db.query(OtpChallenge).filter(OtpChallenge.token_hash == digest(data.challenge_token)).populate_existing().with_for_update().first()
    if challenge.used_at or challenge.expires_at <= datetime.utcnow() or not credential or not credential.enabled:
        raise HTTPException(400, "Sign-in request expired. Enter your username and password again.")
    user = db.query(User).filter(User.id == challenge.user_id, User.account_status == "ACTIVE").first()
    if not user:
        raise HTTPException(403, "Account is not active")
    verify_code(db, credential, data.code)
    challenge.used_at = datetime.utcnow()
    response.headers["Cache-Control"] = "no-store"
    return begin_pin(user, db)


@router.post("/disable", status_code=204)
def disable(data: DisableInput, user: User = Depends(current_user), token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    check_current_password(db, user, data.password)
    credential = credential_for(db, user)
    if not credential or not credential.enabled:
        raise HTTPException(400, "Authenticator verification is not enabled")
    verify_code(db, credential, data.code)
    credential.enabled = False
    credential.encrypted_secret = None
    credential.recovery_hashes = []
    credential.last_counter = -1
    revoke_other_sessions(db, user, token)
    db.commit()
