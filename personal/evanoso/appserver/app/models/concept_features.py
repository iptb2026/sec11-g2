from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DECIMAL, DateTime, ForeignKey
from app.database.session import Base

class MobileLoad(Base):
    __tablename__ = 'mobile_loads'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey('accounts.id'), nullable=False)
    customer_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    network = Column(String(20), nullable=False)
    mobile_number = Column(String(11), nullable=False)
    amount = Column(DECIMAL(18,2), nullable=False)
    reference = Column(String(40), unique=True, nullable=False)
    request_key = Column(String(40), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class SupportTicket(Base):
    __tablename__ = 'support_tickets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    subject = Column(String(100), nullable=False)
    message = Column(String(2000), nullable=False)
    status = Column(String(12), default='OPEN', nullable=False)
    reply = Column(String(2000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
