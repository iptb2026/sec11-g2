from app.core.password_policy import StrongPassword
# ==== LAYER 2: Identity & Access ====
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.core.security import check_password, create_token, oauth2_scheme, get_current_user, hash_password
from app.models.role import Role
from app.models.pin import PinCredential, PinChallenge
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from app.core.db_utils import commit_or_409
from app.database.session import get_db
from app.models.session import UserSession
from app.models.user import User
from app.schemas.auth import Token
from app.models.otp import OtpCredential, OtpChallenge
from app.core.otp import throttle, digest, ensure_unlocked
import secrets
import base64
import binascii
from io import BytesIO
from PIL import Image, ImageOps, UnidentifiedImageError
from app.models.profile_photo import ProfilePhoto

router = APIRouter(prefix="/auth", tags=["Layer 2 - Auth"])


@router.get("/me")
def me(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    role = db.query(Role).filter(Role.id == user.role_id).first()
    return {"id": user.id, "username": user.username, "first_name": user.first_name, "last_name": user.last_name, "email": user.email, "mobile_number": user.mobile_number, "account_status": user.account_status, "role_id": user.role_id, "role_code": role.role_code, "role_name": role.role_name}


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None
    mobile_number: str | None = Field(default=None, max_length=30)


@router.put("/profile")
def update_profile(data: ProfileUpdate, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    for key, value in data.model_dump().items():
        setattr(user, key, value)
    commit_or_409(db, "This email address is already in use. Choose another address.")
    return me(username, db)


class PasswordChange(BaseModel):
    current_password: str
    new_password: StrongPassword


class PhotoUpdate(BaseModel):
    image: str = Field(max_length=400_000)


@router.get("/profile-photo")
def get_profile_photo(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    photo = db.get(ProfilePhoto, user.id)
    return {"profile_photo": "data:image/jpeg;base64," + base64.b64encode(photo.image).decode() if photo else None}


@router.put("/profile-photo")
def update_profile_photo(data: PhotoUpdate, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        header, encoded = data.image.split(",", 1)
        if header not in {"data:image/jpeg;base64", "data:image/png;base64", "data:image/webp;base64"}:
            raise ValueError()
        raw = base64.b64decode(encoded, validate=True)
        with Image.open(BytesIO(raw)) as original:
            if original.format not in {"JPEG", "PNG", "WEBP"} or original.width * original.height > 4_000_000:
                raise ValueError()
            photo = ImageOps.fit(ImageOps.exif_transpose(original).convert("RGB"), (256, 256))
            output = BytesIO()
            photo.save(output, format="JPEG", quality=80, optimize=True)
        image = output.getvalue()
        if len(image) > 60_000:
            raise ValueError()
    except (ValueError, binascii.Error, OSError, UnidentifiedImageError, Image.DecompressionBombError):
        raise HTTPException(400, "Choose a valid JPG, PNG, or WebP photo.")
    user = db.query(User).filter(User.username == username).first()
    record = db.get(ProfilePhoto, user.id)
    if record:
        record.image = image
    else:
        db.add(ProfilePhoto(user_id=user.id, image=image))
    db.commit()
    return get_profile_photo(username, db)


@router.delete("/profile-photo", status_code=204)
def remove_profile_photo(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    db.query(ProfilePhoto).filter(ProfilePhoto.user_id == user.id).delete()
    db.commit()


@router.get("/sessions")
def my_sessions(username: str = Depends(get_current_user), token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    sessions = db.query(UserSession).filter(UserSession.user_id == user.id, UserSession.revoked_at.is_(None), UserSession.expires_at > datetime.utcnow()).order_by(UserSession.login_at.desc()).all()
    return [{"id": s.id, "user_agent": s.user_agent, "ip_address": s.ip_address, "login_at": s.login_at, "expires_at": s.expires_at, "current": s.jwt_token == token} for s in sessions]


@router.delete("/sessions/{session_id}", status_code=204)
def revoke_session(session_id: int, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    session = db.query(UserSession).filter(UserSession.id == session_id, UserSession.user_id == user.id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    session.revoked_at = datetime.utcnow()
    db.commit()


@router.post("/password", status_code=204)
def change_password(data: PasswordChange, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    throttle(db, "reauth:" + username)
    user = db.query(User).filter(User.username == username).first()
    if not check_password(data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(data.new_password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password must be at most 72 UTF-8 bytes")
    user.hashed_password = hash_password(data.new_password)
    db.query(OtpChallenge).filter(OtpChallenge.user_id == user.id, OtpChallenge.used_at.is_(None)).update({"used_at": datetime.utcnow()})
    db.query(UserSession).filter(UserSession.user_id == user.id, UserSession.revoked_at.is_(None)).update({"revoked_at": datetime.utcnow()})
    db.commit()


@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    identifier = form_data.username.strip()
    user = db.query(User).filter(User.username == identifier).first()
    if not user and '@' in identifier:
        user = db.query(User).filter(func.lower(User.email) == identifier.lower()).first()
    # Username and email attempts share the same account throttle.
    throttle(db, "password:" + (user.username if user else identifier).casefold())
    if not user or not check_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active")

    return begin_login(user, db)


def begin_login(user, db):
    credential = db.query(OtpCredential).filter(OtpCredential.user_id == user.id).with_for_update().first()
    if credential and credential.enabled:
        ensure_unlocked(credential)
        challenge = secrets.token_urlsafe(32)
        db.add(OtpChallenge(token_hash=digest(challenge), user_id=user.id, expires_at=datetime.utcnow() + timedelta(minutes=5)))
        db.commit()
        return {"otp_required": True, "challenge_token": challenge, "expires_in": 300}
    return begin_pin(user, db)


def begin_pin(user, db):
    challenge = secrets.token_urlsafe(32)
    db.add(PinChallenge(token_hash=digest(challenge), user_id=user.id,
                        password_digest=digest(user.hashed_password),
                        expires_at=datetime.utcnow() + timedelta(minutes=5)))
    setup = db.get(PinCredential, user.id) is None
    db.commit()
    return {"pin_required": True, "pin_setup_required": setup,
            "challenge_token": challenge, "expires_in": 300}


class PinInput(BaseModel):
    challenge_token: str = Field(min_length=20, max_length=100)
    pin: str = Field(pattern=r"^[0-9]{6}$", min_length=6, max_length=6)
    confirm_pin: str | None = Field(default=None, pattern=r"^[0-9]{6}$", min_length=6, max_length=6)


@router.post("/pin/verify")
def verify_pin(data: PinInput, request: Request, db: Session = Depends(get_db)):
    challenge = db.get(PinChallenge, digest(data.challenge_token))
    if not challenge:
        raise HTTPException(400, "Sign-in request expired. Enter your password again.")
    user_id = challenge.user_id
    throttle(db, "pin:" + str(user_id))
    # Serialize enrollment and verification across all challenges for this user.
    user = db.query(User).filter(User.id == user_id).populate_existing().with_for_update().first()
    challenge = db.query(PinChallenge).filter(PinChallenge.token_hash == digest(data.challenge_token)).populate_existing().with_for_update().first()
    if not user or not challenge or challenge.used_at or challenge.expires_at <= datetime.utcnow() or challenge.password_digest != digest(user.hashed_password):
        raise HTTPException(400, "Sign-in request expired. Enter your password again.")
    if user.account_status != "ACTIVE":
        raise HTTPException(403, "Account is not active")
    credential = db.get(PinCredential, user.id)
    if credential:
        if not check_password(data.pin, credential.hashed_pin):
            raise HTTPException(400, "Incorrect PIN. Please try again.")
    else:
        if data.confirm_pin != data.pin:
            raise HTTPException(400, "PINs must match. Enter your six-digit PIN twice.")
        db.add(PinCredential(user_id=user.id, hashed_pin=hash_password(data.pin)))
    challenge.used_at = datetime.utcnow()
    return issue_session(user, request, db)


def issue_session(user, request, db):
    token = create_token(user.username)
    expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Every successful login is recorded as a row in `sessions` (Layer 2 table).
    new_session = UserSession(
        user_id=user.id,
        jwt_token=token,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        expires_at=expires_at,
    )
    db.add(new_session)

    user.last_login_at = datetime.utcnow()

    db.commit()
    return Token(access_token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.jwt_token == token).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.revoked_at = datetime.utcnow()
    db.commit()
