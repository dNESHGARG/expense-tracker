import sqlite3
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from expense_tracker.core import Transaction
from expense_tracker.storage import connect, fingerprint, import_transactions, list_transactions


def transaction(account='default', external_id='tx-1'):
    return Transaction(date(2026, 10, 1), 'Coffee', Decimal('5'), 'Food', external_id, account)


class AccountIdentityTests(unittest.TestCase):
    def test_same_external_id_different_accounts(self):
        with connect(':memory:') as db:
            self.assertEqual(import_transactions(db, [transaction('checking'), transaction('credit')]), 2)
            self.assertEqual(import_transactions(db, [transaction('checking')]), 0)
            self.assertEqual({t.account_id for t in list_transactions(db)}, {'checking', 'credit'})

    def test_no_id_content_fallback_scoped_to_account(self):
        with connect(':memory:') as db:
            self.assertEqual(import_transactions(db, [transaction('a', None), transaction('b', None)]), 2)
            self.assertEqual(import_transactions(db, [transaction('a', None)]), 0)

    def test_migrates_legacy_data_without_changing_fingerprint(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'expenses.db'
            legacy = transaction(external_id=None)
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE transactions (fingerprint TEXT PRIMARY KEY, date TEXT NOT NULL, '
                           'description TEXT NOT NULL, amount TEXT NOT NULL, category TEXT NOT NULL)')
                db.execute('INSERT INTO transactions VALUES (?, ?, ?, ?, ?)',
                           (fingerprint(legacy), '2026-10-01', 'Coffee', '5', 'Food'))
            with connect(path) as db:
                self.assertEqual(import_transactions(db, [legacy]), 0)
                self.assertEqual(list_transactions(db), [legacy])

    def test_migrates_previous_transaction_id_schema(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'expenses.db'
            old = transaction()
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE transactions (fingerprint TEXT PRIMARY KEY, date TEXT NOT NULL, '
                           'description TEXT NOT NULL, amount TEXT NOT NULL, category TEXT NOT NULL, '
                           'transaction_id TEXT)')
                db.execute('INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?)',
                           (fingerprint(old), '2026-10-01', 'Coffee', '5', 'Food', 'tx-1'))
            with connect(path) as db:
                self.assertEqual(import_transactions(db, [old]), 0)
                self.assertEqual(list_transactions(db), [old])

    def test_named_account_persists(self):
        from expense_tracker.storage import create_account, list_accounts
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'accounts.db'
            with connect(path) as db:
                create_account(db, 'checking', 'Checking', 'Example Bank')
            with connect(path) as db:
                self.assertIn(('checking', 'Checking', 'Example Bank'), list_accounts(db))

    def test_duplicate_account_rejected(self):
        from expense_tracker.storage import create_account
        with connect(':memory:') as db:
            create_account(db, 'checking', 'Checking')
            with self.assertRaises(sqlite3.IntegrityError):
                create_account(db, 'checking', 'Duplicate')

    def test_blank_account_rejected(self):
        from expense_tracker.storage import create_account
        with connect(':memory:') as db:
            with self.assertRaises(ValueError):
                create_account(db, '', 'Missing ID')
