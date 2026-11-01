from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import csv
from pathlib import Path


@dataclass(frozen=True)
class Transaction:
    date: date
    description: str
    amount: Decimal
    category: str
    transaction_id: str | None = None
    account_id: str = 'default'


def load_transactions(path: str | Path) -> list[Transaction]:
    """Read date, description, amount, category from a UTF-8 CSV file.

    Positive amounts represent expenses; negative amounts represent refunds.
    """
    transactions = []
    with Path(path).open(newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        aliases = {'date': ('date', 'transaction date', 'posted date'),
                   'description': ('description', 'details', 'merchant', 'memo'),
                   'amount': ('amount', 'transaction amount'),
                   'debit': ('debit', 'withdrawal'), 'credit': ('credit', 'deposit'),
                   'category': ('category',)}
        headers = {h.strip().lower(): h for h in (reader.fieldnames or []) if h}
        columns = {k: next((headers[a] for a in names if a in headers), None)
                   for k, names in aliases.items()}
        required = {'date', 'description'}
        if not all(columns[k] for k in required) or not (columns['amount'] or columns['debit'] or columns['credit']):
            raise ValueError(f'CSV must contain columns: {", ".join(sorted(required))}')
        for line, row in enumerate(reader, start=2):
            try:
                def field(key):
                    return (row.get(columns[key]) or '').strip() if columns[key] else ''
                def money(value):
                    value = value.replace('
                if not amount.is_finite():
                    raise ValueError('Amount must be finite')
                transaction = Transaction(
                    date=parsed_date,
                    description=field('description'),
                    amount=amount,
                    category=field('category') or 'Uncategorized',
                    transaction_id=(row.get('transaction_id') or '').strip() or None,
                    account_id=(row.get('account_id') or 'default').strip() or 'default',
                )
            except (ValueError, TypeError, InvalidOperation, AttributeError) as exc:
                raise ValueError(f'Invalid transaction on CSV line {line}: {exc}') from exc
            transactions.append(transaction)
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
, '').replace(',', '')
                    if value.startswith('(') and value.endswith(')'):
                        value = '-' + value[1:-1]
                    return Decimal(value or '0')
                amount = money(field('amount')) if columns['amount'] else (
                    money(field('debit')) - money(field('credit')))
                day = field('date')
                parsed_date = None
                for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'):
                    try:
                        parsed_date = datetime.strptime(day, fmt).date()
                        break
                    except ValueError:
                        pass
                if parsed_date is None:
                    raise ValueError('Unsupported date format')
                if not amount.is_finite():
                    raise ValueError('Amount must be finite')
                transaction = Transaction(
                    date=date.fromisoformat(row['date']),
                    description=row['description'].strip(),
                    amount=amount,
                    category=row['category'].strip() or 'Uncategorized',
                    transaction_id=(row.get('transaction_id') or '').strip() or None,
                    account_id=(row.get('account_id') or 'default').strip() or 'default',
                )
            except (ValueError, TypeError, InvalidOperation, AttributeError) as exc:
                raise ValueError(f'Invalid transaction on CSV line {line}: {exc}') from exc
            transactions.append(transaction)
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
