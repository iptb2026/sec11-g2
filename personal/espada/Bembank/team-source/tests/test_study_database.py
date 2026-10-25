import os
import unittest
from unittest.mock import patch

from sqlalchemy import BigInteger, create_engine, text
from sqlalchemy.schema import Column, MetaData, Table

from app.core.config import settings
from app.database import session


class StudyDatabaseTests(unittest.TestCase):
    def test_separate_sqlite_default_and_override(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(settings.DATABASE_URL.endswith('/bembank-demo.sqlite3'))
        with patch.dict(os.environ, {'BEMBANK_DATABASE_URL': 'sqlite:///:memory:'}):
            self.assertEqual(settings.DATABASE_URL, 'sqlite:///:memory:')

    def test_sqlite_bigint_id_autoincrements(self):
        engine = create_engine('sqlite://')
        metadata = MetaData()
        rows = Table('rows', metadata, Column('id', BigInteger, primary_key=True))
        metadata.create_all(engine)
        with engine.begin() as connection:
            connection.execute(rows.insert().values())
            self.assertEqual(connection.execute(text('SELECT id FROM rows')).scalar_one(), 1)


if __name__ == '__main__':
    unittest.main()
