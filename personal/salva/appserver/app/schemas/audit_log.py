# ==== LAYER 2: Identity & Access ====
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class AuditLogCreate(BaseModel):
    user_id: Optional[int] = None
    action_type: str
    entity_name: str
    entity_id: Optional[int] = None
    old_value: Optional[dict[str, Any]] = None
    new_value: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    action_type: str
    entity_name: str
    entity_id: Optional[int] = None
    old_value: Optional[dict[str, Any]] = None
    new_value: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    action_timestamp: datetime

    class Config:
        from_attributes = True