# ==== LAYER 3: Account Configuration ====
from sqlalchemy import Column, BigInteger, DECIMAL, Date, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func

from app.database.session import Base


class WithdrawalLimit(Base):
    __tablename__ = "withdrawal_limits"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey("accounts.id"), unique=True, nullable=False)
    daily_limit_amount = Column(DECIMAL(18, 2), nullable=False)
    daily_used_amount = Column(DECIMAL(18, 2), default=0.00)
    last_reset_date = Column(Date, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
