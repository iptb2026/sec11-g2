# ==== LAYER 5: Financial Records & Ledger ====
from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func

from app.database.session import Base


class FeeRecord(Base):
    __tablename__ = "fee_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey("accounts.id"), nullable=False)
    fee_type_id = Column(BigInteger, ForeignKey("fee_types.id"), nullable=False)
    transaction_reference = Column(String(100), nullable=True)
    amount_charged = Column(DECIMAL(18, 2), nullable=False)
    charged_at = Column(TIMESTAMP, server_default=func.now())
    remarks = Column(Text, nullable=True)