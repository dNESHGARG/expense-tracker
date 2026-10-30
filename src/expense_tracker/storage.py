"""SQLite persistence with account-scoped transaction identity."""
from __future__ import annotations

from contextlib import contextmanager
from decimal import Decimal
import hashlib
from pathlib import Path
import sqlite3
from typing import Iterator

from .core import Transaction

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    fingerprint TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    amount TEXT NOT NULL,
    category TEXT NOT NULL,
    transaction_id TEXT,
    account_id TEXT NOT NULL DEFAULT 'default'
);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
"""


def fingerprint(tx: Transaction) -> str:
    """Identity based on account and external ID, or content fallback.

    The default account retains historical fingerprints for legacy imports.
    """
    if tx.transaction_id:
        fields = ('bank-id', tx.transaction_id) if tx.account_id == 'default' else (
            'bank-id', tx.account_id, tx.transaction_id)
    else:
        content = (tx.date.isoformat(), tx.description, str(tx.amount.normalize()), tx.category)
        fields = content if tx.account_id == 'default' else ('content', tx.account_id, *content)
    return hashlib.sha256('\x1f'.join(fields).encode('utf-8')).hexdigest()


@contextmanager
def connect(path: str | Path) -> Iterator[sqlite3.Connection]:
    db = sqlite3.connect(str(path))
    try:
        db.executescript(SCHEMA)
        columns = {row[1] for row in db.execute('PRAGMA table_info(transactions)')}
        if 'transaction_id' not in columns:
            db.execute('ALTER TABLE transactions ADD COLUMN transaction_id TEXT')
        if 'account_id' not in columns:
            db.execute("ALTER TABLE transactions ADD COLUMN account_id TEXT NOT NULL DEFAULT 'default'")
        db.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_account_transaction_id '
                   'ON transactions(account_id, transaction_id) WHERE transaction_id IS NOT NULL')
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()


def import_transactions(db: sqlite3.Connection, transactions: list[Transaction]) -> int:
    """Insert new transactions atomically; return inserted row count."""
    before = db.total_changes
    with db:
        db.executemany(
            'INSERT OR IGNORE INTO transactions '
            '(fingerprint, date, description, amount, category, transaction_id, account_id) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            [(fingerprint(t), t.date.isoformat(), t.description, str(t.amount), t.category,
              t.transaction_id, t.account_id) for t in transactions],
        )
    return db.total_changes - before


def list_transactions(db: sqlite3.Connection) -> list[Transaction]:
    from datetime import date
    return [Transaction(date.fromisoformat(day), description, Decimal(amount), category,
                        transaction_id, account_id)
            for day, description, amount, category, transaction_id, account_id in db.execute(
                'SELECT date, description, amount, category, transaction_id, account_id '
                'FROM transactions ORDER BY date, fingerprint'
            )]
