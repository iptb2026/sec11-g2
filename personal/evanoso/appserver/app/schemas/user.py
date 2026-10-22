from app.core.password_policy import StrongPassword
# ==== LAYER 2: Identity & Access ====
from datetime import date, datetime
from typing import Optional, Literal

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    password: StrongPassword
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: Optional[date] = None
    role_id: int
    account_status: Literal["ACTIVE", "LOCKED", "DISABLED"] = "ACTIVE"


class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: Optional[date] = None
    role_id: int
    account_status: str
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True