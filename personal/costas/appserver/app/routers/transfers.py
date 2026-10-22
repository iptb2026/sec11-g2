from datetime import datetime
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.account import Account
from app.models.transfer import Transfer
from app.schemas.transfer import TransferCreate,TransferOut
router=APIRouter(prefix='/transfers',tags=['Layer 4 - Transfers'])
@router.post('/',response_model=TransferOut,status_code=201)
def create(data:TransferCreate,db:Session=Depends(get_db)):
    if data.source_account_id==data.destination_account_id: raise HTTPException(400,'source and destination accounts must be different')
    first,second=sorted([data.source_account_id,data.destination_account_id]); found={a.id:a for a in db.query(Account).filter(Account.id.in_([first,second])).with_for_update().all()}
    source,dest=found.get(data.source_account_id),found.get(data.destination_account_id)
    if not source: raise HTTPException(400,'source_account_id does not exist')
    if not dest: raise HTTPException(400,'destination_account_id does not exist')
    if db.query(Transfer).filter(Transfer.transfer_reference==data.transfer_reference).first(): raise HTTPException(400,'transfer_reference already exists')
    if source.status!='ACTIVE': raise HTTPException(400,f'Source account is {source.status}, cannot transfer')
    if source.available_balance<data.amount: raise HTTPException(400,'Insufficient balance')
    obj=Transfer(**data.model_dump(),status='SUCCESS',completed_at=datetime.utcnow()); db.add(obj); source.available_balance-=data.amount; source.ledger_balance-=data.amount; dest.available_balance+=data.amount; dest.ledger_balance+=data.amount; db.commit(); db.refresh(obj); return obj
@router.get('/',response_model=list[TransferOut])
def listing(db:Session=Depends(get_db)): return db.query(Transfer).all()
@router.get('/{item_id}',response_model=TransferOut)
def get(item_id:int,db:Session=Depends(get_db)):
    obj=db.query(Transfer).filter(Transfer.id==item_id).first()
    if not obj: raise HTTPException(404,'Transfer not found')
    return obj
@router.put('/{item_id}',response_model=TransferOut)
def update(item_id:int,data:TransferCreate,db:Session=Depends(get_db)):
    obj=db.query(Transfer).filter(Transfer.id==item_id).first()
    if not obj: raise HTTPException(404,'Transfer not found')
    for field,value in data.model_dump().items(): setattr(obj,field,value)
    db.commit(); db.refresh(obj); return obj
@router.delete('/{item_id}',status_code=204)
def delete(item_id:int,db:Session=Depends(get_db)):
    obj=db.query(Transfer).filter(Transfer.id==item_id).first()
    if not obj: raise HTTPException(404,'Transfer not found')
    db.delete(obj); db.commit()
