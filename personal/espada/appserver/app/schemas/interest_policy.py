from datetime import date
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel

class InterestPolicyCreate(BaseModel):
    account_type_id: int
    policy_name: str
    annual_rate: Decimal
    compounding_frequency: Literal["DAILY", "MONTHLY", "QUARTERLY", "YEARLY"] = "MONTHLY"
    effective_date: date
    expiration_date: Optional[date] = None

class InterestPolicyOut(BaseModel):
    id: int
    account_type_id: int
    policy_name: str
    annual_rate: Decimal
    compounding_frequency: str
    effective_date: date
    expiration_date: Optional[date] = None

    class Config:
        from_attributes = True
