from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.account import Account
from app.models.ledger_entry import LedgerEntry
from app.schemas.ledger_entry import LedgerEntryCreate,LedgerEntryOut
router=APIRouter(prefix='/ledger-entries',tags=['Layer 5 - Ledger Entries'])
@router.post('/',response_model=LedgerEntryOut,status_code=201)
def create(data:LedgerEntryCreate,db:Session=Depends(get_db)):
    account=db.query(Account).filter(Account.id==data.account_id).first()
    if not account: raise HTTPException(400,'account_id does not exist')
    obj=LedgerEntry(**data.model_dump(),balance_after=account.available_balance); db.add(obj); db.commit(); db.refresh(obj); return obj
@router.get('/',response_model=list[LedgerEntryOut])
def listing(db:Session=Depends(get_db)): return db.query(LedgerEntry).all()
@router.get('/{item_id}',response_model=LedgerEntryOut)
def get(item_id:int,db:Session=Depends(get_db)):
    obj=db.query(LedgerEntry).filter(LedgerEntry.id==item_id).first()
    if not obj: raise HTTPException(404,'Ledger entry not found')
    return obj
@router.delete('/{item_id}',status_code=204)
def delete(item_id:int,db:Session=Depends(get_db)):
    obj=db.query(LedgerEntry).filter(LedgerEntry.id==item_id).first()
    if not obj: raise HTTPException(404,'Ledger entry not found')
    db.delete(obj); db.commit()
