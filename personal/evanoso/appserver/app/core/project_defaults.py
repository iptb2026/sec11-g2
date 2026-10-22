"""Add project reference choices without changing existing records."""
from app.models.account_type import AccountType
from app.models.bank import Bank

def ensure_project_defaults(db):
    for code, name in [('FAMILY_SAVINGS', 'Family savings account'), ('EMPLOYEE', 'Employee account'), ('BUSINESS', 'Business account')]:
        if not db.query(AccountType).filter(AccountType.type_code == code).first():
            db.add(AccountType(type_code=code, type_name=name, minimum_balance=0, opening_deposit=0, annual_interest_rate=0, daily_withdrawal_limit=10000))
    for code, name in [('NORTHSTAR', 'Northstar Bank'), ('HARBOR', 'Harbor Bank')]:
        if not db.query(Bank).filter(Bank.bank_code == code).first():
            db.add(Bank(bank_code=code, bank_name=name, short_name=name, status='ACTIVE'))
    db.commit()
