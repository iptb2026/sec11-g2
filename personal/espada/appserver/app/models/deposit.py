from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, Enum, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database.session import Base

class Deposit(Base):
    __tablename__ = "deposits"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey("accounts.id"), nullable=False)
    reference_number = Column(String(100), unique=True, nullable=False)
    amount = Column(DECIMAL(18, 2), nullable=False)
    deposit_channel = Column(Enum("CASH", "ATM", "ONLINE", "INTERBANK"), nullable=False)
    deposited_by_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    remarks = Column(Text, nullable=True)
    transaction_date = Column(DateTime, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
