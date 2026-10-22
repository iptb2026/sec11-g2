from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.audit import record_audit_event
from app.core.db_utils import commit_or_409
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.account import Account
from app.models.bill_payment import BillPayment
from app.models.deposit import Deposit
from app.models.interbank_transfer import InterbankTransfer
from app.models.investment import Investment
from app.models.role import Role
from app.models.transfer import Transfer
from app.models.user import User
from app.models.withdrawal import Withdrawal
from app.models.savings_goal import SavingsGoal
from app.models.concept_features import MobileLoad
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.account import AccountOut
from app.schemas.customer_banking import (
    BillPaymentCreate,
    BillPaymentOut,
    CustomerTransactionOut,
    CustomerTransferCreate,
    InvestmentCreate,
    InvestmentOut,
)
from app.schemas.transfer import TransferOut

router = APIRouter(prefix="/customer", tags=["Customer Banking"])
INVESTMENT_TERMS = {"SHORT_TERM": 3, "MEDIUM_TERM": 6, "LONG_TERM": 12}


class GoalInput(BaseModel):
    name: str = Field(min_length=1, max_length=80, pattern=r"\S")
    target_amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    saved_amount: Decimal = Field(ge=0, max_digits=18, decimal_places=2)


class GoalOutput(GoalInput):
    model_config = ConfigDict(from_attributes=True)
    id: int


def get_customer(
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    user = db.query(User).filter(User.username == username).first()
    if not user or user.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Active customer account required")

    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role or role.role_code != "CUSTOMER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer access required")
    return user


def lock_owned_account(db: Session, account_id: int, customer_id: int) -> Account:
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.customer_id == customer_id)
        .with_for_update()
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.status != "ACTIVE":
        raise HTTPException(status_code=409, detail=f"Account is {account.status}")
    return account


@router.get("/goals/", response_model=list[GoalOutput])
def list_goals(customer: User = Depends(get_customer), db: Session = Depends(get_db)):
    return db.query(SavingsGoal).filter(SavingsGoal.customer_id == customer.id).order_by(SavingsGoal.id).all()


@router.post("/goals/", response_model=GoalOutput, status_code=201)
def create_goal(data: GoalInput, customer: User = Depends(get_customer), db: Session = Depends(get_db)):
    goal = SavingsGoal(customer_id=customer.id, **data.model_dump())
    db.add(goal)
    commit_or_409(db, "Could not save savings goal")
    db.refresh(goal)
    return goal


@router.put("/goals/{goal_id}", response_model=GoalOutput)
def update_goal(goal_id: int, data: GoalInput, customer: User = Depends(get_customer), db: Session = Depends(get_db)):
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id, SavingsGoal.customer_id == customer.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    for key, value in data.model_dump().items():
        setattr(goal, key, value)
    commit_or_409(db, "Could not update savings goal")
    db.refresh(goal)
    return goal


@router.get("/accounts/", response_model=list[AccountOut])
def list_my_accounts(customer: User = Depends(get_customer), db: Session = Depends(get_db)):
    return db.query(Account).filter(Account.customer_id == customer.id).order_by(Account.id).all()


@router.post("/transfers/", response_model=TransferOut, status_code=status.HTTP_201_CREATED)
def create_my_transfer(
    data: CustomerTransferCreate,
    request: Request,
    customer: User = Depends(get_customer),
    db: Session = Depends(get_db),
):
    source = (
        db.query(Account)
        .filter(Account.id == data.source_account_id, Account.customer_id == customer.id)
        .first()
    )
    if not source:
        raise HTTPException(status_code=404, detail="Source account not found")

    destination = db.query(Account).filter(Account.account_number == data.destination_account_number).first()
    if not destination or destination.id == source.id:
        raise HTTPException(status_code=400, detail="Choose a different, valid destination account")

    accounts = {
        account.id: account
        for account in db.query(Account)
        .filter(Account.id.in_(sorted([source.id, destination.id])))
        .with_for_update()
        .all()
    }
    source = accounts[source.id]
    destination = accounts[destination.id]
    if source.status != "ACTIVE" or destination.status != "ACTIVE":
        raise HTTPException(status_code=409, detail="Both accounts must be active")
    if source.available_balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient available balance")

    transfer = Transfer(
        source_account_id=source.id,
        destination_account_id=destination.id,
        transfer_reference=f"CUS-{uuid4().hex[:24].upper()}",
        amount=data.amount,
        transfer_type="INTERNAL",
        remarks=data.remarks,
        status="SUCCESS",
        completed_at=datetime.utcnow(),
    )
    source.available_balance -= data.amount
    source.ledger_balance -= data.amount
    destination.available_balance += data.amount
    destination.ledger_balance += data.amount
    db.add(transfer)
    db.flush()
    record_audit_event(
        db,
        request,
        "CREATE",
        "transfers",
        transfer.id,
        new_value={
            "source_account_id": source.id,
            "destination_account_id": destination.id,
            "transfer_reference": transfer.transfer_reference,
            "amount": str(data.amount),
            "initiated_by_customer_id": customer.id,
        },
    )
    commit_or_409(db, "Transfer could not be completed because the record conflicts with existing data")
    db.refresh(transfer)
    return transfer


