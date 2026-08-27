from datetime import datetime
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.account import Account
from app.models.bank import Bank
from app.models.interbank_transfer import InterbankTransfer
from app.schemas.interbank_transfer import InterbankTransferCreate,InterbankTransferStatusUpdate,InterbankTransferOut
router=APIRouter(prefix='/interbank-transfers',tags=['Layer 4 - Interbank Transfers'])
@router.post('/',response_model=InterbankTransferOut,status_code=201)
def create(data:InterbankTransferCreate,db:Session=Depends(get_db)):
    source=db.query(Account).filter(Account.id==data.source_account_id).with_for_update().first()
    if not source: raise HTTPException(400,'source_account_id does not exist')
    if not db.query(Bank).filter(Bank.id==data.target_bank_id).first(): raise HTTPException(400,'target_bank_id does not exist')
    if db.query(InterbankTransfer).filter(InterbankTransfer.reference_number==data.reference_number).first(): raise HTTPException(400,'reference_number already exists')
    if source.status!='ACTIVE': raise HTTPException(400,f'Source account is {source.status}, cannot transfer')
    total=data.amount+data.transfer_fee
    if source.available_balance<total: raise HTTPException(400,'Insufficient balance to cover amount + transfer fee')
    obj=InterbankTransfer(**data.model_dump(),status='PROCESSING'); db.add(obj); source.available_balance-=total; source.ledger_balance-=total; db.commit(); db.refresh(obj); return obj
@router.get('/',response_model=list[InterbankTransferOut])
def listing(db:Session=Depends(get_db)): return db.query(InterbankTransfer).all()
@router.get('/{item_id}',response_model=InterbankTransferOut)
def get(item_id:int,db:Session=Depends(get_db)):
    obj=db.query(InterbankTransfer).filter(InterbankTransfer.id==item_id).first()
    if not obj: raise HTTPException(404,'Interbank transfer not found')
    return obj
@router.put('/{item_id}/status',response_model=InterbankTransferOut)
def update_status(item_id:int,data:InterbankTransferStatusUpdate,db:Session=Depends(get_db)):
    obj=db.query(InterbankTransfer).filter(InterbankTransfer.id==item_id).first()
    if not obj: raise HTTPException(404,'Interbank transfer not found')
    obj.status=data.status
    if data.status in ('SUCCESS','FAILED','REVERSED'): obj.completed_at=datetime.utcnow()
    db.commit(); db.refresh(obj); return obj
@router.delete('/{item_id}',status_code=204)
def delete(item_id:int,db:Session=Depends(get_db)):
    obj=db.query(InterbankTransfer).filter(InterbankTransfer.id==item_id).first()
    if not obj: raise HTTPException(404,'Interbank transfer not found')
    db.delete(obj); db.commit()
