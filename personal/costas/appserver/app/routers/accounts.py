from datetime import datetime
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.core.db_utils import commit_or_409
from app.database.session import get_db
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.user import User
from app.schemas.account import AccountCreate,AccountUpdate,AccountOut
router=APIRouter(prefix='/accounts',tags=['Layer 3 - Accounts'])
def refs(db,customer_id,account_type_id):
    if not db.query(User).filter(User.id==customer_id).first(): raise HTTPException(400,'customer_id does not exist')
    typ=db.query(AccountType).filter(AccountType.id==account_type_id).first()
    if not typ: raise HTTPException(400,'account_type_id does not exist')
    return typ
@router.post('/',response_model=AccountOut,status_code=201)
def create(data:AccountCreate,db:Session=Depends(get_db)):
    typ=refs(db,data.customer_id,data.account_type_id)
    if db.query(Account).filter(Account.account_number==data.account_number).first(): raise HTTPException(400,'account_number already exists')
    obj=Account(**data.model_dump(),available_balance=typ.opening_deposit,ledger_balance=typ.opening_deposit); db.add(obj); db.commit(); db.refresh(obj); return obj
@router.get('/',response_model=list[AccountOut])
def listing(db:Session=Depends(get_db)): return db.query(Account).all()
@router.get('/{account_id}',response_model=AccountOut)
def get(account_id:int,db:Session=Depends(get_db)):
    obj=db.query(Account).filter(Account.id==account_id).first()
    if not obj: raise HTTPException(404,'Account not found')
    return obj
@router.put('/{account_id}',response_model=AccountOut)
def update(account_id:int,data:AccountUpdate,db:Session=Depends(get_db)):
    obj=db.query(Account).filter(Account.id==account_id).first()
    if not obj: raise HTTPException(404,'Account not found')
    refs(db,data.customer_id,data.account_type_id)
    if data.status=='CLOSED' and obj.status!='CLOSED': obj.closed_at=datetime.utcnow()
    for field,value in data.model_dump().items(): setattr(obj,field,value)
    db.commit(); db.refresh(obj); return obj
@router.delete('/{account_id}',status_code=204)
def delete(account_id:int,db:Session=Depends(get_db)):
    obj=db.query(Account).filter(Account.id==account_id).first()
    if not obj: raise HTTPException(404,'Account not found')
    db.delete(obj); commit_or_409(db,'Cannot delete this account — related transactions or records still reference it')
