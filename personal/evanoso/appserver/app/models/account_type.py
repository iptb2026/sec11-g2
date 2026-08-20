# ==== LAYER 1: Foundation & Reference Data ====
from sqlalchemy import Column, BigInteger, String, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func

from app.database.session import Base


class AccountType(Base):
    __tablename__ = "account_types"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type_code = Column(String(50), unique=True, nullable=False)
    type_name = Column(String(100), nullable=False)
    minimum_balance = Column(DECIMAL(18, 2), default=0.00)
    opening_deposit = Column(DECIMAL(18, 2), default=0.00)
    annual_interest_rate = Column(DECIMAL(5, 2), default=0.00)
    daily_withdrawal_limit = Column(DECIMAL(18, 2), default=0.00)
    created_at = Column(TIMESTAMP, server_default=func.now())