from datetime import datetime
from uuid import uuid4
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.security import require_roles
from app.core.audit import record_audit_event
from app.core.db_utils import commit_or_409
from app.models.account_application import AccountApplication
from app.models.account_type import AccountType
from app.models.account import Account
from app.models.user import User
from app.routers.customer_banking import get_customer

router = APIRouter(tags=["Account applications"])


class ApplicationInput(BaseModel):
    account_type_id: int


class ApplicationOutput(ApplicationInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    customer_id: int
    status: str
    account_number: str | None
    created_at: datetime


@router.get("/customer/account-options/")
def account_options(user: User = Depends(get_customer), db: Session = Depends(get_db)):
    return [{"id": t.id, "name": t.type_name} for t in db.query(AccountType).all()]


@router.get("/customer/account-applications/", response_model=list[ApplicationOutput])
def my_applications(user: User = Depends(get_customer), db: Session = Depends(get_db)):
    return db.query(AccountApplication).filter(AccountApplication.customer_id == user.id).order_by(AccountApplication.id.desc()).all()


@router.post("/customer/account-applications/", response_model=ApplicationOutput, status_code=201)
def apply(data: ApplicationInput, user: User = Depends(get_customer), db: Session = Depends(get_db)):
    if not db.query(AccountType).filter(AccountType.id == data.account_type_id).first():
        raise HTTPException(400, "Account type not found")
    application = AccountApplication(customer_id=user.id, account_type_id=data.account_type_id)
    db.add(application)
    commit_or_409(db, "Could not submit account application")
    db.refresh(application)
    return application


@router.get("/account-applications/", response_model=list[ApplicationOutput])
def applications(user: User = Depends(require_roles("ADMIN", "STAFF")), db: Session = Depends(get_db)):
    return db.query(AccountApplication).order_by(AccountApplication.id.desc()).all()


class Decision(BaseModel):
    status: Literal["APPROVED", "REJECTED"]


@router.post("/account-applications/{application_id}/review", response_model=ApplicationOutput)
def review(application_id: int, data: Decision, request: Request, user: User = Depends(require_roles("ADMIN")), db: Session = Depends(get_db)):
    application = db.query(AccountApplication).filter(AccountApplication.id == application_id).with_for_update().first()
    if not application:
        raise HTTPException(404, "Application not found")
    if application.status != "PENDING":
        raise HTTPException(409, "Application has already been reviewed")
    if data.status == "APPROVED":
        customer = db.query(User).filter(User.id == application.customer_id, User.account_status == "ACTIVE").first()
        if not customer:
            raise HTTPException(409, "Customer is no longer active")
        application.account_number = "BEM" + uuid4().hex[:20].upper()
        db.add(Account(account_number=application.account_number, customer_id=application.customer_id, account_type_id=application.account_type_id, available_balance=0, ledger_balance=0, currency_code="PHP", status="ACTIVE", branch_code="ONLINE"))
    application.status = data.status
    record_audit_event(db, request, "UPDATE", "account_applications", application.id, old_value={"status": "PENDING"}, new_value={"status": data.status, "account_number": application.account_number, "reviewed_by": user.id})
    commit_or_409(db, "Could not review account application")
    db.refresh(application)
    return application
