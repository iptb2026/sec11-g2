# ==== LAYER 5: Financial Records & Ledger ====
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class InterestRecordCreate(BaseModel):
    account_id: int
    policy_id: int
    amount_credited: Decimal
    # balance_before / balance_after are NOT accepted here — they're a
    # server-computed snapshot of the account's balance right before and
    # right after this credit is applied.


class InterestRecordOut(BaseModel):
    id: int
    account_id: int
    policy_id: int
    amount_credited: Decimal
    balance_before: Decimal
    balance_after: Decimal
    credited_at: datetime

    class Config:
        from_attributes = True