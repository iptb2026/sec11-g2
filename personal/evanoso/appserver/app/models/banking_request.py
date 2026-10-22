from sqlalchemy import Column, Integer, BigInteger, String, DECIMAL, ForeignKey, DateTime
from datetime import datetime
from app.database.session import Base


class BankingRequest(Base):
    __tablename__ = "banking_requests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    account_id = Column(BigInteger, ForeignKey("accounts.id"), nullable=False)
    kind = Column(String(12), nullable=False)
    amount = Column(DECIMAL(18, 2), nullable=False)
    reference = Column(String(40), nullable=False, unique=True)
    status = Column(String(16), nullable=False, default="PENDING")
    note = Column(String(250), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    reviewed_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)


class Recipient(Base):
    __tablename__ = "saved_recipients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(80), nullable=False)
    account_number = Column(String(100), nullable=False)
