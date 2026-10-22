

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy.orm import Session
from app.database.session import get_db

from app.core.config import settings

# Tells FastAPI where users log in to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# --- PASSWORD FUNCTIONS ---

def hash_password(password: str) -> str:
    """Turn a plain password into a hash before saving to the database."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plain password with the stored hash. Returns True or False."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


# --- JWT TOKEN FUNCTIONS ---

def create_token(username: str) -> str:
    """Create a unique, time-limited session token."""
    data = {"sub": username, "jti": uuid4().hex, "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)}
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> str:
    """
    Used inside protected routes.
    FastAPI automatically grabs the token from the request header
    and passes it here. If valid, returns the username.
    If invalid or expired, stops the request with a 401 error.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        from app.models.session import UserSession
        from app.models.user import User
        session = db.query(UserSession).filter(UserSession.jwt_token == token, UserSession.revoked_at.is_(None), UserSession.expires_at > datetime.utcnow()).first()
        user = db.query(User).filter(User.username == username, User.account_status == "ACTIVE").first()
        if not session or not user or session.user_id != user.id:
            raise HTTPException(status_code=401, detail="Session expired or revoked")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def require_roles(*allowed):
    def authorize(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
        from app.models.user import User
        from app.models.role import Role
        user = db.query(User).filter(User.username == username).first()
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if not role or role.role_code not in allowed:
            raise HTTPException(status_code=403, detail="Access denied for this role")
        return user
    return authorize


def reference_access(request: Request, username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Staff can read reference lists; only administrators may change them."""
    allowed = ("ADMIN", "STAFF") if request.method in ("GET", "HEAD") else ("ADMIN",)
    return require_roles(*allowed)(username, db)


