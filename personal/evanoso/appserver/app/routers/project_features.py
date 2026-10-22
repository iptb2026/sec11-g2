from app.core.password_policy import StrongPassword
"""Class-project onboarding, simulated other-bank transfers, and statements."""
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app.core.otp import throttle
from app.database.session import get_db
from app.core.security import require_roles, hash_password
from app.core.audit import record_audit_event
from app.core.db_utils import commit_or_409
from app.models.user import User
from app.models.role import Role
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.bank import Bank
from app.models.fee_record import FeeRecord
from app.models.interest_record import InterestRecord
from app.models.interbank_transfer import InterbankTransfer
from app.routers.customer_banking import get_customer, lock_owned_account, list_my_transactions
from app.schemas.interbank_transfer import InterbankTransferOut

router = APIRouter(tags=['Project banking'])

class PublicRegistration(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    username: str = Field(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_.-]+$')
    password: StrongPassword
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    mobile_number: str = Field(default='', max_length=30)
    date_of_birth: date | None = None

class Registration(PublicRegistration):
    account_type_id: int

@router.post('/staff/customers/', status_code=201)
def register_customer(data: Registration, request: Request, actor=Depends(require_roles('STAFF', 'ADMIN')), db: Session = Depends(get_db)):
    return create_customer(data, request, db)

def create_customer(data, request, db):
    try:
        return _create_customer(data, request, db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Customer details conflict with an existing record')


def _create_customer(data, request, db):
    if data.date_of_birth and data.date_of_birth >= date.today():
        raise HTTPException(400, 'Date of birth must be in the past')
    if not db.get(AccountType, data.account_type_id):
        raise HTTPException(400, 'Choose a valid account type')
    role = db.query(Role).filter(Role.role_code == 'CUSTOMER').first()
    if not role:
        raise HTTPException(409, 'Customer role must be configured by an administrator')
    if db.query(User).filter((func.lower(User.username) == data.username.lower()) | (func.lower(User.email) == str(data.email).lower())).first():
        raise HTTPException(409, 'Username or email is already registered')
    user = User(**data.model_dump(exclude={'password', 'account_type_id'}), hashed_password=hash_password(data.password), role_id=role.id, account_status='ACTIVE')
    db.add(user)
    db.flush()
    account = Account(customer_id=user.id, account_type_id=data.account_type_id, account_number='BEM' + uuid4().hex[:20].upper(), available_balance=0, ledger_balance=0, currency_code='PHP', status='ACTIVE')
    db.add(account)
    db.flush()
    record_audit_event(db, request, 'CREATE', 'accounts', account.id, new_value={'customer_id': user.id, 'account_number': account.account_number, 'opening_balance': '0.00'})
    commit_or_409(db, 'Customer details conflict with an existing record')
    return {'customer_id': user.id, 'username': user.username, 'account_number': account.account_number, 'account_id': account.id}

@router.post('/auth/signup', status_code=201)
def signup(data: PublicRegistration, request: Request, db: Session = Depends(get_db)):
    throttle(db, 'signup:' + (request.client.host if request.client else 'unknown'))
    account_type = db.query(AccountType).filter(AccountType.type_code == 'FAMILY_SAVINGS').first()
    if not account_type:
        raise HTTPException(503, 'Sign-up is temporarily unavailable. Please try again later.')
    return create_customer(Registration(**data.model_dump(), account_type_id=account_type.id), request, db)


class ExternalTransfer(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    source_account_id: int
    target_bank_id: int
    target_account_number: str = Field(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9-]+$')
    beneficiary_name: str = Field(min_length=1, max_length=150)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)

@router.get('/customer/other-banks/')
def other_banks(user=Depends(get_customer), db: Session = Depends(get_db)):
    return [{'id': b.id, 'bank_name': b.bank_name} for b in db.query(Bank).filter(Bank.status == 'ACTIVE').order_by(Bank.bank_name).all()]

@router.post('/customer/interbank-transfers/', response_model=InterbankTransferOut, status_code=201)
def external_transfer(data: ExternalTransfer, request: Request, user=Depends(get_customer), db: Session = Depends(get_db)):
    account = lock_owned_account(db, data.source_account_id, user.id)
    bank = db.get(Bank, data.target_bank_id)
    if not bank or bank.status != 'ACTIVE':
        raise HTTPException(400, 'Choose an active destination bank')
    if account.available_balance < data.amount:
        raise HTTPException(400, 'Insufficient available balance')
    transfer = InterbankTransfer(**data.model_dump(), transfer_fee=0, reference_number='EXT-' + uuid4().hex[:24].upper(), status='PROCESSING')
    account.available_balance -= data.amount
    account.ledger_balance -= data.amount
    db.add(transfer)
    db.flush()
    record_audit_event(db, request, 'CREATE', 'interbank_transfers', transfer.id, new_value={'amount': str(data.amount), 'reference_number': transfer.reference_number, 'status': 'PROCESSING'})
    commit_or_409(db, 'Transfer could not be recorded')
    db.refresh(transfer)
    return transfer

@router.get('/customer/interbank-transfers/', response_model=list[InterbankTransferOut])
def external_history(user=Depends(get_customer), db: Session = Depends(get_db)):
    return db.query(InterbankTransfer).join(Account, Account.id == InterbankTransfer.source_account_id).filter(Account.customer_id == user.id).order_by(InterbankTransfer.id.desc()).all()

@router.get('/reports/accounts/{account_id}/statement')
def statement(account_id: int, start: date, end: date, actor=Depends(require_roles('CUSTOMER', 'STAFF', 'ADMIN')), db: Session = Depends(get_db)):
    if start > end or end > date.today():
        raise HTTPException(400, 'Choose an ordered date range ending today or earlier')
    user = actor
    account = db.query(Account).filter(Account.id == account_id).with_for_update().first()
    if not account or (db.get(Role, user.role_id).role_code == 'CUSTOMER' and account.customer_id != user.id):
        raise HTTPException(404, 'Account not found')
    owner = db.get(User, account.customer_id)
    events = []
    for row in list_my_transactions(owner, db):
        if row['account_number'] != account.account_number or row['transaction_type'].startswith('INVESTMENT'):
            continue  # Investments reserve available funds, not ledger funds.
        if row['transaction_type'].startswith('TRANSFER') and row['status'] != 'SUCCESS':
            continue
        events.append({'date': row['transaction_date'], 'reference': row['reference'] or row['id'], 'description': row['transaction_type'], 'delta': row['amount'] if row['direction'] == 'CREDIT' else -row['amount']})
    for item in db.query(FeeRecord).filter(FeeRecord.account_id == account.id).all():
        events.append({'date': item.charged_at, 'reference': item.transaction_reference or f'FEE-{item.id}', 'description': 'FEE', 'delta': -item.amount_charged})
    for item in db.query(InterestRecord).filter(InterestRecord.account_id == account.id).all():
        events.append({'date': item.credited_at, 'reference': f'INT-{item.id}', 'description': 'INTEREST', 'delta': item.amount_credited})
    events.sort(key=lambda e: (e['date'], e['reference']))
    lower, upper = datetime.combine(start, time.min), datetime.combine(end + timedelta(days=1), time.min)
    opening = account.ledger_balance - sum((e['delta'] for e in events if e['date'] >= lower), Decimal('0'))
    balance, debit, credit, rows = opening, Decimal('0'), Decimal('0'), []
    for e in events:
        if lower <= e['date'] < upper:
            balance += e['delta']
            debit += max(-e['delta'], Decimal('0'))
            credit += max(e['delta'], Decimal('0'))
            rows.append({'date': e['date'], 'reference': e['reference'], 'description': e['description'], 'debit': str(max(-e['delta'], Decimal('0'))), 'credit': str(max(e['delta'], Decimal('0'))), 'balance': str(balance)})
    return {'account_number': account.account_number, 'customer': f'{owner.first_name} {owner.last_name}', 'account_type': db.get(AccountType, account.account_type_id).type_name, 'currency': account.currency_code, 'start': start, 'end': end, 'opening_balance': str(opening), 'closing_balance': str(balance), 'total_debits': str(debit), 'total_credits': str(credit), 'rows': rows}
