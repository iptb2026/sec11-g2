
import base64
import hashlib
import hmac
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt


from app.core.config import settings

PASSWORD_ITERATIONS = 600_000

# Tells FastAPI where users log in to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# --- PASSWORD FUNCTIONS ---

def hash_password(password: str) -> str:
    """Hash new passwords without bcrypt's 72-byte limit or passlib dependency."""
    if not password:
        raise ValueError("Password cannot be empty")

    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return "pbkdf2_sha256${}${}${}".format(
        PASSWORD_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def check_password(plain_password: str, hashed_password: str) -> bool:
    """Verify new PBKDF2 hashes and legacy bcrypt hashes."""
    if hashed_password.startswith("pbkdf2_sha256$"):
        try:
            _, iterations, encoded_salt, encoded_digest = hashed_password.split("$", 3)
            salt = base64.urlsafe_b64decode(encoded_salt.encode("ascii"))
            expected = base64.urlsafe_b64decode(encoded_digest.encode("ascii"))
            actual = hashlib.pbkdf2_hmac(
                "sha256", plain_password.encode("utf-8"), salt, int(iterations)
            )
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False

    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            import bcrypt
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("ascii"))
        except (ValueError, TypeError):
            return False

    return False


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


def get_current_user_record(token: str = Depends(oauth2_scheme)):
    """Resolve the bearer token to an active database user."""
    from app.database.session import SessionLocal
    from app.models.user import User

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        username = None

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user or user.account_status != "ACTIVE":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or inactive account")
        return user
    finally:
        db.close()


def require_roles(*allowed_roles):
    """Create a dependency that permits only the supplied role codes."""
    def dependency(current_user=Depends(get_current_user_record)):
        from app.database.session import SessionLocal
        from app.models.role import Role

        db = SessionLocal()
        try:
            role = db.query(Role).filter(Role.id == current_user.role_id).first()
            if not role or role.role_code not in allowed_roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            return current_user
        finally:
            db.close()

    return dependency

    