from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogCreate,AuditLogOut
router=APIRouter(prefix='/audit-logs',tags=['Layer 2 - Audit Logs'])
@router.post('/',response_model=AuditLogOut,status_code=201)
def create(data:AuditLogCreate,db:Session=Depends(get_db)):
    if data.user_id is not None and not db.query(User).filter(User.id==data.user_id).first(): raise HTTPException(400,'user_id does not exist')
    obj=AuditLog(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj
@router.get('/',response_model=list[AuditLogOut])
def listing(db:Session=Depends(get_db)): return db.query(AuditLog).all()
@router.get('/{log_id}',response_model=AuditLogOut)
def get(log_id:int,db:Session=Depends(get_db)):
    obj=db.query(AuditLog).filter(AuditLog.id==log_id).first()
    if not obj: raise HTTPException(404,'Audit log not found')
    return obj
@router.delete('/{log_id}',status_code=204)
def delete(log_id:int,db:Session=Depends(get_db)):
    obj=db.query(AuditLog).filter(AuditLog.id==log_id).first()
    if not obj: raise HTTPException(404,'Audit log not found')
    db.delete(obj); db.commit()
