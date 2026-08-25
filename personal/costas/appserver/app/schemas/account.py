# ==== LAYER 3: Account Configuration ====
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
    # NOTE: available_balance / ledger_balance are deliberately NOT accepted here.
    # A new account's starting balance is the account_type's opening_deposit,
    # computed by the server — never trust a client to set its own money fields.


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