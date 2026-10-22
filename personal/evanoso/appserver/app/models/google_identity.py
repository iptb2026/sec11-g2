from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey
from app.database.session import Base

class GoogleIdentity(Base):
    __tablename__ = 'google_identities'
    subject = Column(String(255), primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False, unique=True)

class GoogleChallenge(Base):
    __tablename__ = 'google_challenges'
    token_hash = Column(String(64), primary_key=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
