from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from app.database.session import Base


class PinCredential(Base):
    __tablename__ = "pin_credentials"
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    hashed_pin = Column(String(255), nullable=False)


class PinChallenge(Base):
    __tablename__ = "pin_challenges"
    token_hash = Column(String(64), primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    password_digest = Column(String(64), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
