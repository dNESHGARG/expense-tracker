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

## Manage accounts

Create an account once, using a non-sensitive ID:

```bash
PYTHONPATH=src python -m expense_tracker --db expenses.db --add-account checking --name "Everyday Checking" --institution "Example Bank"
PYTHONPATH=src python -m expense_tracker --db expenses.db --list-accounts
```

Import a statement into that account (even when the CSV has no `account_id` column):

```bash
PYTHONPATH=src python -m expense_tracker statement.csv --db expenses.db --account checking
```

Reimporting the same statement does not duplicate its transactions. Account IDs must be unique. The `default` account is reserved for legacy and unspecified imports. Currently, CSV files must already have the required normalized columns and categories.

## Bank CSV preview

Check the sign convention against a known purchase and refund before importing.
For banks that export purchases as negative amounts, run:

```bash
PYTHONPATH=src python -m expense_tracker statement.csv --preview --amount-sign expense-negative
```

Use `expense-positive` (the default) when purchases are positive. The preview
prints up to ten rows without saving. The importer also accepts common date,
description, debit and credit column names. With separate debit and credit
columns, it calculates debit minus credit. Check that convention against your
statement before importing.

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

## Planned milestone: Local data security and import hardening

**Status: Backlog — not implemented or security-certified.** Complete before accepting untrusted files or distributing the application to other users.

1. **Database confidentiality:** SQLite is not encrypted by default. Evaluate encryption at rest, database access permissions, and key management. macOS FileVault helps protect the device but does not replace application-level safeguards.
2. **Cloud synchronization exposure:** Document and detect or warn when the database or imported statements are saved in iCloud Drive, Dropbox, Google Drive, or another synchronized directory; avoid unintended third-party uploads.
3. **Git and secrets hygiene:** Prevent real statements, SQLite databases, and credentials from being committed. Extend `.gitignore`, add example-only fixtures, and check repository history for accidental sensitive files.
4. **Untrusted CSV hardening:** Introduce file-size and row-count limits, strict input validation, resource controls, safe error handling, and adversarial tests before public upload support.

**Acceptance criteria:** Documented threat model and data flows; no unintended network transmission; tests covering import limits and malformed inputs; verified Git exclusions; and a clear disclosure of encryption and cloud-backup limitations.
