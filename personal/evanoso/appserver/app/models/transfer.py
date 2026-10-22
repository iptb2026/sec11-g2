# ==== LAYER 4: Transactions ====
from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, Enum, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func

from app.database.session import Base


class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_account_id = Column(BigInteger, ForeignKey("accounts.id"), nullable=False)
    destination_account_id = Column(BigInteger, ForeignKey("accounts.id"), nullable=False)
    transfer_reference = Column(String(100), unique=True, nullable=False)
    amount = Column(DECIMAL(18, 2), nullable=False)
    transfer_type = Column(Enum("INTERNAL", "SCHEDULED"), default="INTERNAL")
    remarks = Column(Text, nullable=True)
    status = Column(Enum("PENDING", "SUCCESS", "FAILED", "REVERSED"), default="PENDING")
    created_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)