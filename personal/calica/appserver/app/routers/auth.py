# ==== LAYER 2: Identity & Access ====
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import check_password, create_token, oauth2_scheme
from app.database.session import get_db
from app.models.session import UserSession
from app.models.user import User
from app.schemas.auth import Token

router = APIRouter(prefix="/auth", tags=["Layer 2 - Auth"])


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not check_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active")

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