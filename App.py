import time
import json
import sqlite3
import tkinter as tk
import customtkinter as ctk
from ttkbootstrap import Style
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Set up appearance and style
style = Style(theme="darkly")
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def load_to_json():
    try:
        with open("users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"accounts": []}


def create_or_open_database(account_name):
    db_name = f"{account_name}.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Ensure foreign key support
    cursor.execute("PRAGMA foreign_keys = 1")

    # Create necessary tables if they don't exist
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY, name TEXT UNIQUE
        );
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY, account_id INTEGER, category TEXT, amount REAL,
            currency TEXT, date TEXT, FOREIGN KEY (account_id) REFERENCES accounts (id)
        );
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY, account_id INTEGER, category TEXT, amount REAL,
            currency TEXT, date TEXT, FOREIGN KEY (account_id) REFERENCES accounts (id)
        );
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY, account_id INTEGER, category TEXT, amount REAL,
            currency TEXT, date TEXT, FOREIGN KEY (account_id) REFERENCES accounts (id)
        );
        """
    )

    # Check if account exists, if not insert it
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO accounts (name) VALUES (?)", (account_name,))

    conn.commit()
    return conn


# Main Window Setup
root = ctk.CTk()
root.title("Budget Tracker")
root.geometry("800x600")

# Tab Setup
notebook = ctk.CTkTabview(root)
notebook.pack(fill=ctk.BOTH, expand=True, pady=5, padx=5)

# Tabs for Income, Expenses, Goals, Visualization
tabs = ["Income", "Expenses", "Goals", "Visualization", "Summary", "Budget Analysis"]
for tab_name in tabs:
    notebook.add(tab_name)

# Unpack tabs for ease of use
income_tab, expense_tab, goals_tab, visualization_tab, summary_tab, analysis_tab = [
    notebook.tab(tab_name) for tab_name in tabs
]


def add_transaction(account_name, category, amount, transaction_type, conn):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()

    if account_id:
        account_id = account_id[0]
        cursor.execute(
            f"INSERT INTO {transaction_type} (account_id, category, amount, currency, date) "
            "VALUES (?, ?, ?, ?, ?)",
            (account_id, category, amount, "USD", timestamp),
        )
        conn.commit()
        update_summary_text(account_name, transaction_type, conn)
    else:
        print(f"Account '{account_name}' not found.")  # Better error handling


def create_transaction_widgets(tab, transaction_type, conn):
    labels = ["Account Name:", "Category:", "Amount:"]
    entries = [ctk.CTkEntry(tab) for _ in range(3)]

    for i, label in enumerate(labels):
        ctk.CTkLabel(tab, text=label).pack(pady=5)
        entries[i].pack(pady=5)

    add_transaction_button = ctk.CTkButton(
        tab,
        text=f"Add {transaction_type.capitalize()}",
        command=lambda: add_transaction(
            entries[0].get(),
            entries[1].get(),
            (
                float(entries[2].get()) if entries[2].get() else 0.0
            ),  # Prevent empty input error
            transaction_type,
            conn,
        ),
    )
    add_transaction_button.pack(pady=5)


conn = create_or_open_database("Default")
create_transaction_widgets(income_tab, "income", conn)
create_transaction_widgets(expense_tab, "expenses", conn)


def update_summary_text(account_name, transaction_type, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()

    if not account_id:
        summary_text.configure(state=tk.NORMAL)
        summary_text.delete(1.0, tk.END)
        summary_text.insert(tk.END, f"Account '{account_name}' not found.\n")
        summary_text.configure(state=tk.DISABLED)
        return

    account_id = account_id[0]
    cursor.execute(
        f"SELECT category, amount FROM {transaction_type} WHERE account_id = ?",
        (account_id,),
    )
    data = cursor.fetchall()

    summary_text.configure(state=tk.NORMAL)
    summary_text.delete(1.0, tk.END)
    summary_text.insert(
        tk.END,
        f"Summary for Account: {account_name}\n\n{transaction_type.capitalize()}:\n",
    )
    for item in data:
        summary_text.insert(tk.END, f"{item[0]}: ${item[1]:.2f}\n")
    summary_text.configure(state=tk.DISABLED)


# Summary Widgets
ctk.CTkLabel(summary_tab, text="Account Name:").pack(pady=5)
summary_account_entry = ctk.CTkEntry(summary_tab)
summary_account_entry.pack(pady=5)
summary_text = ctk.CTkTextbox(summary_tab, height=10, width=40)
summary_text.pack(pady=5)
display_summary_button = ctk.CTkButton(
    summary_tab,
    text="Display Summary",
    command=lambda: update_summary_text(summary_account_entry.get(), "income", conn),
)
display_summary_button.pack(pady=5)


def create_bar_chart(account_name, conn):
    plt.clf()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()

    if not account_id:
        print(f"Account '{account_name}' not found.")
        return

    account_id = account_id[0]
    cursor.execute(
        "SELECT category, amount FROM income WHERE account_id = ?", (account_id,)
    )
    data = cursor.fetchall()

    categories = [item[0] for item in data]
    amounts = [item[1] for item in data]

    plt.bar(categories, amounts)
    plt.xlabel("Category")
    plt.ylabel("Amount (USD)")
    plt.title(f"Income by Category for {account_name}")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(plt.gcf(), master=visualization_tab)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=5)


def budget_analysis(account_name, conn):

    print(f"Calculating budget analysis for: {account_name}")


# Budget Analysis Widgets
ctk.CTkLabel(analysis_tab, text="Account Name:").pack(pady=5)
analysis_account_entry = ctk.CTkEntry(analysis_tab)
analysis_account_entry.pack(pady=5)
analysis_text = ctk.CTkLabel(analysis_tab, text="Budget Analysis Result:")
analysis_text.pack(pady=5)
analysis_button = ctk.CTkButton(
    analysis_tab,
    text="Calculate Budget Analysis",
    command=lambda: budget_analysis(analysis_account_entry.get(), conn),
)
analysis_button.pack(pady=5)


def save_to_json(account_name, conn):
    cursor = conn.cursor()

    # Fetch data from the database
    def fetch_data(table_name):
        cursor.execute(
            f"SELECT category, amount, currency, date FROM {table_name} WHERE account_id = (SELECT id FROM accounts WHERE name = ?)",
            (account_name,),
        )
        return cursor.fetchall()

    income_data = fetch_data("income")
    expense_data = fetch_data("expenses")
    goal_data = fetch_data("goals")

    # Prepare the data to be saved
    data = {
        "income": [
            {
                "category": item[0],
                "amount": item[1],
                "currency": item[2],
                "date": item[3],
            }
            for item in income_data
        ],
        "expenses": [
            {
                "category": item[0],
                "amount": item[1],
                "currency": item[2],
                "date": item[3],
            }
            for item in expense_data
        ],
        "goals": [
            {
                "category": item[0],
                "amount": item[1],
                "currency": item[2],
                "date": item[3],
            }
            for item in goal_data
        ],
    }

    with open(f"{account_name}.json", "w") as json_file:
        json.dump(data, json_file)


def load_user_data(account_name, conn):
    try:
        with open(f"{account_name}.json", "r") as json_file:
            data = json.load(json_file)
            for item in data.get("income", []):
                add_transaction(
                    account_name, item["category"], item["amount"], "income", conn
                )
            for item in data.get("expenses", []):
                add_transaction(
                    account_name, item["category"], item["amount"], "expenses", conn
                )
            for item in data.get("goals", []):
                add_transaction(
                    account_name, item["category"], item["amount"], "goals", conn
                )
    except FileNotFoundError:
        print("User data file not found")


# Load existing user data
user_data = load_to_json()
if user_data:
    for account in user_data.get("accounts", []):
        conn = create_or_open_database(account)

# Run the main event loop
root.mainloop()
