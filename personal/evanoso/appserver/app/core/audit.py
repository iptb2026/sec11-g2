from typing import Any

from fastapi import Request
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.audit_log import AuditLog
from app.models.user import User


def record_audit_event(
    db: Session,
    request: Request,
    action_type: str,
    entity_name: str,
    entity_id: int,
    new_value: dict[str, Any] | None = None,
    old_value: dict[str, Any] | None = None,
) -> None:
    user_id = None
    authorization = request.headers.get("authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() == "bearer" and token:
        try:
            username = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]).get("sub")
        except JWTError:
            username = None
        if username:
            user_id = db.query(User.id).filter(User.username == username).scalar()

    db.add(
        AuditLog(
            user_id=user_id,
            action_type=action_type,
            entity_name=entity_name,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    )