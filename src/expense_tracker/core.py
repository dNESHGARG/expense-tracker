from collections import defaultdict
from dataclasses import dataclass
from datetime import date
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
        required = {'date', 'description', 'amount', 'category'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f'CSV must contain columns: {", ".join(sorted(required))}')
        for line, row in enumerate(reader, start=2):
            try:
                amount = Decimal(row['amount'])
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
