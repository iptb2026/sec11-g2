from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.account import Account
from app.models.fee_record import FeeRecord
from app.models.fee_type import FeeType
from app.schemas.fee_record import FeeRecordCreate,FeeRecordOut
router=APIRouter(prefix='/fee-records',tags=['Layer 5 - Fee Records'])
@router.post('/',response_model=FeeRecordOut,status_code=201)
def create(data:FeeRecordCreate,db:Session=Depends(get_db)):
    account=db.query(Account).filter(Account.id==data.account_id).with_for_update().first()
    if not account: raise HTTPException(400,'account_id does not exist')
    if not db.query(FeeType).filter(FeeType.id==data.fee_type_id).first(): raise HTTPException(400,'fee_type_id does not exist')
    obj=FeeRecord(**data.model_dump()); db.add(obj); account.available_balance-=data.amount_charged; account.ledger_balance-=data.amount_charged; db.commit(); db.refresh(obj); return obj
@router.get('/',response_model=list[FeeRecordOut])
def listing(db:Session=Depends(get_db)): return db.query(FeeRecord).all()
@router.get('/{item_id}',response_model=FeeRecordOut)
def get(item_id:int,db:Session=Depends(get_db)):
    obj=db.query(FeeRecord).filter(FeeRecord.id==item_id).first()
    if not obj: raise HTTPException(404,'Fee record not found')
    return obj
@router.put('/{item_id}',response_model=FeeRecordOut)
def update(item_id:int,data:FeeRecordCreate,db:Session=Depends(get_db)):
    obj=db.query(FeeRecord).filter(FeeRecord.id==item_id).first()
    if not obj: raise HTTPException(404,'Fee record not found')
    for field,value in data.model_dump().items(): setattr(obj,field,value)
    db.commit(); db.refresh(obj); return obj
@router.delete('/{item_id}',status_code=204)
def delete(item_id:int,db:Session=Depends(get_db)):
    obj=db.query(FeeRecord).filter(FeeRecord.id==item_id).first()
    if not obj: raise HTTPException(404,'Fee record not found')
    db.delete(obj); db.commit()
