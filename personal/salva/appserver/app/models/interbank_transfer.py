# ==== LAYER 4: Transactions ====
from sqlalchemy import Column, BigInteger, String, DECIMAL, Enum, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func

from app.database.session import Base


class InterbankTransfer(Base):
    __tablename__ = "interbank_transfers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_account_id = Column(BigInteger, ForeignKey("accounts.id"), nullable=False)
    target_bank_id = Column(BigInteger, ForeignKey("banks.id"), nullable=False)
    target_account_number = Column(String(50), nullable=False)
    beneficiary_name = Column(String(150), nullable=True)
    reference_number = Column(String(100), unique=True, nullable=False)
    amount = Column(DECIMAL(18, 2), nullable=False)
    transfer_fee = Column(DECIMAL(18, 2), default=0.00)
    status = Column(Enum("PENDING", "VERIFIED", "PROCESSING", "SUCCESS", "FAILED", "REVERSED"), default="PENDING")
    initiated_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)