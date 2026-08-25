# ==== LAYER 5: Financial Records & Ledger ====
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class InterestRecordCreate(BaseModel):
    account_id: int
    policy_id: int
    amount_credited: Decimal
    # balance_before / balance_after are NOT accepted here.
    # They are computed server-side from the account balance.


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
