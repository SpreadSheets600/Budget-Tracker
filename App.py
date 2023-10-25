import tkinter as tk
from tkinter import ttk

import sqlite3
import time
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

        cursor.execute("INSERT INTO accounts (name) VALUES (?)",
                       (account_name,))
        conn.commit()

    return conn


# Create the main window
root = tk.Tk()
root.title("Budget Tracker")

# Create a notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Create tabs for adding income, expenses, and goals
income_tab = ttk.Frame(notebook)
expense_tab = ttk.Frame(notebook)
goals_tab = ttk.Frame(notebook)

notebook.add(income_tab, text="Add Income")
notebook.add(expense_tab, text="Add Expense")

# Create a frame for the "Visualization" tab
visualization_tab = ttk.Frame(notebook)
notebook.add(visualization_tab, text="Visualization")

# Function to add income


def add_transaction(account_name, category, amount, transaction_type, conn):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()[0]
    cursor.execute(f"INSERT INTO {transaction_type} (account_id, category, amount, currency, date) VALUES (?, ?, ?, ?, ?)",
                   (account_id, category, amount, 'USD', timestamp))
    conn.commit()
    update_summary_text(account_name, transaction_type, conn)

# Create labels and entry fields for transactions


def create_transaction_widgets(tab, transaction_type, conn):
    account_name_label = tk.Label(tab, text="Account Name:")
    account_name_label.pack()

    account_name_entry = tk.Entry(tab)
    account_name_entry.pack()

    category_label = tk.Label(tab, text="Category:")
    category_label.pack()

    category_entry = tk.Entry(tab)
    category_entry.pack()

    amount_label = tk.Label(tab, text="Amount:")
    amount_label.pack()

    amount_entry = tk.Entry(tab)
    amount_entry.pack()

    add_transaction_button = tk.Button(tab, text=f"Add {transaction_type}", command=lambda: add_transaction(
        account_name_entry.get(), category_entry.get(), float(amount_entry.get()), transaction_type, conn))
    add_transaction_button.pack()


# Create widgets for income and expenses tabs
conn = create_or_open_database("Default")
create_transaction_widgets(income_tab, 'income', conn)
create_transaction_widgets(expense_tab, 'expenses', conn)

# Function to update the summary text


