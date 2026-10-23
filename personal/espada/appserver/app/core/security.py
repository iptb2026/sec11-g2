

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.models.session import UserSession
from app.models.role import Role
from app.models.user import User

# Tool for hashing passwords
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

# Tells FastAPI where users log in to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# --- PASSWORD FUNCTIONS ---

def hash_password(password: str) -> str:
    """Turn a plain password into a hash before saving to the database."""
    return pwd_context.hash(password)


def check_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plain password with the stored hash. Returns True or False."""
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT TOKEN FUNCTIONS ---

def create_token(username: str) -> str:
    """Create a short-lived JWT token for a logged-in user."""
    data = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    session = db.query(UserSession).filter(
        UserSession.jwt_token == token,
        UserSession.revoked_at.is_(None),
        UserSession.expires_at > datetime.utcnow(),
    ).first()
    user = db.query(User).filter(User.username == username).first() if username else None
    if not session or not user or user.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user


def get_current_admin(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role or role.role_code != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return user