@router.get("/transfers/", response_model=list[TransferOut])
def list_my_transfers(customer: User = Depends(get_customer), db: Session = Depends(get_db)):
    account_ids = [row.id for row in db.query(Account.id).filter(Account.customer_id == customer.id).all()]
    if not account_ids:
        return []
    return (
        db.query(Transfer)
        .filter(or_(Transfer.source_account_id.in_(account_ids), Transfer.destination_account_id.in_(account_ids)))
        .order_by(Transfer.created_at.desc())
        .all()
    )


@router.post("/bill-payments/", response_model=BillPaymentOut, status_code=status.HTTP_201_CREATED)
def pay_bill(
    data: BillPaymentCreate,
    request: Request,
    customer: User = Depends(get_customer),
    db: Session = Depends(get_db),
):
    account = lock_owned_account(db, data.account_id, customer.id)
    if account.available_balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient available balance")

    payment = BillPayment(
        account_id=account.id,
        biller_name=data.biller_name.strip(),
        biller_reference=data.biller_reference.strip(),
        payment_reference=f"BILL-{uuid4().hex[:24].upper()}",
        amount=data.amount,
        status="COMPLETED",
    )
    account.available_balance -= data.amount
    account.ledger_balance -= data.amount
    db.add(payment)
    db.flush()
    record_audit_event(
        db,
        request,
        "CREATE",
        "bill_payments",
        payment.id,
        new_value={
            "account_id": account.id,
            "biller_name": payment.biller_name,
            "biller_reference": payment.biller_reference,
            "payment_reference": payment.payment_reference,
            "amount": str(data.amount),
            "initiated_by_customer_id": customer.id,
        },
    )
    commit_or_409(db, "Bill payment could not be recorded")
    db.refresh(payment)
    return payment


@router.get("/bill-payments/", response_model=list[BillPaymentOut])
def list_my_bill_payments(customer: User = Depends(get_customer), db: Session = Depends(get_db)):
    return (
        db.query(BillPayment)
        .join(Account, BillPayment.account_id == Account.id)
        .filter(Account.customer_id == customer.id)
        .order_by(BillPayment.created_at.desc())
        .all()
    )


@router.post("/investments/", response_model=InvestmentOut, status_code=status.HTTP_201_CREATED)
def create_investment(
    data: InvestmentCreate,
    request: Request,
    customer: User = Depends(get_customer),
    db: Session = Depends(get_db),
):
    account = lock_owned_account(db, data.account_id, customer.id)
    if account.available_balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient available balance")

    investment = Investment(
        account_id=account.id,
        plan_code=data.plan_code,
        term_months=INVESTMENT_TERMS[data.plan_code],
        amount=data.amount,
        status="ACTIVE",
    )
    account.available_balance -= data.amount
    db.add(investment)
    db.flush()
    record_audit_event(
        db,
        request,
        "CREATE",
        "investments",
        investment.id,
        new_value={
            "account_id": account.id,
            "plan_code": investment.plan_code,
            "term_months": investment.term_months,
            "amount": str(data.amount),
            "initiated_by_customer_id": customer.id,
        },
    )
    commit_or_409(db, "Investment allocation could not be recorded")
    db.refresh(investment)
    return investment


@router.get("/investments/", response_model=list[InvestmentOut])
def list_my_investments(customer: User = Depends(get_customer), db: Session = Depends(get_db)):
    return (
        db.query(Investment)
        .join(Account, Investment.account_id == Account.id)
        .filter(Account.customer_id == customer.id)
        .order_by(Investment.created_at.desc())
        .all()
    )


@router.post("/investments/{investment_id}/redeem", response_model=InvestmentOut)
def redeem_investment(
    investment_id: int,
    request: Request,
    customer: User = Depends(get_customer),
    db: Session = Depends(get_db),
):
    investment = (
        db.query(Investment)
        .join(Account, Investment.account_id == Account.id)
        .filter(Investment.id == investment_id, Account.customer_id == customer.id)
        .with_for_update()
        .first()
    )
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    if investment.status != "ACTIVE":
        raise HTTPException(status_code=409, detail="Investment is already redeemed")

    account = lock_owned_account(db, investment.account_id, customer.id)
    investment.status = "REDEEMED"
    investment.redeemed_at = datetime.utcnow()
    account.available_balance += investment.amount
    record_audit_event(
        db,
        request,
        "UPDATE",
        "investments",
        investment.id,
        old_value={"status": "ACTIVE", "amount": str(investment.amount)},
        new_value={"status": "REDEEMED", "amount": str(investment.amount), "redeemed_by_customer_id": customer.id},
    )
    commit_or_409(db, "Investment redemption could not be recorded")
    db.refresh(investment)
    return investment


