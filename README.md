# expense-tracker

A small Python project for understanding spending patterns from transaction exports.

## v0.1 — CSV summary CLI

- Read transactions from a CSV (`date,description,amount,category`)
- Use `Decimal` for precise currency arithmetic
- Summarize expenses by category, optionally for one month
- Treat negative amounts as refunds
- Report malformed CSV rows with line numbers
- No runtime dependencies

## Run

```bash
PYTHONPATH=src python -m expense_tracker examples/transactions.csv --month 2026-10
```

## Test

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Roadmap

- v0.2: SQLite storage and duplicate detection
- v0.3: User-defined categorization rules and CSV export
- v0.4: Web API and structured logging
- v1.0: Forecasting and anomaly detection, with explicit evaluation metrics
