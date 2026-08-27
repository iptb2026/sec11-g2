

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db

# Tool for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

def create_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token for a logged-in user with expiration."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    data = {"sub": username, "exp": expire}
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> str:
    """
    Used inside protected routes.
    FastAPI automatically grabs the token from the request header
    and passes it here. If valid, returns the username.
    If invalid or expired, stops the request with a 401 error.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception

    # Check if session has been revoked in database
    from app.models.session import UserSession
    session = (
        db.query(UserSession)
        .filter(UserSession.jwt_token == token)
        .order_by(UserSession.id.desc())
        .first()
    )
    if session and session.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return username


def get_current_user_model(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Returns the authenticated User ORM model with their role information.
    """
    username = get_current_user(token=token, db=db)
    from app.models.user import User
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active")
    return user


def require_roles(*allowed_roles: str):
    """
    Dependency factory to enforce role-based access control.
    Example: Depends(require_roles("ADMIN")) or Depends(require_roles("ADMIN", "STAFF"))
    """
    def role_checker(
        current_user = Depends(get_current_user_model),
        db: Session = Depends(get_db),
    ):
        from app.models.role import Role
        user_role = db.query(Role).filter(Role.id == current_user.role_id).first()
        if not user_role or user_role.role_code not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: required role in {list(allowed_roles)}",
            )
        return current_user

    return role_checker


    