import csv
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from expense_tracker.core import Transaction, load_transactions
from expense_tracker.storage import connect, import_transactions, list_transactions


class TransactionIDTests(unittest.TestCase):
    def test_identical_purchases_with_distinct_bank_ids_are_preserved(self):
        first = Transaction(date(2026, 10, 1), "Coffee", Decimal("5"), "Food", "bank-1")
        second = Transaction(date(2026, 10, 1), "Coffee", Decimal("5"), "Food", "bank-2")
        with connect(":memory:") as db:
            self.assertEqual(import_transactions(db, [first, second]), 2)
            self.assertEqual(import_transactions(db, [first, second]), 0)
            self.assertEqual(len(list_transactions(db)), 2)

    def test_csv_optional_transaction_id(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bank.csv"
            with path.open("w", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["date", "description", "amount", "category", "transaction_id"])
                writer.writerow(["2026-10-01", "Coffee", "5.00", "Food", "bank-1"])
            self.assertEqual(load_transactions(path)[0].transaction_id, "bank-1")

    def test_legacy_database_migration(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "legacy.db"
            with sqlite3.connect(path) as db:
                db.execute("CREATE TABLE transactions (fingerprint TEXT PRIMARY KEY, date TEXT NOT NULL, description TEXT NOT NULL, amount TEXT NOT NULL, category TEXT NOT NULL)")
            with connect(path) as db:
                tx = Transaction(date(2026, 10, 1), "Coffee", Decimal("5"), "Food", "bank-1")
                self.assertEqual(import_transactions(db, [tx]), 1)
                self.assertEqual(list_transactions(db), [tx])


if __name__ == "__main__":
    unittest.main()