def update_summary_text(account_name, transaction_type, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()[0]
    cursor.execute(
        f"SELECT category, amount FROM {transaction_type} WHERE account_id = ?", (account_id,))
    data = cursor.fetchall()

    summary_text.config(state=tk.NORMAL)
    summary_text.delete(1.0, tk.END)
    summary_text.insert(tk.END, f"Summary for Account: {account_name}\n\n")
    summary_text.insert(tk.END, f"{transaction_type.capitalize()}:\n")
    for item in data:
        summary_text.insert(tk.END, f"{item[0]}: ${item[1]:.2f}\n")
    summary_text.config(state=tk.DISABLED)


# Button to display the summary in the "Display Summary" tab
summary_tab = ttk.Frame(notebook)
notebook.add(summary_tab, text="Display Summary")

summary_account_label = tk.Label(summary_tab, text="Account Name:")
summary_account_label.pack()

summary_account_entry = tk.Entry(summary_tab)
summary_account_entry.pack()

summary_text = tk.Text(summary_tab, height=10, width=40)
summary_text.pack()

display_summary_button = tk.Button(summary_tab, text="Display Summary", command=lambda: update_summary_text(
    summary_account_entry.get(), "income", conn))
display_summary_button.pack()

# Function to create a bar chart


def create_bar_chart(account_name, conn):
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

    # Embed the matplotlib figure in the Tkinter window
    canvas = FigureCanvasTkAgg(plt.gcf(), master=visualization_tab)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()

# Function to create a line chart


def create_line_chart(account_name, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()[0]
    cursor.execute(
        "SELECT date, amount FROM income WHERE account_id = ?", (account_id,))
    data = cursor.fetchall()
    dates = [item[0] for item in data]
    amounts = [item[1] for item in data]

    plt.figure(figsize=(8, 6))
    plt.plot(dates, amounts, marker='o', linestyle='-')
    plt.xlabel('Date')
    plt.ylabel('Income Amount (USD)')
    plt.title('Income Over Time')
    plt.xticks(rotation=45, ha='right')

    # Embed the matplotlib figure in the Tkinter window
    canvas = FigureCanvasTkAgg(plt.gcf(), master=visualization_tab)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()

# Function to create a pie chart


def create_pie_chart(account_name, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()[0]
    cursor.execute(
        "SELECT category, amount FROM expenses WHERE account_id = ?", (account_id,))
    data = cursor.fetchall()
    categories = [item[0] for item in data]
    amounts = [item[1] for item in data]

    plt.figure(figsize=(8, 6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title('Expense Distribution by Category')

    # Embed the matplotlib figure in the Tkinter window
    canvas = FigureCanvasTkAgg(plt.gcf(), master=visualization_tab)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()


# Create buttons to generate bar, line, and pie charts
bar_chart_button = tk.Button(visualization_tab, text="Generate Income Bar Chart",
                             command=lambda: create_bar_chart(summary_account_entry.get(), conn))
bar_chart_button.pack()

line_chart_button = tk.Button(visualization_tab, text="Generate Income Line Chart",
                              command=lambda: create_line_chart(summary_account_entry.get(), conn))
line_chart_button.pack()

pie_chart_button = tk.Button(visualization_tab, text="Generate Expense Pie Chart",
                             command=lambda: create_pie_chart(summary_account_entry.get(), conn))
pie_chart_button.pack()

# Function to calculate and display budget analysis


def budget_analysis(account_name, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()[0]

    cursor.execute(
        "SELECT SUM(amount) FROM income WHERE account_id = ?", (account_id,))
    total_income = cursor.fetchone()[0]
    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE account_id = ?", (account_id,))
    total_expenses = cursor.fetchone()[0]
    net_income = total_income - total_expenses

    analysis_text.config(state=tk.NORMAL)
    analysis_text.delete(1.0, tk.END)
    analysis_text.insert(
        tk.END, f"Budget Analysis for Account: {account_name}\n\n")
    analysis_text.insert(tk.END, f"Total Income: ${total_income:.2f}\n")
    analysis_text.insert(tk.END, f"Total Expenses: ${total_expenses:.2f}\n")
    analysis_text.insert(tk.END, f"Net Income: ${net_income:.2f}\n")
    analysis_text.config(state=tk.DISABLED)


# Create a tab for budget analysis
analysis_tab = ttk.Frame(notebook)
notebook.add(analysis_tab, text="Budget Analysis")

analysis_account_label = tk.Label(analysis_tab, text="Account Name:")
analysis_account_label.pack()

analysis_account_entry = tk.Entry(analysis_tab)
analysis_account_entry.pack()

analysis_text = tk.Text(analysis_tab, height=10, width=40)
analysis_text.pack()

analysis_button = tk.Button(analysis_tab, text="Calculate Budget Analysis",
                            command=lambda: budget_analysis(analysis_account_entry.get(), conn))
analysis_button.pack()

# Function to create or update a financial goal


def set_goal(account_name, goal_name, target_amount, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()[0]

    cursor.execute("INSERT OR REPLACE INTO goals (account_id, category, amount, currency, date) VALUES (?, ?, ?, ?, ?)",
                   (account_id, goal_name, target_amount, 'USD', 'target_date_here'))
    conn.commit()

    # Calculate progress towards the goal
    cursor.execute(
        "SELECT SUM(amount) FROM income WHERE account_id = ?", (account_id,))
    total_income = cursor.fetchone()[0]
    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE account_id = ?", (account_id,))
    total_expenses = cursor.fetchone()[0]
    progress = total_income - total_expenses

    goal_progress_text.config(state=tk.NORMAL)
    goal_progress_text.delete(1.0, tk.END)
    goal_progress_text.insert(tk.END, f"Goal: {goal_name}\n")
    goal_progress_text.insert(tk.END, f"Target Amount: ${target_amount:.2f}\n")
    goal_progress_text.insert(tk.END, f"Progress: ${progress:.2f}\n")
    goal_progress_text.config(state=tk.DISABLED)


# Create a tab for setting and tracking financial goals
goals_tab = ttk.Frame(notebook)
notebook.add(goals_tab, text="Goals")

goal_account_label = tk.Label(goals_tab, text="Account Name:")
goal_account_label.pack()

goal_account_entry = tk.Entry(goals_tab)
goal_account_entry.pack()

goal_name_label = tk.Label(goals_tab, text="Goal Name:")
goal_name_label.pack()

goal_name_entry = tk.Entry(goals_tab)
goal_name_entry.pack()

target_amount_label = tk.Label(goals_tab, text="Target Amount:")
target_amount_label.pack()

target_amount_entry = tk.Entry(goals_tab)
target_amount_entry.pack()

goal_button = tk.Button(goals_tab, text="Set Goal", command=lambda: set_goal(
    goal_account_entry.get(), goal_name_entry.get(), float(target_amount_entry.get()), conn))
goal_button.pack()

goal_progress_text = tk.Text(goals_tab, height=5, width=40)
goal_progress_text.pack()

root.mainloop()
