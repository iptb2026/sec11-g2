# ==== LAYER 3: Account Configuration ====
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import commit_or_409
from app.core.security import get_current_user_model, require_roles
from app.database.session import get_db
from app.models.account_type import AccountType
from app.models.interest_policy import InterestPolicy
from app.models.user import User
from app.schemas.interest_policy import InterestPolicyCreate, InterestPolicyOut

router = APIRouter(prefix="/interest-policies", tags=["Layer 3 - Interest Policies"])


@router.post("/", response_model=InterestPolicyOut, status_code=status.HTTP_201_CREATED)
def create_interest_policy(
    policy: InterestPolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    account_type = db.query(AccountType).filter(AccountType.id == policy.account_type_id).first()
    if not account_type:
        raise HTTPException(status_code=400, detail="account_type_id does not exist")

    new_policy = InterestPolicy(**policy.model_dump())
    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)
    return new_policy


@router.get("/", response_model=list[InterestPolicyOut])
def list_interest_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    return db.query(InterestPolicy).all()


@router.get("/{policy_id}", response_model=InterestPolicyOut)
def get_interest_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_model),
):
    policy = db.query(InterestPolicy).filter(InterestPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Interest policy not found")
    return policy


@router.put("/{policy_id}", response_model=InterestPolicyOut)
def update_interest_policy(
    policy_id: int,
    data: InterestPolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    policy = db.query(InterestPolicy).filter(InterestPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Interest policy not found")

    account_type = db.query(AccountType).filter(AccountType.id == data.account_type_id).first()
    if not account_type:
        raise HTTPException(status_code=400, detail="account_type_id does not exist")

    for field, value in data.model_dump().items():
        setattr(policy, field, value)

    db.commit()
    db.refresh(policy)
    return policy


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interest_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "STAFF")),
):
    policy = db.query(InterestPolicy).filter(InterestPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Interest policy not found")

    db.delete(policy)
    commit_or_409(db, "Cannot delete this interest policy — one or more interest records still reference it")