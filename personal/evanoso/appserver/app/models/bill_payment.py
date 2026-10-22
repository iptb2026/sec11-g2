from sqlalchemy import Column, BigInteger, String, DECIMAL, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func

from app.database.session import Base


class BillPayment(Base):
    __tablename__ = "bill_payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey("accounts.id"), nullable=False)
    biller_name = Column(String(100), nullable=False)
    biller_reference = Column(String(100), nullable=False)
    payment_reference = Column(String(100), unique=True, nullable=False)
    amount = Column(DECIMAL(18, 2), nullable=False)
    status = Column(Enum("COMPLETED"), nullable=False, default="COMPLETED")
    created_at = Column(TIMESTAMP, server_default=func.now())