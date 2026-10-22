# ==== LAYER 4: Transactions ====
from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal

from pydantic import BaseModel, Field


class InterbankTransferCreate(BaseModel):
    source_account_id: int
    target_bank_id: int
    target_account_number: str
    beneficiary_name: Optional[str] = None
    reference_number: str
    amount: Decimal = Field(gt=0)
    transfer_fee: Decimal = Field(default=Decimal("0.00"), ge=0)


class InterbankTransferStatusUpdate(BaseModel):
    status: Literal["PENDING", "VERIFIED", "PROCESSING", "SUCCESS", "FAILED", "REVERSED"]


class InterbankTransferOut(BaseModel):
    id: int
    source_account_id: int
    target_bank_id: int
    target_account_number: str
    beneficiary_name: Optional[str] = None
    reference_number: str
    amount: Decimal
    transfer_fee: Decimal
    status: str
    initiated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True