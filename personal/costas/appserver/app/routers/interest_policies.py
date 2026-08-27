from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.core.db_utils import commit_or_409
from app.database.session import get_db
from app.models.account_type import AccountType
from app.models.interest_policy import InterestPolicy
from app.schemas.interest_policy import InterestPolicyCreate,InterestPolicyOut
router=APIRouter(prefix='/interest-policies',tags=['Layer 3 - Interest Policies'])
@router.post('/',response_model=InterestPolicyOut,status_code=201)
def create(data:InterestPolicyCreate,db:Session=Depends(get_db)):
    if not db.query(AccountType).filter(AccountType.id==data.account_type_id).first(): raise HTTPException(400,'account_type_id does not exist')
    obj=InterestPolicy(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj
@router.get('/',response_model=list[InterestPolicyOut])
def listing(db:Session=Depends(get_db)): return db.query(InterestPolicy).all()
@router.get('/{policy_id}',response_model=InterestPolicyOut)
def get(policy_id:int,db:Session=Depends(get_db)):
    obj=db.query(InterestPolicy).filter(InterestPolicy.id==policy_id).first()
    if not obj: raise HTTPException(404,'Interest policy not found')
    return obj
@router.put('/{policy_id}',response_model=InterestPolicyOut)
def update(policy_id:int,data:InterestPolicyCreate,db:Session=Depends(get_db)):
    obj=db.query(InterestPolicy).filter(InterestPolicy.id==policy_id).first()
    if not obj: raise HTTPException(404,'Interest policy not found')
    if not db.query(AccountType).filter(AccountType.id==data.account_type_id).first(): raise HTTPException(400,'account_type_id does not exist')
    for field,value in data.model_dump().items(): setattr(obj,field,value)
    db.commit(); db.refresh(obj); return obj
@router.delete('/{policy_id}',status_code=204)
def delete(policy_id:int,db:Session=Depends(get_db)):
    obj=db.query(InterestPolicy).filter(InterestPolicy.id==policy_id).first()
    if not obj: raise HTTPException(404,'Interest policy not found')
    db.delete(obj); commit_or_409(db,'Cannot delete this interest policy — one or more interest records still reference it')
