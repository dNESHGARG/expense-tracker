import argparse
from .core import category_totals, load_transactions
from .storage import connect, import_transactions, list_transactions


def main() -> None:
    parser = argparse.ArgumentParser(description='Summarize expenses from CSV or SQLite')
    parser.add_argument('csv_file', nargs='?', help='CSV with date,description,amount,category columns')
    parser.add_argument('--month', help='Filter by YYYY-MM')
    parser.add_argument('--db', help='SQLite database file (imports CSV when provided)')
    args = parser.parse_args()
    if args.db:
        with connect(args.db) as db:
            if args.csv_file:
                inserted = import_transactions(db, load_transactions(args.csv_file))
                print(f'Imported {inserted} new transactions')
            transactions = list_transactions(db)
    elif args.csv_file:
        transactions = load_transactions(args.csv_file)
    else:
        parser.error('provide a CSV file or --db')
    totals = category_totals(transactions, args.month)
    for category, amount in totals.items():
        print(f'{category:20} {amount:>12.2f}')
    print(f'{"TOTAL":20} {sum(totals.values()):>12.2f}')


if __name__ == '__main__':
    main()
