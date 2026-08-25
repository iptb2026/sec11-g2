# ==== LAYER 4: Transactions ====
from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal

from pydantic import BaseModel


class TransferCreate(BaseModel):
    source_account_id: int
    destination_account_id: int
    transfer_reference: str
    amount: Decimal
    transfer_type: Literal["INTERNAL", "SCHEDULED"] = "INTERNAL"
    remarks: Optional[str] = None


class TransferOut(BaseModel):
    id: int
    source_account_id: int
    destination_account_id: int
    transfer_reference: str
    amount: Decimal
    transfer_type: str
    remarks: Optional[str] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
