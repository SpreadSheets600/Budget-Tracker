import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sqlite3
import time
import os
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ttkbootstrap import Style

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
    cursor.execute("PRAGMA foreign_keys = 1")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY, name TEXT UNIQUE
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY, account_id INTEGER, category TEXT, amount REAL,
            currency TEXT, date TEXT, FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY, account_id INTEGER, category TEXT, amount REAL,
            currency TEXT, date TEXT, FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY, account_id INTEGER, category TEXT, amount REAL,
            currency TEXT, date TEXT, FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    """
    )
    cursor.execute("INSERT OR IGNORE INTO accounts (name) VALUES (?)", (account_name,))
    conn.commit()
    return conn


# Helper function for error notifications
def show_error(message):
    messagebox.showerror("Error", message)


# Main Window
root = ctk.CTk()
root.title("Budget Tracker")
root.geometry("900x600")

# Tab Setup
notebook = ctk.CTkTabview(root)
notebook.pack(fill=ctk.BOTH, expand=True, pady=10, padx=10)

# Tabs for Income, Expenses, Goals, Visualization, Summary, and Budget Analysis
tabs = ["Income", "Expenses", "Goals", "Visualization", "Summary", "Budget Analysis"]
for tab_name in tabs:
    notebook.add(tab_name)
income_tab, expense_tab, goals_tab, visualization_tab, summary_tab, analysis_tab = [
    notebook.tab(tab_name) for tab_name in tabs
]


def add_transaction(account_name, category, amount, transaction_type, conn):
    if not account_name or not category or amount <= 0:
        show_error(
            "Please provide valid inputs for account name, category, and amount."
        )
        return

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()

    # If the account doesn't exist, create one
    if not account_id:
        cursor.execute("INSERT INTO accounts (name) VALUES (?)", (account_name,))
        conn.commit()
        cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
        account_id = cursor.fetchone()

    account_id = account_id[0]
    cursor.execute(
        f"INSERT INTO {transaction_type} (account_id, category, amount, currency, date) "
        "VALUES (?, ?, ?, ?, ?)",
        (account_id, category, amount, "USD", timestamp),
    )
    conn.commit()
    update_summary_text(account_name, transaction_type, conn)


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
            float(entries[2].get() or 0),  # Handle empty input for amount
            transaction_type,
            conn,
        ),
    )
    add_transaction_button.pack(pady=10)


conn = create_or_open_database("Default")
create_transaction_widgets(income_tab, "income", conn)
create_transaction_widgets(expense_tab, "expenses", conn)


def update_summary_text(account_name, transaction_type, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()

    if not account_id:
        show_error(f"No account found for '{account_name}'")
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
summary_text.pack(pady=10)
display_summary_button = ctk.CTkButton(
    summary_tab,
    text="Display Summary",
    command=lambda: update_summary_text(summary_account_entry.get(), "income", conn),
)
display_summary_button.pack(pady=10)


def create_bar_chart(account_name, conn):
    plt.clf()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()

    if not account_id:
        show_error(f"No account found for '{account_name}'")
        return

    account_id = account_id[0]
    cursor.execute(
        "SELECT category, amount FROM income WHERE account_id = ?", (account_id,)
    )
    data = cursor.fetchall()

    if not data:
        show_error("No income data available for the selected account.")
        return

    categories = [item[0] for item in data]
    amounts = [item[1] for item in data]

    plt.bar(categories, amounts)
    plt.xlabel("Category")
    plt.ylabel("Amount (USD)")
    plt.title("Income by Category")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(plt.gcf(), master=visualization_tab)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)


# Budget Analysis Widgets
ctk.CTkLabel(analysis_tab, text="Account Name:").pack(pady=5)
analysis_account_entry = ctk.CTkEntry(analysis_tab)
analysis_account_entry.pack(pady=5)
analysis_text = ctk.CTkLabel(analysis_tab, text="Budget Analysis Result:")
analysis_text.pack(pady=10)


def budget_analysis(account_name, conn):
    print(f"Calculating budget analysis for: {account_name}")


analysis_button = ctk.CTkButton(
    analysis_tab,
    text="Calculate Budget Analysis",
    command=lambda: budget_analysis(analysis_account_entry.get(), conn),
)
analysis_button.pack(pady=10)


def save_to_json(account_name, conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT category, amount, currency, date FROM income WHERE account_id = (SELECT id FROM accounts WHERE name = ?)",
        (account_name,),
    )
    income_data = cursor.fetchall()
    cursor.execute(
        "SELECT category, amount, currency, date FROM expenses WHERE account_id = (SELECT id FROM accounts WHERE name = ?)",
        (account_name,),
    )
    expense_data = cursor.fetchall()
    cursor.execute(
        "SELECT category, amount, currency, date FROM goals WHERE account_id = (SELECT id FROM accounts WHERE name = ?)",
        (account_name,),
    )
    goal_data = cursor.fetchall()

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
        show_error(f"No data found for '{account_name}'")


# Loading user data and initializing app with accounts
user_data = load_to_json()
if user_data:
    for account in user_data.get("accounts", []):
        conn = create_or_open_database(account)

root.mainloop()
