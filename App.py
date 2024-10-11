import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import sqlite3
import time
import os
import ttkbootstrap as tb
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

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
root = tb.Window(themename="superhero")  # Using ttkbootstrap theme
root.title("Budget Tracker")
root.geometry("800x600")
try:
    root.iconphoto(False, tk.PhotoImage(file='./budget_icon.png'))  # Set the icon for the window
except tk.TclError as e:
    print(f"Error loading icon: {e}")

# Create a notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

# Create tabs for adding income, expenses, and visualization
income_tab = ttk.Frame(notebook)
expense_tab = ttk.Frame(notebook)
visualization_tab = ttk.Frame(notebook)
summary_tab = ttk.Frame(notebook)
analysis_tab = ttk.Frame(notebook)

notebook.add(income_tab, text="Add Income")
notebook.add(expense_tab, text="Add Expense")
notebook.add(visualization_tab, text="Visualization")
notebook.add(summary_tab, text="Display Summary")
notebook.add(analysis_tab, text="Budget Analysis")

# Create database connection
conn = create_or_open_database("Default")

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
    except Exception as e:
        print(f"Error adding transaction: {e}")

# Create labels and entry fields for transactions with improved layout
def create_transaction_widgets(tab, transaction_type):
    account_name_label = ttk.Label(tab, text="Account Name:")
    account_name_label.pack(pady=5)

    account_name_entry = ttk.Entry(tab)
    account_name_entry.pack(pady=5)

    category_label = ttk.Label(tab, text="Category:")
    category_label.pack(pady=5)

    category_entry = ttk.Entry(tab)
    category_entry.pack(pady=5)

    amount_label = ttk.Label(tab, text="Amount:")
    amount_label.pack(pady=5)

    amount_entry = ttk.Entry(tab)
    amount_entry.pack(pady=5)

    add_transaction_button = ttk.Button(tab, text=f"Add {transaction_type.capitalize()}",
                                         command=lambda: add_transaction(
                                             account_name_entry.get(),
                                             category_entry.get(),
                                             amount_entry.get(),
                                             transaction_type,
                                             conn))
    add_transaction_button.pack(pady=10)

    # Add Tooltip for clarity
    ToolTip(add_transaction_button, text=f"Add a new {transaction_type} entry", bootstyle=INFO)

# Create widgets for income and expenses tabs
create_transaction_widgets(income_tab, 'income')
create_transaction_widgets(expense_tab, 'expenses')

# Function to update the summary text
def update_summary_text(account_name, transaction_type, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()
    
    if account_id is not None:
        account_id = account_id[0]
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
summary_account_label = ttk.Label(summary_tab, text="Account Name:")
summary_account_label.pack(pady=5)

summary_account_entry = ttk.Entry(summary_tab)
summary_account_entry.pack(pady=5)

summary_text = tk.Text(summary_tab, height=10, width=40)
summary_text.pack(pady=5)

display_summary_button = ttk.Button(summary_tab, text="Display Summary",
                                     command=lambda: update_summary_text(
                                         summary_account_entry.get(), "income", conn))
display_summary_button.pack(pady=5)

ToolTip(display_summary_button, text="Show income summary", bootstyle=INFO)

# Function to create a bar chart
def create_bar_chart(account_name, conn):
    plt.clf()  # Avoid overlap
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()
    
    if account_id is not None:
        account_id = account_id[0]
        cursor.execute("SELECT category, amount FROM income WHERE account_id = ?", (account_id,))
        data = cursor.fetchall()
        categories = [item[0] for item in data]
        amounts = [item[1] for item in data]

        plt.figure(figsize=(8, 6))
        plt.bar(categories, amounts, color="#5DADE2")
        plt.xlabel('Category')
        plt.ylabel('Amount (USD)')
        plt.title('Income by Category')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Embed the matplotlib figure in the Tkinter window
        canvas = FigureCanvasTkAgg(plt.gcf(), master=visualization_tab)
        canvas.get_tk_widget().pack(pady=20)
    else:
        print("Account not found for bar chart.")

# Visualization Tab
visualization_account_label = ttk.Label(visualization_tab, text="Account Name:")
visualization_account_label.pack(pady=5)

visualization_account_entry = ttk.Entry(visualization_tab)
visualization_account_entry.pack(pady=5)

visualization_button = ttk.Button(visualization_tab, text="Generate Bar Chart",
                                   command=lambda: create_bar_chart(visualization_account_entry.get(), conn))
visualization_button.pack(pady=5)

ToolTip(visualization_button, text="Generate a bar chart for income", bootstyle=INFO)

# Budget Analysis Tab
analysis_account_label = ttk.Label(analysis_tab, text="Account Name:")
analysis_account_label.pack(pady=5)

analysis_account_entry = ttk.Entry(analysis_tab)
analysis_account_entry.pack(pady=5)

analysis_text = tk.Text(analysis_tab, height=10, width=40)
analysis_text.pack(pady=5)

# Add a function for budget analysis (currently just a placeholder)
def budget_analysis(account_name, conn):
    analysis_text.config(state=tk.NORMAL)
    analysis_text.delete(1.0, tk.END)
    analysis_text.insert(tk.END, f"Budget analysis for {account_name} will be implemented.\n")
    analysis_text.config(state=tk.DISABLED)

analysis_button = ttk.Button(analysis_tab, text="Calculate Budget Analysis",
                             command=lambda: budget_analysis(analysis_account_entry.get(), conn))
analysis_button.pack(pady=20)

ToolTip(analysis_button, text="Calculate analysis of budget", bootstyle=INFO)

# Main Loop
root.mainloop()
conn.close()