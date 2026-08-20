from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel

class AccountCreate(BaseModel):
    account_number: str
    customer_id: int
    account_type_id: int
    currency_code: str = "PHP"
    branch_code: Optional[str] = None

class AccountUpdate(BaseModel):
    account_number: str
    customer_id: int
    account_type_id: int
    currency_code: str = "PHP"
    branch_code: Optional[str] = None
    status: Literal["ACTIVE", "FROZEN", "CLOSED"] = "ACTIVE"

class AccountOut(BaseModel):
    id: int
    account_number: str
    customer_id: int
    account_type_id: int
    available_balance: Decimal
    ledger_balance: Decimal
    currency_code: str
    status: str
    opened_at: datetime
    closed_at: Optional[datetime] = None
    branch_code: Optional[str] = None

    class Config:
        from_attributes = True
