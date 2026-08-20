# ==== LAYER 1: Foundation & Reference Data ====
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AccountTypeCreate(BaseModel):
    type_code: str
    type_name: str
    minimum_balance: Decimal = Decimal("0.00")
    opening_deposit: Decimal = Decimal("0.00")
    annual_interest_rate: Decimal = Decimal("0.00")
    daily_withdrawal_limit: Decimal = Decimal("0.00")


class AccountTypeOut(BaseModel):
    id: int
    type_code: str
    type_name: str
    minimum_balance: Decimal
    opening_deposit: Decimal
    annual_interest_rate: Decimal
    daily_withdrawal_limit: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

        