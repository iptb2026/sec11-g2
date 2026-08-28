# ==== LAYER 5: Financial Records & Ledger ====
from sqlalchemy import Column, BigInteger, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func

from app.database.session import Base


class InterestRecord(Base):
    __tablename__ = "interest_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey("accounts.id"), nullable=False)
    policy_id = Column(BigInteger, ForeignKey("interest_policies.id"), nullable=False)
    amount_credited = Column(DECIMAL(18, 2), nullable=False)
    balance_before = Column(DECIMAL(18, 2), nullable=False)
    balance_after = Column(DECIMAL(18, 2), nullable=False)
    credited_at = Column(TIMESTAMP, server_default=func.now())