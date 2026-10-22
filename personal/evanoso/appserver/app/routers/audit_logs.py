# ==== LAYER 2: Identity & Access ====
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogOut

router = APIRouter(prefix="/audit-logs", tags=["Layer 2 - Audit Logs"])


@router.get("/", response_model=list[AuditLogOut])
def list_audit_logs(db: Session = Depends(get_db)):
    return db.query(AuditLog).all()


@router.get("/{log_id}", response_model=AuditLogOut)
def get_audit_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log
