from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.account import Account
from app.models.deposit import Deposit
from app.models.user import User
from app.schemas.deposit import DepositCreate,DepositOut
router=APIRouter(prefix='/deposits',tags=['Layer 4 - Deposits'])
@router.post('/',response_model=DepositOut,status_code=201)
def create(data:DepositCreate,db:Session=Depends(get_db)):
    account=db.query(Account).filter(Account.id==data.account_id).with_for_update().first()
    if not account: raise HTTPException(400,'account_id does not exist')
    if data.deposited_by_user_id is not None and not db.query(User).filter(User.id==data.deposited_by_user_id).first(): raise HTTPException(400,'deposited_by_user_id does not exist')
    if db.query(Deposit).filter(Deposit.reference_number==data.reference_number).first(): raise HTTPException(400,'reference_number already exists')
    obj=Deposit(**data.model_dump()); db.add(obj); account.available_balance+=data.amount; account.ledger_balance+=data.amount; db.commit(); db.refresh(obj); return obj
@router.get('/',response_model=list[DepositOut])
def listing(db:Session=Depends(get_db)): return db.query(Deposit).all()
@router.get('/{item_id}',response_model=DepositOut)
def get(item_id:int,db:Session=Depends(get_db)):
    obj=db.query(Deposit).filter(Deposit.id==item_id).first()
    if not obj: raise HTTPException(404,'Deposit not found')
    return obj
@router.put('/{item_id}',response_model=DepositOut)
def update(item_id:int,data:DepositCreate,db:Session=Depends(get_db)):
    obj=db.query(Deposit).filter(Deposit.id==item_id).first()
    if not obj: raise HTTPException(404,'Deposit not found')
    for field,value in data.model_dump().items(): setattr(obj,field,value)
    db.commit(); db.refresh(obj); return obj
@router.delete('/{item_id}',status_code=204)
def delete(item_id:int,db:Session=Depends(get_db)):
    obj=db.query(Deposit).filter(Deposit.id==item_id).first()
    if not obj: raise HTTPException(404,'Deposit not found')
    db.delete(obj); db.commit()
