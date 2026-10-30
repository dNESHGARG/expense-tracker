# Expense Tracker

A dependency-free Python CLI for importing and summarizing transaction exports. Uses `Decimal` for currency and SQLite for persistence.

## Requirements

Python 3.10 or later.

## Usage

Summarize CSV directly:

```bash
PYTHONPATH=src python -m expense_tracker examples/transactions.csv --month 2026-10
```

Import transactions into SQLite and summarize:

```bash
PYTHONPATH=src python -m expense_tracker examples/transactions.csv --db expenses.db --month 2026-10
```

Run the same command again: the import reports zero new transactions. Query previously imported transactions without another CSV:

```bash
PYTHONPATH=src python -m expense_tracker --db expenses.db
```

Positive amounts represent expenses; negative amounts represent refunds. Required CSV columns: `date,description,amount,category`. Optional: `transaction_id` (a stable ID from the financial institution) and `account_id` (a stable, non-sensitive identifier for the account). If omitted, `account_id` defaults to `default` for backward compatibility.

## Duplicate policy

When `transaction_id` is present, imports deduplicate by the pair `(account_id, transaction_id)`, allowing different accounts to use the same external ID. Without a transaction ID, the content fingerprint is scoped to the account; genuinely identical purchases in one account may still collapse. Existing databases migrate automatically and legacy records remain assigned to `default`. Use a stable, non-sensitive account ID, not a bank account number. A future release should introduce explicit account management and import-source tracking.

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

GitHub Actions runs unit tests on Python 3.10, 3.12 and 3.13.

## Roadmap

- v0.1: CSV import and monthly category summaries
- v0.2: SQLite persistence, idempotent imports, CI
- v0.3 (in progress): Account-scoped transaction IDs and database migration; next: explicit account management, configurable categorization, CSV export
- v0.4: Web API and reporting

## Multi-account CSV example

```csv
date,description,amount,category,transaction_id,account_id
2026-10-01,Coffee,5.00,Food,tx-1,checking
2026-10-01,Coffee,5.00,Food,tx-1,credit-card
```

Both rows are valid: the external transaction ID is unique within each account, not globally.
