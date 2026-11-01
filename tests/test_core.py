import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path
from expense_tracker.core import Transaction, category_totals, load_transactions


class ExpenseTrackerTests(unittest.TestCase):
    def test_csv_load_and_monthly_totals(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'transactions.csv'
            path.write_text('date,description,amount,category\n2026-10-01,Coffee,4.50,Food\n2026-09-30,Train,10.00,Travel\n', encoding='utf-8')
            transactions = load_transactions(path)
            self.assertEqual(len(transactions), 2)
            self.assertEqual(category_totals(transactions, '2026-10'), {'Food': Decimal('4.50')})

    def test_refund_reduces_spend(self):
        transactions = [Transaction(date(2026, 10, 1), 'Purchase', Decimal('30'), 'Food'), Transaction(date(2026, 10, 2), 'Refund', Decimal('-5'), 'Food')]
        self.assertEqual(category_totals(transactions)['Food'], Decimal('25'))

    def test_invalid_month(self):
        with self.assertRaises(ValueError):
            category_totals([], '2026-13')

    def test_invalid_csv_amount(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.csv'
            path.write_text('date,description,amount,category\n2026-10-01,Coffee,NaN,Food\n')
            with self.assertRaisesRegex(ValueError, 'line 2'):
                load_transactions(path)

    def test_bank_debit_credit_import(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'statement.csv'
            path.write_text('Posted Date,Details,Debit,Credit' + chr(10) +
                            '10/01/2026,Coffee,5.25,' + chr(10) +
                            '10/02/2026,Refund,,2.00' + chr(10))
            rows = load_transactions(path)
            self.assertEqual([row.amount for row in rows],
                             [Decimal('5.25'), Decimal('-2.00')])
            self.assertEqual(rows[0].category, 'Uncategorized')

    def test_single_amount_sign_convention(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'statement.csv'
            path.write_text('Transaction Date,Merchant,Amount' + chr(10) +
                            '10/01/2026,Coffee,-5.25' + chr(10))
            self.assertEqual(load_transactions(path)[0].amount, Decimal('-5.25'))
            self.assertEqual(load_transactions(path, 'expense-negative')[0].amount,
                             Decimal('5.25'))

    def test_invalid_bank_date_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.csv'
            path.write_text('Posted Date,Merchant,Amount' + chr(10) +
                            'invalid,Coffee,5' + chr(10))
            with self.assertRaisesRegex(ValueError, 'line 2'):
                load_transactions(path)


if __name__ == '__main__':
    unittest.main()
