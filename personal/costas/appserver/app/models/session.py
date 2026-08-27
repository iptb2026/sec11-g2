from sqlalchemy import Column, BigInteger, String, Text, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database.session import Base

class UserSession(Base):
    __tablename__ = 'sessions'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    jwt_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    login_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
