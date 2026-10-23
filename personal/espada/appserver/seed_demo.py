"""Create the fictional BEMBank thesis-demo data. Safe to run more than once."""

from datetime import datetime, timezone
from decimal import Decimal

from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models.account import Account
from app.models.account_type import AccountType
from app.models.deposit import Deposit
from app.models.ledger_entry import LedgerEntry
from app.models.role import Role
from app.models.user import User


def get_role(db, code, name):
    role = db.query(Role).filter_by(role_code=code).first()
    if not role:
        role = Role(role_code=code, role_name=name)
        db.add(role)
        db.flush()
    return role


def main():
    db = SessionLocal()
    try:
        customer_role = get_role(db, "CUSTOMER", "Customer")
        admin_role = get_role(db, "ADMIN", "Administrator")
        savings = db.query(AccountType).filter_by(type_code="DEMO_SAVINGS").first()
        if not savings:
            savings = AccountType(type_code="DEMO_SAVINGS", type_name="Demo Savings")
            db.add(savings)
            db.flush()

        people = [
            ("espada", "Espada", "Customer", "ESP-000001", Decimal("900.00"), admin_role),
            ("marie.santos", "Marie", "Santos", "BEM-000102", Decimal("8550.00"), customer_role),
            ("james.cruz", "James", "Cruz", "BEM-000203", Decimal("12675.50"), customer_role),
            ("lina.reyes", "Lina", "Reyes", "BEM-000304", Decimal("3250.75"), customer_role),
        ]
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        for username, first, last, number, balance, role in people:
            user = db.query(User).filter_by(username=username).first()
            if not user:
                user = User(username=username, hashed_password=hash_password("Espada1234" if username == "espada" else "Demo1234"), first_name=first, last_name=last, role_id=role.id, account_status="ACTIVE")
                db.add(user)
                db.flush()
            if db.query(Account).filter_by(account_number=number).first():
                continue
            account = Account(account_number=number, customer_id=user.id, account_type_id=savings.id, available_balance=balance, ledger_balance=balance, currency_code="PHP", status="ACTIVE", branch_code="BEM-DEMO")
            db.add(account)
            db.flush()
            reference = f"SEED-{number}"
            db.add(Deposit(account_id=account.id, reference_number=reference, amount=balance, deposit_channel="CASH", remarks="Fictional thesis demo balance", transaction_date=now))
            db.add(LedgerEntry(account_id=account.id, transaction_reference=reference, transaction_type="DEPOSIT", credit_amount=balance, debit_amount=Decimal("0"), balance_after=balance, transaction_date=now))
        db.commit()
        print("BEMBank demo data is ready.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