@router.get("/transactions/", response_model=list[CustomerTransactionOut])
def list_my_transactions(customer: User = Depends(get_customer), db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.customer_id == customer.id).all()
    account_ids = [account.id for account in accounts]
    account_numbers = {account.id: account.account_number for account in accounts}
    if not account_ids:
        return []

    rows = []
    for item in db.query(Deposit).filter(Deposit.account_id.in_(account_ids)).all():
        rows.append({"id": f"deposit-{item.id}", "account_number": account_numbers[item.account_id], "transaction_type": "DEPOSIT", "reference": item.reference_number, "amount": item.amount, "direction": "CREDIT", "status": "COMPLETED", "transaction_date": item.transaction_date})
    for item in db.query(Withdrawal).filter(Withdrawal.account_id.in_(account_ids)).all():
        rows.append({"id": f"withdrawal-{item.id}", "account_number": account_numbers[item.account_id], "transaction_type": "WITHDRAWAL", "reference": item.reference_number, "amount": item.amount, "direction": "DEBIT", "status": "COMPLETED", "transaction_date": item.transaction_date})
    for item in db.query(Transfer).filter(or_(Transfer.source_account_id.in_(account_ids), Transfer.destination_account_id.in_(account_ids))).all():
        if item.source_account_id in account_numbers:
            rows.append({"id": f"transfer-out-{item.id}", "account_number": account_numbers[item.source_account_id], "transaction_type": "TRANSFER OUT", "reference": item.transfer_reference, "amount": item.amount, "direction": "DEBIT", "status": item.status, "transaction_date": item.created_at})
        if item.destination_account_id in account_numbers:
            rows.append({"id": f"transfer-in-{item.id}", "account_number": account_numbers[item.destination_account_id], "transaction_type": "TRANSFER IN", "reference": item.transfer_reference, "amount": item.amount, "direction": "CREDIT", "status": item.status, "transaction_date": item.created_at})
    for item in db.query(InterbankTransfer).filter(InterbankTransfer.source_account_id.in_(account_ids)).all():
        rows.append({"id": f"interbank-{item.id}", "account_number": account_numbers[item.source_account_id], "transaction_type": "INTERBANK TRANSFER", "reference": item.reference_number, "amount": item.amount + item.transfer_fee, "direction": "DEBIT", "status": item.status, "transaction_date": item.initiated_at})
        if item.status in ('FAILED', 'REVERSED'):
            rows.append({"id": f"interbank-refund-{item.id}", "account_number": account_numbers[item.source_account_id], "transaction_type": "INTERBANK REFUND", "reference": item.reference_number, "amount": item.amount + item.transfer_fee, "direction": "CREDIT", "status": "COMPLETED", "transaction_date": item.completed_at or item.initiated_at})
    for item in db.query(BillPayment).filter(BillPayment.account_id.in_(account_ids)).all():
        rows.append({"id": f"bill-{item.id}", "account_number": account_numbers[item.account_id], "transaction_type": "BILL PAYMENT", "reference": item.payment_reference, "amount": item.amount, "direction": "DEBIT", "status": item.status, "transaction_date": item.created_at})
    for item in db.query(Investment).filter(Investment.account_id.in_(account_ids)).all():
        rows.append({"id": f"investment-{item.id}", "account_number": account_numbers[item.account_id], "transaction_type": "INVESTMENT ALLOCATION", "reference": f"INV-{item.id}", "amount": item.amount, "direction": "DEBIT", "status": item.status, "transaction_date": item.created_at})
        if item.redeemed_at:
            rows.append({"id": f"investment-redeemed-{item.id}", "account_number": account_numbers[item.account_id], "transaction_type": "INVESTMENT REDEMPTION", "reference": f"INV-{item.id}", "amount": item.amount, "direction": "CREDIT", "status": "COMPLETED", "transaction_date": item.redeemed_at})

    for item in db.query(MobileLoad).filter(MobileLoad.account_id.in_(account_ids)).all():
        rows.append({"id": f"load-{item.id}", "account_number": account_numbers[item.account_id], "transaction_type": "MOBILE LOAD", "reference": item.reference, "amount": item.amount, "direction": "DEBIT", "status": "COMPLETED", "transaction_date": item.created_at})
    rows.sort(key=lambda row: row["transaction_date"] or datetime.min, reverse=True)
    return rows
