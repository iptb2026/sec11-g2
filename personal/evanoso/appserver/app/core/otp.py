import hashlib
import hmac
import os
import secrets
import time
import fcntl
from datetime import datetime, timedelta
from pathlib import Path

import pyotp
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.models.otp import LoginThrottle


def secret_cipher():
    key = os.environ.get("BEMBANK_OTP_ENCRYPTION_KEY")
    if not key:
        path = Path(os.environ.get("BEMBANK_OTP_KEY_FILE", str(Path(__file__).resolve().parents[2] / ".bembank-otp.key")))
        # Serialize initialization so concurrent workers never read a partial key.
        with open(path, "a+b", opener=lambda name, flags: os.open(name, flags, 0o600)) as file:
            fcntl.flock(file, fcntl.LOCK_EX)
            file.seek(0)
            key = file.read().strip()
            if not key:
                key = Fernet.generate_key()
                file.write(key)
                file.flush()
                os.fsync(file.fileno())
    return Fernet(key)


def decrypt_secret(value):
    try:
        return secret_cipher().decrypt(value.encode()).decode()
    except (InvalidToken, ValueError, OSError):
        raise HTTPException(503, "Authenticator verification is temporarily unavailable. Please try again later.")


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def throttle(db, key):
    """Persistent password-attempt limit, including unknown accounts."""
    now = datetime.utcnow()
    key = digest(key)
    row = db.query(LoginThrottle).filter(LoginThrottle.key == key).with_for_update().first()
    if not row:
        try:
            with db.begin_nested():
                db.add(LoginThrottle(key=key, attempts=0, window_start=now))
                db.flush()
        except IntegrityError:
            pass
        row = db.query(LoginThrottle).filter(LoginThrottle.key == key).with_for_update().first()
    if now - row.window_start >= timedelta(minutes=15):
        row.attempts = 0
        row.window_start = now
    if row.attempts >= 10:
        raise HTTPException(429, "Too many attempts. Please wait 15 minutes before trying again.")
    row.attempts += 1
    db.commit()


def ensure_unlocked(credential):
    if credential.locked_until and credential.locked_until > datetime.utcnow():
        raise HTTPException(429, "Too many incorrect codes. Please wait 15 minutes before trying again.")
    if credential.locked_until:
        credential.locked_until = None
        credential.failed_attempts = 0


def verify_code(db, credential, code, allow_recovery=True):
    ensure_unlocked(credential)
    code = code.strip().replace(" ", "").replace("-", "").upper()
    counter = int(time.time()) // 30
    if len(code) == 6 and code.isascii() and code.isdigit():
        totp = pyotp.TOTP(decrypt_secret(credential.encrypted_secret))
        for offset in (-1, 0, 1):
            candidate = counter + offset
            if candidate > credential.last_counter and hmac.compare_digest(totp.at(candidate * 30), code):
                credential.last_counter = candidate
                credential.failed_attempts = 0
                return
    elif allow_recovery:
        hashed = digest(code)
        for stored in credential.recovery_hashes or []:
            if hmac.compare_digest(hashed, stored):
                credential.recovery_hashes = [item for item in credential.recovery_hashes if item != stored]
                credential.failed_attempts = 0
                return
    credential.failed_attempts += 1
    if credential.failed_attempts >= 5:
        credential.locked_until = datetime.utcnow() + timedelta(minutes=15)
    db.commit()  # Persist failed attempts even though the request returns an error.
    raise HTTPException(400, "The code is incorrect, expired, or already used. Try the next code from your authenticator.")


def recovery_codes():
    values = [secrets.token_hex(8).upper() for _ in range(8)]
    return ["-".join(value[i:i + 4] for i in range(0, 16, 4)) for value in values], [digest(value) for value in values]
