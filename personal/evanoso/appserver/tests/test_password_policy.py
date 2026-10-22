import unittest
from pydantic import ValidationError
import test_bembank as banking
from app.core.password_policy import validate_password
from app.routers.project_features import Registration
from app.schemas.user import UserCreate
from app.routers.auth import PasswordChange

class PasswordPolicyTests(unittest.TestCase):
    def test_each_requirement_and_byte_limit(self):
        for value in ['Short1!', 'lowercaseonly1!', 'UPPERCASEONLY1!', 'MissingDigits!', 'MissingSymbols123', 'A1!'+'a'*70, 'A1!'+'é'*35]:
            with self.subTest(value=value), self.assertRaises(ValueError):validate_password(value)
        for value in ['Long-Unique-Password42!', 'A1!'+('a'*69), '  Long-Password42!  ']:
            self.assertEqual(validate_password(value),value)

    def test_all_write_schemas_enforce_policy_without_trimming(self):
        models=[(Registration,dict(username='customer',first_name='First',last_name='Last',email='first@example.com',account_type_id=1),'password'),(UserCreate,dict(username='customer',first_name='First',last_name='Last',role_id=1),'password'),(PasswordChange,dict(current_password='old'),'new_password')]
        for model,fields,key in models:
            with self.subTest(model=model.__name__):
                with self.assertRaises(ValidationError):model(**fields,**{key:'weakpassword123'})
                value='  Long-Password42!  '
                self.assertEqual(getattr(model(**fields,**{key:value}),key),value)

class PasswordEndpointTests(unittest.TestCase):
    setUp=banking.BankingTests.setUp
    login=banking.BankingTests.login
    def test_weak_write_rejected_and_legacy_login_preserved(self):
        payload=dict(username='weakuser',password='weakpassword123',first_name='First',last_name='Last',email='weak@example.com',account_type_id=1)
        self.assertEqual(self.client.post('/staff/customers/',headers=self.staff,json=payload).status_code,422)
        self.assertEqual(self.client.post('/auth/password',headers=self.alice,json={'current_password':'test-password-123','new_password':'weakpassword123'}).status_code,422)
        self.assertEqual(self.client.get('/auth/me',headers=self.alice).status_code,200)
