# ==== LAYER 1: Foundation & Reference Data ====
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RoleCreate(BaseModel):
    role_code: str
    role_name: str
    description: Optional[str] = None


class RoleOut(BaseModel):
    id: int
    role_code: str
    role_name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True