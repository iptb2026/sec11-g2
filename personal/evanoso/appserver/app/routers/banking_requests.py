from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.security import require_roles
from app.core.audit import record_audit_event
from app.core.db_utils import commit_or_409
from app.models.banking_request import BankingRequest, Recipient
from app.models.user import User
from app.models.account import Account
from app.models.deposit import Deposit
from app.models.withdrawal import Withdrawal
from app.models.withdrawal_limit import WithdrawalLimit
from app.routers.customer_banking import get_customer, lock_owned_account

router = APIRouter(tags=["Banking requests"])


class RequestInput(BaseModel):
    account_id: int
    kind: Literal["DEPOSIT", "WITHDRAWAL"]
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    note: str = Field(default="", max_length=250)


class RequestOutput(RequestInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    reference: str
    status: str
    created_at: datetime


class ReviewInput(BaseModel):
    status: Literal["APPROVED", "REJECTED"]


@router.get("/customer/requests/", response_model=list[RequestOutput])
def my_requests(user: User = Depends(get_customer), db: Session = Depends(get_db)):
    return db.query(BankingRequest).filter(BankingRequest.customer_id == user.id).order_by(BankingRequest.id.desc()).all()


@router.post("/customer/requests/", response_model=RequestOutput, status_code=201)
def submit_request(data: RequestInput, user: User = Depends(get_customer), db: Session = Depends(get_db)):
    account = lock_owned_account(db, data.account_id, user.id)
    if data.kind == "WITHDRAWAL" and account.available_balance < data.amount:
        raise HTTPException(400, "Insufficient available balance")
    item = BankingRequest(customer_id=user.id, reference=f"REQ-{uuid4().hex[:24].upper()}", **data.model_dump())
    db.add(item)
    commit_or_409(db, "Could not submit request")
    db.refresh(item)
    return item


@router.get("/banking-requests/", response_model=list[RequestOutput])
def pending_requests(user: User = Depends(require_roles("ADMIN", "STAFF")), db: Session = Depends(get_db)):
    return db.query(BankingRequest).order_by(BankingRequest.id.desc()).all()


@router.post("/banking-requests/{request_id}/review", response_model=RequestOutput)
def review_request(request_id: int, data: ReviewInput, request: Request, user: User = Depends(require_roles("ADMIN", "STAFF")), db: Session = Depends(get_db)):
    item = db.query(BankingRequest).filter(BankingRequest.id == request_id).with_for_update().first()
    if not item:
        raise HTTPException(404, "Request not found")
    if item.status != "PENDING":
        raise HTTPException(409, "Request has already been reviewed")
    if data.status == "APPROVED":
        account = lock_owned_account(db, item.account_id, item.customer_id)
        if item.kind == "WITHDRAWAL" and account.available_balance < item.amount:
            raise HTTPException(400, "Insufficient available balance")
        if item.kind == "WITHDRAWAL":
            limit = db.query(WithdrawalLimit).filter(WithdrawalLimit.account_id == account.id).with_for_update().first()
            if limit and limit.daily_used_amount + item.amount > limit.daily_limit_amount:
                raise HTTPException(400, "This withdrawal would exceed the daily withdrawal limit")
            if limit:
                limit.daily_used_amount += item.amount
        # These are simulated branch requests; approval records the actual transaction.
        delta = item.amount if item.kind == "DEPOSIT" else -item.amount
        account.available_balance += delta
        account.ledger_balance += delta
        model = Deposit if item.kind == "DEPOSIT" else Withdrawal
        db.add(model(account_id=account.id, amount=item.amount, reference_number=item.reference, remarks=item.note, transaction_date=datetime.utcnow(), **({"deposit_channel": "CASH", "deposited_by_user_id": user.id} if item.kind == "DEPOSIT" else {"withdrawal_channel": "BRANCH", "approved_by_user_id": user.id})))
    item.status = data.status
    item.reviewed_by = user.id
    record_audit_event(db, request, "UPDATE", "banking_requests", item.id, old_value={"status": "PENDING"}, new_value={"status": item.status, "reference": item.reference, "reviewed_by": user.id})
    commit_or_409(db, "Request could not be processed")
    db.refresh(item)
    return item


class RecipientInput(BaseModel):
    name: str = Field(min_length=1, max_length=80, pattern=r"\S")
    account_number: str = Field(min_length=1, max_length=100)


class RecipientOutput(RecipientInput):
    model_config = ConfigDict(from_attributes=True)
    id: int


@router.get("/customer/recipients/", response_model=list[RecipientOutput])
def recipients(user: User = Depends(get_customer), db: Session = Depends(get_db)):
    return db.query(Recipient).filter(Recipient.customer_id == user.id).all()


@router.post("/customer/recipients/", response_model=RecipientOutput, status_code=201)
def add_recipient(data: RecipientInput, user: User = Depends(get_customer), db: Session = Depends(get_db)):
    if not db.query(Account).filter(Account.account_number == data.account_number, Account.status == "ACTIVE").first():
        raise HTTPException(400, "Enter a valid active Bembank account")
    item = Recipient(customer_id=user.id, **data.model_dump())
    db.add(item)
    commit_or_409(db, "Could not save recipient")
    db.refresh(item)
    return item


@router.delete("/customer/recipients/{recipient_id}", status_code=204)
def delete_recipient(recipient_id: int, user: User = Depends(get_customer), db: Session = Depends(get_db)):
    item = db.query(Recipient).filter(Recipient.id == recipient_id, Recipient.customer_id == user.id).first()
    if not item:
        raise HTTPException(404, "Recipient not found")
    db.delete(item)
    db.commit()
