import unittest
import test_bembank as banking
from app.core.project_defaults import ensure_project_defaults
from app.models.user import User
from app.models.account import Account
from app.models.role import Role

class SignupTests(unittest.TestCase):
    setUp = banking.BankingTests.setUp
    login = banking.BankingTests.login

    def payload(self):
        with banking.TestSession() as db:
            ensure_project_defaults(db)
        return dict(username='newuser', first_name='New', last_name='User', email='new@example.com', password='New-Password123!')

    def test_public_signup_and_password_pin_login(self):
        data = self.payload()
        result = self.client.post('/auth/signup', json=data)
        self.assertEqual(result.status_code, 201, result.text)
        with banking.TestSession() as db:
            user = db.get(User, result.json()['customer_id'])
            self.assertEqual(db.get(Role, user.role_id).role_code, 'CUSTOMER')
            self.assertNotEqual(user.hashed_password, data['password'])
            account = db.get(Account, result.json()['account_id'])
            self.assertEqual(account.customer_id, user.id)
            self.assertEqual(account.available_balance, 0)
        result = self.client.post('/auth/login', data={'username': data['username'], 'password': data['password']})
        self.assertTrue(result.json()['pin_setup_required'])
        result = self.client.post('/auth/pin/verify', json={'challenge_token': result.json()['challenge_token'], 'pin': '012345', 'confirm_pin': '012345'})
        self.assertEqual(result.status_code, 200, result.text)
        headers = {'Authorization': 'Bearer ' + result.json()['access_token']}
        self.assertEqual(self.client.get('/auth/me', headers=headers).json()['role_code'], 'CUSTOMER')
        self.assertEqual(len(self.client.get('/customer/accounts/', headers=headers).json()), 1)
        self.assertEqual(self.client.get('/users/', headers=headers).status_code, 403)

    def test_validation_duplicates_and_privilege_escalation(self):
        data = self.payload()
        for extra in [{'role_id': 3}, {'account_type_id': 1}, {'account_status': 'ACTIVE'}, {'password': 'weak'}, {'email': 'bad'}]:
            self.assertEqual(self.client.post('/auth/signup', json={**data, **extra}).status_code, 422)
        self.assertEqual(self.client.post('/auth/signup', json=data).status_code, 201)
        self.assertEqual(self.client.post('/auth/signup', json={**data, 'username': 'NEWUSER', 'email': 'other@example.com'}).status_code, 409)
        self.assertEqual(self.client.post('/auth/signup', json={**data, 'username': 'otheruser', 'email': 'NEW@example.com'}).status_code, 409)

    def test_registration_is_rate_limited(self):
        data = self.payload()
        for i in range(10):
            response = self.client.post('/auth/signup', json=data)
            self.assertEqual(response.status_code, 201 if i == 0 else 409)
        self.assertEqual(self.client.post('/auth/signup', json=data).status_code, 429)
