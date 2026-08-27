from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.account import Account
from app.models.interest_policy import InterestPolicy
from app.models.interest_record import InterestRecord
from app.schemas.interest_record import InterestRecordCreate,InterestRecordOut
router=APIRouter(prefix='/interest-records',tags=['Layer 5 - Interest Records'])
@router.post('/',response_model=InterestRecordOut,status_code=201)
def create(data:InterestRecordCreate,db:Session=Depends(get_db)):
    account=db.query(Account).filter(Account.id==data.account_id).with_for_update().first()
    if not account: raise HTTPException(400,'account_id does not exist')
    if not db.query(InterestPolicy).filter(InterestPolicy.id==data.policy_id).first(): raise HTTPException(400,'policy_id does not exist')
    before=account.available_balance; account.available_balance+=data.amount_credited; account.ledger_balance+=data.amount_credited; obj=InterestRecord(**data.model_dump(),balance_before=before,balance_after=account.available_balance); db.add(obj); db.commit(); db.refresh(obj); return obj
@router.get('/',response_model=list[InterestRecordOut])
def listing(db:Session=Depends(get_db)): return db.query(InterestRecord).all()
@router.get('/{item_id}',response_model=InterestRecordOut)
def get(item_id:int,db:Session=Depends(get_db)):
    obj=db.query(InterestRecord).filter(InterestRecord.id==item_id).first()
    if not obj: raise HTTPException(404,'Interest record not found')
    return obj
@router.delete('/{item_id}',status_code=204)
def delete(item_id:int,db:Session=Depends(get_db)):
    obj=db.query(InterestRecord).filter(InterestRecord.id==item_id).first()
    if not obj: raise HTTPException(404,'Interest record not found')
    db.delete(obj); db.commit()
