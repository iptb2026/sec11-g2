# ==== LAYER 3: Account Configuration ====
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class WithdrawalLimitCreate(BaseModel):
    account_id: int
    daily_limit_amount: Decimal
    last_reset_date: date
    # daily_used_amount is NOT accepted here — it starts at 0 and is only ever
    # incremented internally by the withdrawal endpoint (Layer 4).


class WithdrawalLimitUpdate(BaseModel):
    daily_limit_amount: Decimal
    last_reset_date: date


class WithdrawalLimitOut(BaseModel):
    id: int
    account_id: int
    daily_limit_amount: Decimal
    daily_used_amount: Decimal
    last_reset_date: date
    updated_at: datetime

    class Config:
        from_attributes = True