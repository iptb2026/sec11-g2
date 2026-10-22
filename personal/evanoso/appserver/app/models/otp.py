from sqlalchemy import Column, BigInteger, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from app.database.session import Base


class OtpCredential(Base):
    __tablename__ = "otp_credentials"
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    encrypted_secret = Column(Text, nullable=True)
    enabled = Column(Boolean, nullable=False, default=False)
    setup_expires_at = Column(DateTime, nullable=True)
    last_counter = Column(BigInteger, nullable=False, default=-1)
    recovery_hashes = Column(JSON, nullable=False, default=list)
    failed_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime, nullable=True)


class OtpChallenge(Base):
    __tablename__ = "otp_challenges"
    token_hash = Column(String(64), primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)


class LoginThrottle(Base):
    __tablename__ = "login_throttles"
    key = Column(String(64), primary_key=True)
    attempts = Column(Integer, nullable=False, default=0)
    window_start = Column(DateTime, nullable=False)
