"""Local CSV parsing and expense summaries."""
import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


@dataclass(frozen=True)
class Transaction:
    date: date
    description: str
    amount: Decimal
    category: str
    transaction_id: str | None = None
    account_id: str = 'default'


def load_transactions(path: str | Path, amount_sign: str = 'expense-positive') -> list[Transaction]:
    """Read normalized or bank-export CSV. Positive values always mean expenses.

    A single Amount column requires an explicit sign convention for bank exports.
    Separate Debit/Credit columns use debit-positive, credit-negative.
    """
    if amount_sign not in ('expense-positive', 'expense-negative'):
        raise ValueError('amount_sign must be expense-positive or expense-negative')
    aliases = {
        'date': ('date', 'transaction date', 'posted date', 'posting date'),
        'description': ('description', 'details', 'merchant', 'memo', 'payee'),
        'amount': ('amount', 'transaction amount'),
        'debit': ('debit', 'withdrawal', 'withdrawals'),
        'credit': ('credit', 'deposit', 'deposits'),
        'category': ('category',),
        'transaction_id': ('transaction_id', 'transaction id', 'reference number'),
        'account_id': ('account_id',),
    }
    transactions = []
    with Path(path).open(newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        headers = {h.strip().lower(): h for h in (reader.fieldnames or []) if h}
        columns = {key: next((headers[name] for name in names if name in headers), None)
                   for key, names in aliases.items()}
        if not columns['date'] or not columns['description'] or not (
                columns['amount'] or columns['debit'] or columns['credit']):
            raise ValueError('CSV requires date, description, and amount or debit/credit columns')

        for line, row in enumerate(reader, start=2):
            try:
                if None in row:
                    raise ValueError('Unexpected extra columns')
                def field(key):
                    return (row.get(columns[key]) or '').strip() if columns[key] else ''
                def money(value):
                    value = value.replace('$', '').replace(',', '')
                    if value.startswith('(') and value.endswith(')'):
                        value = '-' + value[1:-1]
                    number = Decimal(value or '0')
                    if not number.is_finite():
                        raise ValueError('Amount must be finite')
                    return number

                if columns['amount']:
                    amount = money(field('amount'))
                    if amount_sign == 'expense-negative':
                        amount = -amount
                else:
                    amount = money(field('debit')) - money(field('credit'))

                day = field('date')
                parsed_date = None
                for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'):
                    try:
                        parsed_date = datetime.strptime(day, fmt).date()
                        break
                    except ValueError:
                        continue
                if parsed_date is None:
                    raise ValueError('Unsupported date format')
                transactions.append(Transaction(
                    date=parsed_date,
                    description=field('description'),
                    amount=amount,
                    category=field('category') or 'Uncategorized',
                    transaction_id=field('transaction_id') or None,
                    account_id=field('account_id') or 'default',
                ))
            except (ValueError, TypeError, InvalidOperation, AttributeError) as exc:
                raise ValueError(f'Invalid transaction on CSV line {line}: {exc}') from exc
    return transactions


def category_totals(transactions: list[Transaction], month: str | None = None) -> dict[str, Decimal]:
    if month is not None:
        try:
            year, number = map(int, month.split('-'))
            date(year, number, 1)
            if month != f'{year:04d}-{number:02d}':
                raise ValueError
        except (ValueError, TypeError) as exc:
            raise ValueError('Month must use YYYY-MM format') from exc
    totals = defaultdict(lambda: Decimal('0'))
    for transaction in transactions:
        if month is None or transaction.date.strftime('%Y-%m') == month:
            totals[transaction.category] += transaction.amount
    return dict(sorted(totals.items()))
