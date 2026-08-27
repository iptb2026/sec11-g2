# ==== LAYER 4: Transactions ====
from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal

from pydantic import BaseModel, Field


class DepositCreate(BaseModel):
    account_id: int
    reference_number: str
    amount: Decimal
    deposit_channel: Literal["CASH", "ATM", "ONLINE", "INTERBANK"]
    deposited_by_user_id: Optional[int] = None
    remarks: Optional[str] = None
    transaction_date: datetime = Field(default_factory=datetime.utcnow)


class DepositOut(BaseModel):
    id: int
    account_id: int
    reference_number: str
    amount: Decimal
    deposit_channel: str
    deposited_by_user_id: Optional[int] = None
    remarks: Optional[str] = None
    transaction_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True
