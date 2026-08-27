from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.account import Account
from app.models.withdrawal_limit import WithdrawalLimit
from app.schemas.withdrawal_limit import WithdrawalLimitCreate,WithdrawalLimitUpdate,WithdrawalLimitOut
router=APIRouter(prefix='/withdrawal-limits',tags=['Layer 3 - Withdrawal Limits'])
@router.post('/',response_model=WithdrawalLimitOut,status_code=201)
def create(data:WithdrawalLimitCreate,db:Session=Depends(get_db)):
    if not db.query(Account).filter(Account.id==data.account_id).first(): raise HTTPException(400,'account_id does not exist')
    if db.query(WithdrawalLimit).filter(WithdrawalLimit.account_id==data.account_id).first(): raise HTTPException(400,'This account already has a withdrawal limit')
    obj=WithdrawalLimit(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj
@router.get('/',response_model=list[WithdrawalLimitOut])
def listing(db:Session=Depends(get_db)): return db.query(WithdrawalLimit).all()
@router.get('/{limit_id}',response_model=WithdrawalLimitOut)
def get(limit_id:int,db:Session=Depends(get_db)):
    obj=db.query(WithdrawalLimit).filter(WithdrawalLimit.id==limit_id).first()
    if not obj: raise HTTPException(404,'Withdrawal limit not found')
    return obj
@router.put('/{limit_id}',response_model=WithdrawalLimitOut)
def update(limit_id:int,data:WithdrawalLimitUpdate,db:Session=Depends(get_db)):
    obj=db.query(WithdrawalLimit).filter(WithdrawalLimit.id==limit_id).first()
    if not obj: raise HTTPException(404,'Withdrawal limit not found')
    obj.daily_limit_amount=data.daily_limit_amount; obj.last_reset_date=data.last_reset_date; db.commit(); db.refresh(obj); return obj
@router.delete('/{limit_id}',status_code=204)
def delete(limit_id:int,db:Session=Depends(get_db)):
    obj=db.query(WithdrawalLimit).filter(WithdrawalLimit.id==limit_id).first()
    if not obj: raise HTTPException(404,'Withdrawal limit not found')
    db.delete(obj); db.commit()
