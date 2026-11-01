import argparse
from dataclasses import replace
from .core import category_totals, load_transactions
from .storage import connect, import_transactions, list_transactions, create_account, list_accounts


def main() -> None:
    parser = argparse.ArgumentParser(description='Summarize expenses from CSV or SQLite')
    parser.add_argument('csv_file', nargs='?', help='CSV with date,description,amount,category columns')
    parser.add_argument('--month', help='Filter by YYYY-MM')
    parser.add_argument('--db', help='SQLite database file (imports CSV when provided)')
    parser.add_argument('--add-account', metavar='ID')
    parser.add_argument('--name')
    parser.add_argument('--institution', default='')
    parser.add_argument('--list-accounts', action='store_true')
    parser.add_argument('--account')
    parser.add_argument('--amount-sign', choices=('expense-positive', 'expense-negative'),
                        default='expense-positive',
                        help='Single Amount column: whether positive or negative means spending')
    parser.add_argument('--preview', action='store_true',
                        help='Display parsed transactions without saving to SQLite')
    args = parser.parse_args()
    if args.preview:
        if not args.csv_file:
            parser.error('--preview requires a CSV file')
        transactions = load_transactions(args.csv_file, amount_sign=args.amount_sign)
        for tx in transactions[:10]:
            print(f'{tx.date}  {tx.amount:>12.2f}  {tx.description}  [{tx.category}]')
        print(f'Previewed {min(len(transactions), 10)} of {len(transactions)} transactions; no database writes')
        return
    if (args.add_account or args.list_accounts or args.account) and not args.db:
        parser.error('account operations require --db')
    if args.db:
        with connect(args.db) as db:
            if args.add_account:
                if not args.name:
                    parser.error('--add-account requires --name')
                create_account(db, args.add_account, args.name, args.institution)
                print(f'Created account {args.add_account}')
                return
            if args.list_accounts:
                for account_id, name, institution in list_accounts(db):
                    print(account_id, name, institution)
                return
            if args.csv_file:
                transactions = load_transactions(args.csv_file, amount_sign=args.amount_sign)
                if args.account:
                    if args.account not in {account[0] for account in list_accounts(db)}:
                        parser.error('unknown account: ' + args.account)
                    transactions = [replace(tx, account_id=args.account) for tx in transactions]
                inserted = import_transactions(db, transactions)
                print(f'Imported {inserted} new transactions')
            transactions = list_transactions(db)
    elif args.csv_file:
        transactions = load_transactions(args.csv_file, amount_sign=args.amount_sign)
    else:
        parser.error('provide a CSV file or --db')
    totals = category_totals(transactions, args.month)
    for category, amount in totals.items():
        print(f'{category:20} {amount:>12.2f}')
    print(f'{"TOTAL":20} {sum(totals.values()):>12.2f}')


if __name__ == '__main__':
    main()
