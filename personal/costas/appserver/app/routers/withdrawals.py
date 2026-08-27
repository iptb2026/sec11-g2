from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.account import Account
from app.models.user import User
from app.models.withdrawal import Withdrawal
from app.models.withdrawal_limit import WithdrawalLimit
from app.schemas.withdrawal import WithdrawalCreate,WithdrawalOut
router=APIRouter(prefix='/withdrawals',tags=['Layer 4 - Withdrawals'])
@router.post('/',response_model=WithdrawalOut,status_code=201)
def create(data:WithdrawalCreate,db:Session=Depends(get_db)):
    account=db.query(Account).filter(Account.id==data.account_id).with_for_update().first()
    if not account: raise HTTPException(400,'account_id does not exist')
    if data.approved_by_user_id is not None and not db.query(User).filter(User.id==data.approved_by_user_id).first(): raise HTTPException(400,'approved_by_user_id does not exist')
    if db.query(Withdrawal).filter(Withdrawal.reference_number==data.reference_number).first(): raise HTTPException(400,'reference_number already exists')
    if account.status!='ACTIVE': raise HTTPException(400,f'Account is {account.status}, cannot withdraw')
    if account.available_balance<data.amount: raise HTTPException(400,'Insufficient balance')
    limit=db.query(WithdrawalLimit).filter(WithdrawalLimit.account_id==account.id).with_for_update().first()
    if limit and limit.daily_used_amount+data.amount>limit.daily_limit_amount: raise HTTPException(400,'This withdrawal would exceed the daily withdrawal limit')
    obj=Withdrawal(**data.model_dump()); db.add(obj); account.available_balance-=data.amount; account.ledger_balance-=data.amount
    if limit: limit.daily_used_amount+=data.amount
    db.commit(); db.refresh(obj); return obj
@router.get('/',response_model=list[WithdrawalOut])
def listing(db:Session=Depends(get_db)): return db.query(Withdrawal).all()
@router.get('/{item_id}',response_model=WithdrawalOut)
def get(item_id:int,db:Session=Depends(get_db)):
    obj=db.query(Withdrawal).filter(Withdrawal.id==item_id).first()
    if not obj: raise HTTPException(404,'Withdrawal not found')
    return obj
@router.put('/{item_id}',response_model=WithdrawalOut)
def update(item_id:int,data:WithdrawalCreate,db:Session=Depends(get_db)):
    obj=db.query(Withdrawal).filter(Withdrawal.id==item_id).first()
    if not obj: raise HTTPException(404,'Withdrawal not found')
    for field,value in data.model_dump().items(): setattr(obj,field,value)
    db.commit(); db.refresh(obj); return obj
@router.delete('/{item_id}',status_code=204)
def delete(item_id:int,db:Session=Depends(get_db)):
    obj=db.query(Withdrawal).filter(Withdrawal.id==item_id).first()
    if not obj: raise HTTPException(404,'Withdrawal not found')
    db.delete(obj); db.commit()
