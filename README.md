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

Positive amounts represent expenses; negative amounts represent refunds. Required CSV columns: `date,description,amount,category`.

## Duplicate policy

Imports are idempotent by hashing date, description, normalized amount and category. **Tradeoff:** two genuinely separate purchases with identical fields are treated as duplicates. A later version should support an optional bank-provided transaction ID to distinguish them.

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

GitHub Actions runs unit tests on Python 3.10, 3.12 and 3.13.

## Roadmap

- v0.1: CSV import and monthly category summaries
- v0.2: SQLite persistence, idempotent imports, CI
- v0.3: Bank transaction IDs, configurable categorization, CSV export
- v0.4: Web API and reporting
