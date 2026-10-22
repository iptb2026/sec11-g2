from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


class CustomerTransferCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    source_account_id: int
    destination_account_number: str = Field(min_length=1, max_length=30)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    remarks: Optional[str] = Field(default=None, max_length=500)


class BillPaymentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    account_id: int
    biller_name: str = Field(min_length=2, max_length=100)
    biller_reference: str = Field(min_length=2, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)


class InvestmentCreate(BaseModel):
    account_id: int
    plan_code: Literal["SHORT_TERM", "MEDIUM_TERM", "LONG_TERM"]
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)


class BillPaymentOut(BaseModel):
    id: int
    account_id: int
    biller_name: str
    biller_reference: str
    payment_reference: str
    amount: Decimal
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class InvestmentOut(BaseModel):
    id: int
    account_id: int
    plan_code: str
    term_months: int
    amount: Decimal
    status: str
    created_at: datetime
    redeemed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerTransactionOut(BaseModel):
    id: str
    account_number: str
    transaction_type: str
    reference: str
    amount: Decimal
    direction: Literal["CREDIT", "DEBIT"]
    status: str
    transaction_date: datetime
