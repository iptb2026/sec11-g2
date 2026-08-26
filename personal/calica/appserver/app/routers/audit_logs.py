# ==== LAYER 2: Identity & Access ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.database.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogCreate, AuditLogOut

router = APIRouter(
    prefix="/audit-logs",
    tags=["Layer 2 - Audit Logs"],
    dependencies=[Depends(require_roles("ADMIN"))]
)

@router.post("/", response_model=AuditLogOut, status_code=status.HTTP_201_CREATED)
def create_audit_log(log: AuditLogCreate, db: Session = Depends(get_db)):
    if log.user_id is not None:
        user = db.query(User).filter(User.id == log.user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="user_id does not exist")

    new_log = AuditLog(**log.model_dump())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.get("/", response_model=list[AuditLogOut])
def list_audit_logs(db: Session = Depends(get_db)):
    return db.query(AuditLog).all()


@router.get("/{log_id}", response_model=AuditLogOut)
def get_audit_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_audit_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")

    db.delete(log)
    db.commit()