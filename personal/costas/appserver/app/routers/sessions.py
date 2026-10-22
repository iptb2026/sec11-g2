from datetime import datetime
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.core.db_utils import commit_or_409
from app.database.session import get_db
from app.models.session import UserSession
from app.models.user import User
from app.schemas.session import SessionCreate,SessionOut
router=APIRouter(prefix='/sessions',tags=['Layer 2 - Sessions'])
@router.post('/',response_model=SessionOut,status_code=201)
def create(data:SessionCreate,db:Session=Depends(get_db)):
    if not db.query(User).filter(User.id==data.user_id).first(): raise HTTPException(400,'user_id does not exist')
    obj=UserSession(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj
@router.get('/',response_model=list[SessionOut])
def listing(db:Session=Depends(get_db)): return db.query(UserSession).all()
@router.get('/{session_id}',response_model=SessionOut)
def get(session_id:int,db:Session=Depends(get_db)):
    obj=db.query(UserSession).filter(UserSession.id==session_id).first()
    if not obj: raise HTTPException(404,'Session not found')
    return obj
@router.put('/{session_id}/revoke',response_model=SessionOut)
def revoke(session_id:int,db:Session=Depends(get_db)):
    obj=db.query(UserSession).filter(UserSession.id==session_id).first()
    if not obj: raise HTTPException(404,'Session not found')
    obj.revoked_at=datetime.utcnow(); db.commit(); db.refresh(obj); return obj
@router.delete('/{session_id}',status_code=204)
def delete(session_id:int,db:Session=Depends(get_db)):
    obj=db.query(UserSession).filter(UserSession.id==session_id).first()
    if not obj: raise HTTPException(404,'Session not found')
    db.delete(obj); commit_or_409(db,'Cannot delete this session — it is still referenced elsewhere')
