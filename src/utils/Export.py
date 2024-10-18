import csv
from datetime import datetime
from utils.Database import get_account_id, fetch_data, fetch_total

# Constants for CSV headers
TRANSACTION_HEADERS = ["Category", "Amount", "Currency", "Date"]
SUMMARY_HEADERS = ["Account Summary", "Total Income", "Total Expenses", "Net Income"]
TOP_CATEGORIES_HEADERS = ["Category", "Amount"]


def export_to_csv(account_name: str, conn) -> tuple:

    cursor = conn.cursor()
    try:
        account_id = get_account_id(cursor, account_name)
        if account_id is None:
            raise ValueError(f"Account '{account_name}' not found.")

        income_file = export_transactions(
            cursor, account_id, "income", f"{account_name}_income.csv"
        )
        expenses_file = export_transactions(
            cursor, account_id, "expenses", f"{account_name}_expenses.csv"
        )
        summary_file = export_summary(
            cursor, account_id, account_name, f"{account_name}_summary.csv"
        )

        return income_file, expenses_file, summary_file

    except Exception as e:
        raise RuntimeError(f"Error exporting data: {e}")
    finally:
        cursor.close()


def export_transactions(
    cursor, account_id: int, transaction_type: str, filename: str
) -> str:
    try:
        query = f"SELECT category, amount, currency, date FROM {transaction_type} WHERE account_id = ? ORDER BY date"
        transactions = fetch_data(cursor, query, (account_id,))

        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(TRANSACTION_HEADERS)  # Header
            writer.writerows(transactions)

        return filename

    except Exception as e:
        raise RuntimeError(f"Error exporting {transaction_type}: {e}")


def export_summary(cursor, account_id: int, account_name: str, filename: str) -> str:
    try:
        total_income = fetch_total(cursor, "income", account_id)
        total_expenses = fetch_total(cursor, "expenses", account_id)
        net_income = total_income - total_expenses

        # Fetch top 5 income categories
        income_categories = fetch_data(
            cursor,
            "SELECT category, SUM(amount) as total FROM income WHERE account_id = ? GROUP BY category ORDER BY total DESC LIMIT 5",
            (account_id,),
        )

        # Fetch top 5 expense categories
        expense_categories = fetch_data(
            cursor,
            "SELECT category, SUM(amount) as total FROM expenses WHERE account_id = ? GROUP BY category ORDER BY total DESC LIMIT 5",
            (account_id,),
        )

        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([SUMMARY_HEADERS[0], account_name])
            writer.writerow([SUMMARY_HEADERS[1], f"${total_income:.2f}"])
            writer.writerow([SUMMARY_HEADERS[2], f"${total_expenses:.2f}"])
            writer.writerow([SUMMARY_HEADERS[3], f"${net_income:.2f}"])
            writer.writerow([])

            writer.writerow(["Top 5 Income Categories"])
            writer.writerow(TOP_CATEGORIES_HEADERS)
            writer.writerows(income_categories)
            writer.writerow([])

            writer.writerow(["Top 5 Expense Categories"])
            writer.writerow(TOP_CATEGORIES_HEADERS)
            writer.writerows(expense_categories)
            writer.writerow([])

            writer.writerow(
                ["Export Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            )

        return filename

    except Exception as e:
        raise RuntimeError(f"Error exporting summary: {e}")


def export_date_range(account_name: str, conn, start_date: str, end_date: str) -> tuple:
    cursor = conn.cursor()
    try:
        account_id = get_account_id(cursor, account_name)
        if account_id is None:
            raise ValueError(f"Account '{account_name}' not found.")

        income_file = export_transactions_range(
            cursor,
            account_id,
            "income",
            start_date,
            end_date,
            f"{account_name}_income_{start_date}_{end_date}.csv",
        )
        expenses_file = export_transactions_range(
            cursor,
            account_id,
            "expenses",
            start_date,
            end_date,
            f"{account_name}_expenses_{start_date}_{end_date}.csv",
        )
        summary_file = export_summary_range(
            cursor,
            account_id,
            account_name,
            start_date,
            end_date,
            f"{account_name}_summary_{start_date}_{end_date}.csv",
        )

        return income_file, expenses_file, summary_file

    except Exception as e:
        raise RuntimeError(f"Error exporting data for date range: {e}")
    finally:
        cursor.close()


def export_transactions_range(
    cursor,
    account_id: int,
    transaction_type: str,
    start_date: str,
    end_date: str,
    filename: str,
) -> str:
    try:
        query = f"SELECT category, amount, currency, date FROM {transaction_type} WHERE account_id = ? AND date BETWEEN ? AND ? ORDER BY date"
        transactions = fetch_data(cursor, query, (account_id, start_date, end_date))

        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(TRANSACTION_HEADERS)  # Header
            writer.writerows(transactions)

        return filename

    except Exception as e:
        raise RuntimeError(f"Error exporting {transaction_type} for date range: {e}")


def export_summary_range(
    cursor,
    account_id: int,
    account_name: str,
    start_date: str,
    end_date: str,
    filename: str,
) -> str:
    try:
        total_income = fetch_total(cursor, "income", account_id, start_date, end_date)
        total_expenses = fetch_total(
            cursor, "expenses", account_id, start_date, end_date
        )
        net_income = total_income - total_expenses

        # Fetch top 5 income categories for the date range
        income_categories = fetch_data(
            cursor,
            "SELECT category, SUM(amount) as total FROM income WHERE account_id = ? AND date BETWEEN ? AND ? GROUP BY category ORDER BY total DESC LIMIT 5",
            (account_id, start_date, end_date),
        )

        # Fetch top 5 expense categories for the date range
        expense_categories = fetch_data(
            cursor,
            "SELECT category, SUM(amount) as total FROM expenses WHERE account_id = ? AND date BETWEEN ? AND ? GROUP BY category ORDER BY total DESC LIMIT 5",
            (account_id, start_date, end_date),
        )

        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([SUMMARY_HEADERS[0], account_name])
            writer.writerow(["Date Range", f"{start_date} to {end_date}"])
            writer.writerow([SUMMARY_HEADERS[1], f"${total_income:.2f}"])
            writer.writerow([SUMMARY_HEADERS[2], f"${total_expenses:.2f}"])
            writer.writerow([SUMMARY_HEADERS[3], f"${net_income:.2f}"])
            writer.writerow([])

            writer.writerow(["Top 5 Income Categories"])
            writer.writerow(TOP_CATEGORIES_HEADERS)
            writer.writerows(income_categories)
            writer.writerow([])

            writer.writerow(["Top 5 Expense Categories"])
            writer.writerow(TOP_CATEGORIES_HEADERS)
            writer.writerows(expense_categories)
            writer.writerow([])

            writer.writerow(
                ["Export Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            )

        return filename

    except Exception as e:
        raise RuntimeError(f"Error exporting summary for date range: {e}")
