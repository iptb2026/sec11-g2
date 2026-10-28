"""Isolated SQLite integration tests; never connects to the application's MySQL database."""
import unittest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import BigInteger
from fastapi.testclient import TestClient


@compiles(BigInteger, "sqlite")
def sqlite_bigint(element, compiler, **kw):
    return "INTEGER"


from app.database import session as database
database.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
from app.main import app
from sqlalchemy.orm import sessionmaker
from app.models.role import Role
from app.models.user import User
from app.models.account_type import AccountType
from app.models.account import Account
from app.models.demo_card import DemoCard
from app.core.security import hash_password, check_password

TestSession = sessionmaker(bind=database.engine)


def test_db():
    with TestSession() as db:
        yield db


app.dependency_overrides[database.get_db] = test_db


class BankingTests(unittest.TestCase):
    def setUp(self):
        database.Base.metadata.drop_all(database.engine)
        database.Base.metadata.create_all(database.engine)
        self.client = TestClient(app)
        with TestSession() as db:
            db.add_all([Role(id=1, role_code="CUSTOMER", role_name="Customer"), Role(id=2, role_code="STAFF", role_name="Staff"), Role(id=3, role_code="ADMIN", role_name="Admin")])
            db.flush()
            hashed = hash_password("test-password-123")
            db.add_all([User(id=i, username=name, hashed_password=hashed, first_name=name, last_name="Test", role_id=role, account_status="ACTIVE") for i, name, role in [(1, "alice", 1), (2, "bob", 1), (3, "staff", 2), (4, "admin", 3)]])
            db.add(AccountType(id=1, type_code="SAVINGS", type_name="Savings"))
            db.flush()
            db.add_all([Account(id=i, account_number=f"BEM000{i}", customer_id=i, account_type_id=1, available_balance=1000, ledger_balance=1000, status="ACTIVE") for i in (1, 2)])
            db.commit()
        self.alice = self.login("alice")
        self.bob = self.login("bob")
        self.staff = self.login("staff")
        self.admin = self.login("admin")

    def login(self, username):
        response = self.client.post('/auth/login', data={"username": username, "password": "test-password-123"})
        self.assertEqual(response.status_code, 200, response.text)
        response = self.client.post('/auth/pin/verify', json={"challenge_token": response.json()["challenge_token"], "pin": "012345", "confirm_pin": "012345"})
        self.assertEqual(response.status_code, 200, response.text)
        return {"Authorization": "Bearer " + response.json()["access_token"]}

    def test_auth_roles_and_revocation(self):
        self.assertEqual(self.client.get('/accounts/').status_code, 401)
        self.assertEqual(self.client.get('/accounts/', headers=self.alice).status_code, 403)
        self.assertEqual(self.client.get('/accounts/', headers=self.staff).status_code, 200)
        self.assertEqual(self.client.get('/account-types/', headers=self.staff).status_code, 200)
        self.assertEqual(self.client.post('/account-types/', headers=self.staff, json={}).status_code, 403)
        self.assertEqual(self.client.post('/users/', headers=self.staff, json={}).status_code, 403)
        self.assertEqual(self.client.get('/auth/me', headers=self.alice).json()['username'], 'alice')
        self.assertEqual(self.client.post('/auth/logout', headers=self.alice).status_code, 204)
        self.assertEqual(self.client.get('/auth/me', headers=self.alice).status_code, 401)

    def test_admin_edit_user_does_not_require_or_change_password(self):
        with TestSession() as db:
            original_hash = db.get(User, 1).hashed_password
        payload = {
            "username": "alice", "email": "alice@example.com", "mobile_number": None,
            "first_name": "Alicia", "middle_name": None, "last_name": "Test",
            "date_of_birth": None, "role_id": 1, "account_status": "ACTIVE",
        }
        response = self.client.put('/users/1', headers=self.admin, json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        with TestSession() as db:
            self.assertEqual(db.get(User, 1).hashed_password, original_hash)
        self.assertEqual(self.client.put('/users/1', headers=self.admin, json={**payload, "password": "Replacement-123!"}).status_code, 422)

    def test_goal_ownership_and_validation(self):
        response = self.client.post('/customer/goals/', headers=self.alice, json={"name": "Emergency fund", "target_amount": "5000", "saved_amount": "100"})
        self.assertEqual(response.status_code, 201, response.text)
        goal_id = response.json()['id']
        self.assertEqual(self.client.get('/customer/goals/', headers=self.bob).json(), [])
        self.assertEqual(self.client.put(f'/customer/goals/{goal_id}', headers=self.bob, json={"name": "Bad", "target_amount": 100, "saved_amount": 0}).status_code, 404)
        self.assertEqual(self.client.post('/customer/goals/', headers=self.alice, json={"name": "Bad", "target_amount": -1, "saved_amount": 0}).status_code, 422)

    def test_request_approval_is_once_and_atomic(self):
        payload = {"account_id": 1, "kind": "WITHDRAWAL", "amount": "125.50"}
        request = self.client.post('/customer/requests/', headers=self.alice, json=payload)
        self.assertEqual(request.status_code, 201, request.text)
        url = f"/banking-requests/{request.json()['id']}/review"
        self.assertEqual(self.client.post(url, headers=self.alice, json={"status": "APPROVED"}).status_code, 403)
        response = self.client.post(url, headers=self.staff, json={"status": "APPROVED"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.client.post(url, headers=self.staff, json={"status": "APPROVED"}).status_code, 409)
        with TestSession() as db:
            self.assertEqual(db.get(Account, 1).available_balance, Decimal('874.50'))
        transactions = self.client.get('/customer/transactions/', headers=self.alice).json()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['reference'], request.json()['reference'])

    def test_requests_cannot_spend_other_accounts_or_overdraw(self):
        self.assertEqual(self.client.post('/customer/requests/', headers=self.alice, json={"account_id": 2, "kind": "DEPOSIT", "amount": 10}).status_code, 404)
        self.assertEqual(self.client.post('/customer/requests/', headers=self.alice, json={"account_id": 1, "kind": "WITHDRAWAL", "amount": 1001}).status_code, 400)

    def test_transfer_conserves_money_and_checks_ownership(self):
        payload = {"source_account_id": 1, "destination_account_number": "BEM0002", "amount": "120.25"}
        self.assertEqual(self.client.post('/customer/transfers/', headers=self.bob, json=payload).status_code, 404)
        response = self.client.post('/customer/transfers/', headers=self.alice, json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        with TestSession() as db:
            self.assertEqual(db.get(Account, 1).available_balance, Decimal('879.75'))
            self.assertEqual(db.get(Account, 2).available_balance, Decimal('1120.25'))

    def test_cards_ownership_pin_and_lost_state(self):
        response = self.client.post('/customer/cards/', headers=self.alice, json={"account_id": 1})
        self.assertEqual(response.status_code, 201, response.text)
        card_id = response.json()['id']
        url = f'/customer/cards/{card_id}'
        self.assertEqual(self.client.put(url, headers=self.bob, json={"status": "FROZEN", "spending_limit": 100}).status_code, 404)
        self.assertEqual(self.client.post(url + '/pin', headers=self.alice, json={"password": "test-password-123", "pin": "123456"}).status_code, 204)
        with TestSession() as db:
            self.assertTrue(check_password('123456', db.get(DemoCard, card_id).pin_hash))
        self.assertNotIn('pin_hash', self.client.get('/customer/cards/', headers=self.alice).json()[0])
        self.assertEqual(self.client.put(url, headers=self.alice, json={"status": "LOST", "spending_limit": 100}).status_code, 200)
        self.assertEqual(self.client.put(url, headers=self.alice, json={"status": "ACTIVE", "spending_limit": 100}).status_code, 409)

    def test_password_change_revokes_all_sessions(self):
        second = self.login('alice')
        response = self.client.post('/auth/password', headers=self.alice, json={"current_password": "test-password-123", "new_password": "New-test-password-456"})
        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(self.client.get('/auth/me', headers=second).status_code, 401)

    def test_sessions_hide_tokens_and_enforce_ownership(self):
        sessions = self.client.get('/auth/sessions', headers=self.alice).json()
        self.assertTrue(sessions[0]['current'])
        self.assertNotIn('jwt_token', sessions[0])
        url = f"/auth/sessions/{sessions[0]['id']}"
        self.assertEqual(self.client.delete(url, headers=self.bob).status_code, 404)
        self.assertEqual(self.client.delete(url, headers=self.alice).status_code, 204)
        self.assertEqual(self.client.get('/auth/me', headers=self.alice).status_code, 401)

    def test_deposit_approval_and_rejection(self):
        for decision in ('REJECTED', 'APPROVED'):
            response = self.client.post('/customer/requests/', headers=self.alice, json={"account_id": 1, "kind": "DEPOSIT", "amount": "250"})
            self.assertEqual(response.status_code, 201, response.text)
            review = self.client.post(f"/banking-requests/{response.json()['id']}/review", headers=self.staff, json={"status": decision})
            self.assertEqual(review.status_code, 200, review.text)
        with TestSession() as db:
            self.assertEqual(db.get(Account, 1).available_balance, Decimal('1250'))

    def test_recipients_are_private(self):
        response = self.client.post('/customer/recipients/', headers=self.alice, json={"name": "Bob", "account_number": "BEM0002"})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(self.client.get('/customer/recipients/', headers=self.bob).json(), [])
        self.assertEqual(self.client.delete(f"/customer/recipients/{response.json()['id']}", headers=self.bob).status_code, 404)

    def test_expired_session_is_rejected(self):
        from app.models.session import UserSession
        from datetime import datetime, timedelta
        with TestSession() as db:
            db.query(UserSession).filter(UserSession.user_id == 1).update({"expires_at": datetime.utcnow() - timedelta(minutes=1)})
            db.commit()
        self.assertEqual(self.client.get('/auth/me', headers=self.alice).status_code, 401)

    def test_account_approval_requires_admin_and_does_not_create_money(self):
        application = self.client.post('/customer/account-applications/', headers=self.alice, json={"account_type_id": 1})
        self.assertEqual(application.status_code, 201, application.text)
        self.assertEqual(self.client.get('/customer/account-applications/', headers=self.bob).json(), [])
        url = f"/account-applications/{application.json()['id']}/review"
        self.assertEqual(self.client.post(url, headers=self.staff, json={"status": "APPROVED"}).status_code, 403)
        admin = self.login('admin')
        result = self.client.post(url, headers=admin, json={"status": "APPROVED"})
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(self.client.post(url, headers=admin, json={"status": "APPROVED"}).status_code, 409)
        with TestSession() as db:
            account = db.query(Account).filter(Account.account_number == result.json()['account_number']).one()
            self.assertEqual(account.customer_id, 1)
            self.assertEqual(account.available_balance, Decimal('0'))

    def test_bills_investments_and_transactions(self):
        payment = self.client.post('/customer/bill-payments/', headers=self.alice, json={"account_id": 1, "biller_name": "Electricity", "biller_reference": "INV-101", "amount": "100.50"})
        self.assertEqual(payment.status_code, 201, payment.text)
        investment = self.client.post('/customer/investments/', headers=self.alice, json={"account_id": 1, "plan_code": "SHORT_TERM", "amount": "200"})
        self.assertEqual(investment.status_code, 201, investment.text)
        with TestSession() as db:
            self.assertEqual(db.get(Account, 1).available_balance, Decimal('699.50'))
            self.assertEqual(db.get(Account, 1).ledger_balance, Decimal('899.50'))
        url = f"/customer/investments/{investment.json()['id']}/redeem"
        self.assertEqual(self.client.post(url, headers=self.bob).status_code, 404)
        self.assertEqual(self.client.post(url, headers=self.alice).status_code, 200)
        self.assertEqual(self.client.post(url, headers=self.alice).status_code, 409)
        with TestSession() as db:
            self.assertEqual(db.get(Account, 1).available_balance, Decimal('899.50'))
        transactions = self.client.get('/customer/transactions/', headers=self.alice).json()
        self.assertEqual(len(transactions), 3)
        self.assertEqual(self.client.get('/customer/transactions/', headers=self.bob).json(), [])

    def test_money_precision_and_whitespace_validation(self):
        response = self.client.post('/customer/transfers/', headers=self.alice, json={"source_account_id": 1, "destination_account_number": "BEM0002", "amount": "0.001"})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.post('/customer/bill-payments/', headers=self.alice, json={"account_id": 1, "biller_name": "  ", "biller_reference": "INV-101", "amount": "1"}).status_code, 422)

    def test_alerts_read_state_and_ownership(self):
        self.client.post('/customer/requests/', headers=self.alice, json={"account_id": 1, "kind": "DEPOSIT", "amount": "25"})
        alerts = self.client.get('/customer/alerts/', headers=self.alice)
        self.assertEqual(alerts.status_code, 200, alerts.text)
        key = alerts.json()[0]['id']
        self.assertFalse(alerts.json()[0]['read'])
        self.assertEqual(self.client.post('/customer/alerts/read', headers=self.bob, json={"ids": [key]}).status_code, 400)
        self.assertEqual(self.client.post('/customer/alerts/read', headers=self.alice, json={"ids": [key]}).status_code, 204)
        self.assertTrue(self.client.get('/customer/alerts/', headers=self.alice).json()[0]['read'])
        self.assertEqual(self.client.post('/customer/alerts/read', headers=self.alice, json={"ids": [key]}).status_code, 204)

    def test_profile_update_cannot_change_role(self):
        response = self.client.put('/auth/profile', headers=self.alice, json={"first_name": "Alice", "last_name": "Updated", "email": "alice@example.com", "role_id": 3})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['role_code'], 'CUSTOMER')
        self.assertEqual(self.client.get('/auth/me', headers=self.alice).json()['last_name'], 'Updated')

    def test_all_customer_menu_read_endpoints(self):
        for path in ['/customer/accounts/', '/customer/cards/', '/customer/goals/', '/customer/alerts/', '/customer/requests/', '/auth/me', '/auth/sessions', '/auth/otp/status', '/customer/recipients/', '/customer/transfers/', '/customer/bill-payments/', '/customer/investments/', '/customer/transactions/']:
            response = self.client.get(path, headers=self.alice)
            self.assertEqual(response.status_code, 200, f'{path}: {response.text}')

    def test_mobile_load_is_once_and_in_statements_and_alerts(self):
        from datetime import date
        payload = {'account_id': 1, 'network': 'Globe', 'mobile_number': '09171234567', 'amount': '100.00', 'request_key': 'a' * 32}
        first = self.client.post('/customer/mobile-load/', headers=self.alice, json=payload)
        self.assertEqual(first.status_code, 201, first.text)
        repeat = self.client.post('/customer/mobile-load/', headers=self.alice, json=payload)
        self.assertEqual(repeat.status_code, 201, repeat.text)
        self.assertEqual(first.json()['id'], repeat.json()['id'])
        self.assertEqual(self.client.post('/customer/mobile-load/', headers=self.alice, json={**payload, 'amount': 200}).status_code, 409)
        with TestSession() as db:
            self.assertEqual(db.get(Account, 1).available_balance, Decimal('900'))
            self.assertEqual(db.get(Account, 1).ledger_balance, Decimal('900'))
        self.assertEqual(self.client.get('/customer/mobile-load/', headers=self.bob).json(), [])
        history = self.client.get('/customer/transactions/', headers=self.alice).json()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['transaction_type'], 'MOBILE LOAD')
        alerts = self.client.get('/customer/alerts/', headers=self.alice).json()
        self.assertEqual(alerts[0]['reference'], first.json()['reference'])
        today = date.today().isoformat()
        statement = self.client.get(f'/reports/accounts/1/statement?start={today}&end={today}', headers=self.alice)
        self.assertEqual(statement.status_code, 200, statement.text)
        self.assertEqual(Decimal(statement.json()['closing_balance']), Decimal('900'))
        self.assertEqual(Decimal(statement.json()['total_debits']), Decimal('100'))

    def test_mobile_load_permissions_validation_and_balance(self):
        payload = {'account_id': 1, 'network': 'Smart', 'mobile_number': '09171234567', 'amount': 100, 'request_key': 'b' * 32}
        for changes, expected in [({'account_id': 2},404), ({'amount': 26},400), ({'mobile_number': '123'},422), ({'network': 'Other'},422)]:
            response = self.client.post('/customer/mobile-load/', headers=self.alice, json={**payload, **changes})
            self.assertEqual(response.status_code, expected, response.text)
        self.assertEqual(self.client.post('/customer/mobile-load/', headers=self.staff, json=payload).status_code, 403)
        self.assertEqual(self.client.post('/customer/mobile-load/', json=payload).status_code, 401)
        with TestSession() as db:
            db.get(Account, 1).available_balance = 50
            db.commit()
        self.assertEqual(self.client.post('/customer/mobile-load/', headers=self.alice, json=payload).status_code, 400)
        self.assertEqual(self.client.get('/customer/mobile-load/', headers=self.alice).json(), [])

    def test_recipient_verification_and_recent_ownership(self):
        response = self.client.post('/customer/recipient-lookup', headers=self.alice, json={'account_number': 'BEM0002'})
        self.assertEqual(response.json(), {'account_number': 'BEM0002', 'name': 'bob Test'})
        self.assertEqual(self.client.post('/customer/recipient-lookup', headers=self.alice, json={'account_number': 'missing'}).status_code, 404)
        self.assertEqual(self.client.get('/customer/recent-recipients/', headers=self.alice).json(), [])
        for _ in range(2):
            response = self.client.post('/customer/transfers/', headers=self.alice, json={'source_account_id': 1, 'destination_account_number': 'BEM0002', 'amount': '10.00'})
            self.assertEqual(response.status_code, 201, response.text)
        recent = self.client.get('/customer/recent-recipients/', headers=self.alice).json()
        self.assertEqual(recent, [{'account_number': 'BEM0002', 'name': 'bob Test'}])
        self.assertEqual(self.client.get('/customer/recent-recipients/', headers=self.bob).json(), [])
        with TestSession() as db:
            db.get(Account, 2).status = 'CLOSED'; db.commit()
        self.assertEqual(self.client.get('/customer/recent-recipients/', headers=self.alice).json(), [])
        self.assertEqual(self.client.post('/customer/recipient-lookup', headers=self.alice, json={'account_number': 'BEM0002'}).status_code, 404)

    def test_support_request_ownership_and_staff_resolution(self):
        response = self.client.post('/support/tickets/', headers=self.alice, json={'subject': 'QR help', 'message': 'Please explain how to receive funds.'})
        self.assertEqual(response.status_code, 201, response.text)
        ticket_id = response.json()['id']
        self.assertEqual(self.client.get('/support/tickets/', headers=self.bob).json(), [])
        self.assertEqual(len(self.client.get('/support/tickets/', headers=self.staff).json()), 1)
        url = f'/support/tickets/{ticket_id}/resolve'
        self.assertEqual(self.client.post(url, headers=self.alice, json={'reply': 'Denied'}).status_code, 403)
        self.assertEqual(self.client.post(url, headers=self.staff, json={'reply': '   '}).status_code, 422)
        self.assertEqual(self.client.post(url, headers=self.staff, json={'reply': 'Open My account and choose Receive.'}).status_code, 200)
        self.assertEqual(self.client.post(url, headers=self.staff, json={'reply': 'Duplicate'}).status_code, 409)
        own = self.client.get('/support/tickets/', headers=self.alice).json()[0]
        self.assertEqual(own['status'], 'RESOLVED')
        self.assertEqual(own['reply'], 'Open My account and choose Receive.')

    def test_staff_password_recovery_revokes_sessions_but_keeps_otp(self):
        from datetime import datetime, timedelta
        from app.models.otp import OtpCredential, OtpChallenge
        payload = {'staff_password': 'test-password-123', 'new_password': 'Customer-Reset-42!', 'identity_confirmed': True}
        url = '/staff/customer-access/1/password'
        self.assertEqual(self.client.get('/staff/customer-access/', headers=self.alice).status_code, 403)
        self.assertEqual(self.client.post(url, headers=self.alice, json=payload).status_code, 403)
        self.assertEqual(self.client.post(url, headers=self.staff, json={**payload, 'identity_confirmed': False}).status_code, 422)
        self.assertEqual(self.client.post(url, headers=self.staff, json={**payload, 'new_password': 'weak'}).status_code, 422)
        self.assertEqual(self.client.post(url, headers=self.staff, json={**payload, 'staff_password': 'wrong'}).status_code, 400)
        self.assertEqual(self.client.post('/staff/customer-access/3/password', headers=self.staff, json=payload).status_code, 404)
        with TestSession() as db:
            db.add(OtpCredential(user_id=1, enabled=True, encrypted_secret='unchanged-secret'))
            db.add(OtpChallenge(token_hash='a'*64, user_id=1, expires_at=datetime.utcnow()+timedelta(minutes=5)))
            db.commit()
        response = self.client.post(url, headers=self.staff, json=payload)
        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(self.client.get('/auth/me', headers=self.alice).status_code, 401)
        self.assertEqual(self.client.get('/auth/me', headers=self.staff).status_code, 200)
        with TestSession() as db:
            self.assertTrue(check_password(payload['new_password'], db.get(User, 1).hashed_password))
            self.assertTrue(db.get(OtpCredential, 1).enabled)
            self.assertEqual(db.get(OtpCredential, 1).encrypted_secret, 'unchanged-secret')
            self.assertIsNotNone(db.get(OtpChallenge, 'a'*64).used_at)

    def test_login_accepts_registered_email_and_preserves_otp(self):
        from app.models.otp import OtpCredential
        with TestSession() as db:
            db.get(User, 1).email = 'alice@example.com'
            db.commit()
        response = self.client.post('/auth/login', data={'username': 'ALICE@example.com', 'password': 'test-password-123'})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()['pin_required'])
        self.assertNotIn('access_token', response.json())
        with TestSession() as db:
            db.add(OtpCredential(user_id=1, enabled=True, encrypted_secret='unchanged-secret'))
            db.commit()
        response = self.client.post('/auth/login', data={'username': 'alice@example.com', 'password': 'test-password-123'})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()['otp_required'])
        self.assertNotIn('access_token', response.json())


if __name__ == '__main__':
    unittest.main()
