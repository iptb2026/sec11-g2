from datetime import datetime, timezone
from unittest import TestCase

from jose import jwt

from app.core.config import settings
from app.core.security import create_token


class TokenTest(TestCase):
    def test_token_has_future_expiry(self):
        token = create_token("espada")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        self.assertEqual(payload["sub"], "espada")
        self.assertGreater(payload["exp"], datetime.now(timezone.utc).timestamp())
