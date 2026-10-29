import argparse
from .core import category_totals, load_transactions


def main() -> None:
    parser = argparse.ArgumentParser(description='Summarize expenses from a CSV file')
    parser.add_argument('csv_file', help='CSV with date,description,amount,category columns')
    parser.add_argument('--month', help='Filter by YYYY-MM')
    args = parser.parse_args()
    totals = category_totals(load_transactions(args.csv_file), args.month)
    for category, amount in totals.items():
        print(f'{category:20} {amount:>12.2f}')
    print(f'{"TOTAL":20} {sum(totals.values()):>12.2f}')


if __name__ == '__main__':
    main()
