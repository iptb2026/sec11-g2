# ==== LAYER 1: Foundation & Reference Data ====
from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, EmailStr


class BankCreate(BaseModel):
    bank_code: str
    swift_code: Optional[str] = None
    bank_name: str
    short_name: Optional[str] = None
    api_endpoint: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    status: Literal["ACTIVE", "INACTIVE"] = "ACTIVE"


class BankOut(BaseModel):
    id: int
    bank_code: str
    swift_code: Optional[str] = None
    bank_name: str
    short_name: Optional[str] = None
    api_endpoint: Optional[str] = None
    contact_email: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True



        