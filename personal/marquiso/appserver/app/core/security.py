

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

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


# def hash_password(password: str) -> str:
#     password_bytes = password.encode("utf-8")

#     if len(password_bytes) > 72:
#         raise ValueError("Password cannot be longer than 72 bytes")

#     return pwd_context.hash(password)


# def check_password(plain_password: str, hashed_password: str) -> bool:
#     if len(plain_password.encode("utf-8")) > 72:
#         return False

#     return pwd_context.verify(plain_password, hashed_password)


# --- JWT TOKEN FUNCTIONS ---

def create_token(username: str) -> str:
    """Create a JWT token for a logged-in user. No expiry."""
    data = {"sub": username}
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
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
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    