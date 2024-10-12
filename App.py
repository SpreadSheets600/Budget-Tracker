import customtkinter as ctk  # Imports customTkinter
import tkinter.font as tkFont
import sqlite3
import time
import os
import matplotlib.pyplot as plt
import json  # Uses json to save and load files to keep data permanent per user login
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ttkbootstrap import Style  # Importing ttkbootstrap for better styling

# Initialize ttkbootstrap style
style = Style(theme='darkly')

ctk.set_appearance_mode("Dark")  # Set color scheme
ctk.set_default_color_theme("blue")

def load_to_json():
    try:
        with open("users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None

# Function to create or open the SQLite database
def create_or_open_database(account_name):
    db_name = f"{account_name}.db"
    if os.path.exists(db_name):
        conn = sqlite3.connect(db_name)
    else:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = 1")

        # Create tables for income, expenses, and goals
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY,
                account_id INTEGER,
                category TEXT,
                amount REAL,
                currency TEXT,
                date TEXT,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                account_id INTEGER,
                category TEXT,
                amount REAL,
                currency TEXT,
                date TEXT,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY,
                account_id INTEGER,
                category TEXT,
                amount REAL,
                currency TEXT,
                date TEXT,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        """)

        cursor.execute("INSERT INTO accounts (name) VALUES (?)", (account_name,))
        conn.commit()

    return conn

# Create the main window
root = ctk.CTk()  # Change widgets
root.title("Budget Tracker")
root.geometry("800x600")

# Create a notebook for tabs
notebook = ctk.CTkTabView(root)
notebook.pack(fill=ctk.BOTH, expand=True, pady=5, padx=5)

# Create tabs for adding income, expenses, and goals
income_tab = ctk.CTkFrame(notebook)
expense_tab = ctk.CTkFrame(notebook)
goals_tab = ctk.CTkFrame(notebook)

notebook.add(income_tab, text="Add Income")
notebook.add(expense_tab, text="Add Expense")

# Create a frame for the "Visualization" tab
visualization_tab = ctk.CTkFrame(notebook)
notebook.add(visualization_tab, text="Visualization")

# Function to add income or expense
def add_transaction(account_name, category, amount, transaction_type, conn):
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
        account_id = cursor.fetchone()[0]
        cursor.execute(f"INSERT INTO {transaction_type} (account_id, category, amount, currency, date) VALUES (?, ?, ?, ?, ?)",
                       (account_id, category, amount, 'USD', timestamp))
        conn.commit()
        update_summary_text(account_name, transaction_type, conn)
    except ValueError:
        print("Invalid amount")

# Create labels and entry fields for transactions
def create_transaction_widgets(tab, transaction_type, conn):
    account_name_label = ctk.CTkLabel(tab, text="Account Name:")
    account_name_label.pack(pady=5)

    account_name_entry = ctk.CTkEntry(tab)
    account_name_entry.pack(pady=5)

    category_label = ctk.CTkLabel(tab, text="Category:")
    category_label.pack(pady=5)

    category_entry = ctk.CTkEntry(tab)
    category_entry.pack(pady=5)

    amount_label = ctk.CTkLabel(tab, text="Amount:")
    amount_label.pack(pady=5)

    amount_entry = ctk.CTkEntry(tab)
    amount_entry.pack(pady=5)

    add_transaction_button = ctk.CTkButton(tab, text=f"Add {transaction_type.capitalize()}",
                                             command=lambda: add_transaction(
                                                 account_name_entry.get(), category_entry.get(),
                                                 float(amount_entry.get()), transaction_type, conn))
    add_transaction_button.pack(pady=5)

# Create widgets for income and expenses tabs
conn = create_or_open_database("Default")
create_transaction_widgets(income_tab, 'income', conn)
create_transaction_widgets(expense_tab, 'expenses', conn)

# Function to update the summary text
def update_summary_text(account_name, transaction_type, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()[0]
    cursor.execute(f"SELECT category, amount FROM {transaction_type} WHERE account_id = ?", (account_id,))
    data = cursor.fetchall()

    summary_text.config(state=tk.NORMAL)
    summary_text.delete(1.0, tk.END)
    summary_text.insert(tk.END, f"Summary for Account: {account_name}\n\n")
    summary_text.insert(tk.END, f"{transaction_type.capitalize()}:\n")
    for item in data:
        summary_text.insert(tk.END, f"{item[0]}: ${item[1]:.2f}\n")
    summary_text.config(state=tk.DISABLED)

# Summary Tab
summary_tab = ctk.CTkFrame(notebook)
notebook.add(summary_tab, text="Display Summary")

summary_account_label = ctk.CTkLabel(summary_tab, text="Account Name:")
summary_account_label.pack(pady=5)

summary_account_entry = ctk.CTkEntry(summary_tab)
summary_account_entry.pack(pady=5)

summary_text = ctk.CTkTextbox(summary_tab, height=10, width=40)  # Changed to CTkTextbox for multi-line text
summary_text.pack(pady=5)

display_summary_button = ctk.CTkButton(summary_tab, text="Display Summary", command=lambda: update_summary_text(
    summary_account_entry.get(), "income", conn))
display_summary_button.pack(pady=5)

# Function to create a bar chart
def create_bar_chart(account_name, conn):
    plt.clf()  # Avoid overlap
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()[0]
    cursor.execute(
        "SELECT category, amount FROM income WHERE account_id = ?", (account_id,))
    data = cursor.fetchall()
    categories = [item[0] for item in data]
    amounts = [item[1] for item in data]

    plt.figure(figsize=(8, 6))
    plt.bar(categories, amounts)
    plt.xlabel('Category')
    plt.ylabel('Amount (USD)')
    plt.title('Income by Category')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Embed the matplotlib figure in the Tkinter window
    canvas = FigureCanvasTkAgg(plt.gcf(), master=visualization_tab)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=5)

# Budget Analysis Tab
analysis_tab = ctk.CTkFrame(notebook)
notebook.add(analysis_tab, text="Budget Analysis")

analysis_account_label = ctk.CTkLabel(analysis_tab, text="Account Name:")
analysis_account_label.pack(pady=5)

analysis_account_entry = ctk.CTkEntry(analysis_tab)
analysis_account_entry.pack(pady=5)

analysis_text = ctk.CTkLabel(analysis_tab, text="Budget Analysis Result:")  # Updated label for clarity
analysis_text.pack(pady=5)

analysis_button = ctk.CTkButton(analysis_tab, text="Calculate Budget Analysis",
                                 command=lambda: budget_analysis(analysis_account_entry.get(), conn))
analysis_button.pack(pady=5)

# Function to save user data
def save_to_json(account_name, conn):
    cursor = conn.cursor()

    cursor.execute("SELECT category, amount, currency, date FROM income WHERE account_id = (SELECT id FROM accounts WHERE name = ?)", (account_name,))
    income_data = cursor.fetchall()

    cursor.execute("SELECT category, amount, currency, date FROM expenses WHERE account_id = (SELECT id FROM accounts WHERE name = ?)", (account_name,))
    expense_data = cursor.fetchall()

    cursor.execute("SELECT category, amount, currency, date FROM goals WHERE account_id = (SELECT id FROM accounts WHERE name = ?)", (account_name,))
    goal_data = cursor.fetchall()

    # Data stored via dictionary
    data = {
        "income": [{"category": item[0], "amount": item[1], "currency": item[2], "date": item[3]} for item in income_data],
        "expenses": [{"category": item[0], "amount": item[1], "currency": item[2], "date": item[3]} for item in expense_data],
        "goals": [{"category": item[0], "amount": item[1], "currency": item[2], "date": item[3]} for item in goal_data],
    }

    with open(f"{account_name}.json", "w") as json_file:
        json.dump(data, json_file)

# Function to load user data
def load_user_data(account_name):
    try:
        with open(f"{account_name}.json", "r") as json_file:
            data = json.load(json_file)
            # Load income data
            for item in data.get("income", []):
                add_transaction(account_name, item["category"], item["amount"], "income", conn)
            # Load expense data
            for item in data.get("expenses", []):
                add_transaction(account_name, item["category"], item["amount"], "expenses", conn)
            # Load goal data
            for item in data.get("goals", []):
                add_transaction(account_name, item["category"], item["amount"], "goals", conn)
    except FileNotFoundError:
        print("User data file not found")

# Load user data when the application starts
user_data = load_to_json()
if user_data:
    for account in user_data.get("accounts", []):
        conn = create_or_open_database(account)

# Main loop
root.mainloop()

