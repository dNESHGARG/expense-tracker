import sqlite3
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path
from expense_tracker.core import Transaction, category_totals
from expense_tracker.storage import connect, fingerprint, import_transactions, list_transactions


def tx(amount='10.25', description='Coffee'):
    return Transaction(date(2026, 10, 1), description, Decimal(amount), 'Food')


class StorageTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            with connect(Path(folder) / 'expenses.db') as db:
                self.assertEqual(import_transactions(db, [tx()]), 1)
                self.assertEqual(list_transactions(db), [tx()])

    def test_import_twice_does_not_duplicate(self):
        with connect(':memory:') as db:
            self.assertEqual(import_transactions(db, [tx(), tx()]), 1)
            self.assertEqual(import_transactions(db, [tx()]), 0)
            self.assertEqual(len(list_transactions(db)), 1)

    def test_different_amounts_are_distinct(self):
        with connect(':memory:') as db:
            self.assertEqual(import_transactions(db, [tx('10'), tx('11')]), 2)
            self.assertEqual(category_totals(list_transactions(db))['Food'], Decimal('21'))

    def test_fingerprint_normalizes_decimal_representation(self):
        self.assertEqual(fingerprint(tx('10.0')), fingerprint(tx('10.00')))

    def test_database_persists_between_connections(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'expenses.db'
            with connect(path) as db:
                import_transactions(db, [tx()])
            with connect(path) as db:
                self.assertEqual(list_transactions(db), [tx()])

    def test_transaction_rolls_back_on_failure(self):
        with connect(':memory:') as db:
            with self.assertRaises(sqlite3.IntegrityError):
                with db:
                    db.execute("INSERT INTO transactions VALUES ('one', '2026-10-01', 'a', '1', 'Food')")
                    db.execute("INSERT INTO transactions VALUES ('two', NULL, 'b', '2', 'Food')")
            self.assertEqual(list_transactions(db), [])


if __name__ == '__main__':
    unittest.main()
