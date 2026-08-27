# ==== LAYER 2: Identity & Access ====
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserMeOut(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    role_id: int
    role_code: str
    role_name: str
    account_status: str

    class Config:
        from_attributes = True