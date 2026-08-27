"""
Seed script for Evanoso Mini Banking System.
Creates roles, test users (Admin, Staff, Customer), reference banks, account types, and demo accounts.
Run with: python seed.py
"""

from decimal import Decimal
from datetime import datetime
from app.database.session import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User
from app.models.bank import Bank
from app.models.account_type import AccountType
from app.models.account import Account


def seed():
    print("Connecting to database and creating tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. ROLES
        roles_data = [
            ("ADMIN", "System Administrator", "Full administrative access to all system resources and audit logs"),
            ("STAFF", "Bank Staff", "Operational access to process customer accounts, deposits, and withdrawals"),
            ("CUSTOMER", "Bank Customer", "Customer access to personal accounts and fund transfers"),
        ]
        created_roles = {}
        for code, name, desc in roles_data:
            role = db.query(Role).filter(Role.role_code == code).first()
            if not role:
                role = Role(role_code=code, role_name=name, description=desc)
                db.add(role)
                db.flush()
                print(f"[+] Created role: {code}")
            created_roles[code] = role

        # 2. USERS
        test_users = [
            {
                "username": "admin",
                "password": "Password123!",
                "email": "admin@bank.local",
                "first_name": "System",
                "last_name": "Admin",
                "role_id": created_roles["ADMIN"].id,
                "account_status": "ACTIVE",
            },
            {
                "username": "staff",
                "password": "Password123!",
                "email": "staff@bank.local",
                "first_name": "Bank",
                "last_name": "Officer",
                "role_id": created_roles["STAFF"].id,
                "account_status": "ACTIVE",
            },
            {
                "username": "customer",
                "password": "Password123!",
                "email": "customer@bank.local",
                "first_name": "Juan",
                "last_name": "Dela Cruz",
                "role_id": created_roles["CUSTOMER"].id,
                "account_status": "ACTIVE",
            },
        ]

        created_users = {}
        for u in test_users:
            user = db.query(User).filter(User.username == u["username"]).first()
            if not user:
                user = User(
                    username=u["username"],
                    hashed_password=hash_password(u["password"]),
                    email=u["email"],
                    first_name=u["first_name"],
                    last_name=u["last_name"],
                    role_id=u["role_id"],
                    account_status=u["account_status"],
                )
                db.add(user)
                db.flush()
                print(f"[+] Created user: {u['username']} (Role: {u['role_id']})")
            created_users[u["username"]] = user

        # 3. REFERENCE BANK
        if not db.query(Bank).filter(Bank.bank_code == "BDO").first():
            bank = Bank(
                bank_code="BDO",
                bank_name="Banco de Oro Universal Bank",
                short_name="BDO",
                status="ACTIVE",
            )
            db.add(bank)
            print("[+] Created reference bank: BDO")

        # 4. ACCOUNT TYPE
        acc_type = db.query(AccountType).filter(AccountType.type_code == "SAVINGS").first()
        if not acc_type:
            acc_type = AccountType(
                type_code="SAVINGS",
                type_name="Regular Savings Account",
                minimum_balance=Decimal("500.00"),
                opening_deposit=Decimal("1000.00"),
                annual_interest_rate=Decimal("1.50"),
                daily_withdrawal_limit=Decimal("50000.00"),
            )
            db.add(acc_type)
            db.flush()
            print("[+] Created account type: SAVINGS")

        # 5. DEMO ACCOUNT FOR CUSTOMER
        customer_user = created_users.get("customer")
        if customer_user and acc_type:
            if not db.query(Account).filter(Account.account_number == "1000-2026-0001").first():
                account = Account(
                    account_number="1000-2026-0001",
                    customer_id=customer_user.id,
                    account_type_id=acc_type.id,
                    available_balance=Decimal("25000.00"),
                    ledger_balance=Decimal("25000.00"),
                    currency_code="PHP",
                    status="ACTIVE",
                    branch_code="MAIN-01",
                )
                db.add(account)
                print("[+] Created customer bank account: 1000-2026-0001 (Balance: PHP 25,000.00)")

        db.commit()
        print("\nSUCCESS! Database seeding completed successfully.")
        print("Test Accounts Available:")
        print("  Admin:    admin / Password123!")
        print("  Staff:    staff / Password123!")
        print("  Customer: customer / Password123!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
