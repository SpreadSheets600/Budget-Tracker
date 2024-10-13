import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import time
import os
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ttkbootstrap import Style
import csv
from datetime import datetime, timedelta

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
            currency TEXT, target_date TEXT, FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    """
    )
    cursor.execute("INSERT OR IGNORE INTO accounts (name) VALUES (?)", (account_name,))
    conn.commit()
    return conn


def show_error(message):
    messagebox.showerror("Error", message)


def add_transaction(account_name, category, amount, transaction_type, conn, date=None):
    if not account_name or not category or amount <= 0:
        show_error(
            "Please provide valid inputs for account name, category, and amount."
        )
        return

    timestamp = date if date else time.strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()

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
    update_summary_text(account_name, conn)


def create_transaction_widgets(tab, transaction_type, conn):
    labels = ["Account Name:", "Category:", "Amount:", "Date (YYYY-MM-DD):"]
    entries = [ctk.CTkEntry(tab) for _ in range(4)]

    for i, label in enumerate(labels):
        ctk.CTkLabel(tab, text=label).pack(pady=5)
        entries[i].pack(pady=5)

    add_transaction_button = ctk.CTkButton(
        tab,
        text=f"Add {transaction_type.capitalize()}",
        command=lambda: add_transaction(
            entries[0].get(),
            entries[1].get(),
            float(entries[2].get() or 0),
            transaction_type,
            conn,
            entries[3].get(),
        ),
    )
    add_transaction_button.pack(pady=10)


def update_summary_text(account_name, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()

    if not account_id:
        show_error(f"No account found for '{account_name}'")
        return

    account_id = account_id[0]

    summary_text.configure(state=tk.NORMAL)
    summary_text.delete(1.0, tk.END)
    summary_text.insert(tk.END, f"Summary for Account: {account_name}\n\n")

    for transaction_type in ["income", "expenses"]:
        cursor.execute(
            f"SELECT category, SUM(amount) FROM {transaction_type} WHERE account_id = ? GROUP BY category",
            (account_id,),
        )
        data = cursor.fetchall()

        summary_text.insert(tk.END, f"{transaction_type.capitalize()}:\n")
        total = 0
        for item in data:
            summary_text.insert(tk.END, f"{item[0]}: ${item[1]:.2f}\n")
            total += item[1]
        summary_text.insert(tk.END, f"Total {transaction_type}: ${total:.2f}\n\n")

    # Calculate net income
    cursor.execute("SELECT SUM(amount) FROM income WHERE account_id = ?", (account_id,))
    total_income = cursor.fetchone()[0] or 0
    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE account_id = ?", (account_id,)
    )
    total_expenses = cursor.fetchone()[0] or 0
    net_income = total_income - total_expenses
    summary_text.insert(tk.END, f"Net Income: ${net_income:.2f}\n\n")

    # Display goals
    cursor.execute(
        "SELECT category, amount, target_date FROM goals WHERE account_id = ?",
        (account_id,),
    )
    goals = cursor.fetchall()
    summary_text.insert(tk.END, "Financial Goals:\n")
    for goal in goals:
        summary_text.insert(tk.END, f"{goal[0]}: ${goal[1]:.2f} (Target: {goal[2]})\n")

    summary_text.configure(state=tk.DISABLED)


def create_bar_chart(account_name, conn):
    plt.clf()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()

    if not account_id:
        show_error(f"No account found for '{account_name}'")
        return

    account_id = account_id[0]

    # Fetch income and expense data
    cursor.execute(
        "SELECT category, SUM(amount) FROM income WHERE account_id = ? GROUP BY category",
        (account_id,),
    )
    income_data = cursor.fetchall()
    cursor.execute(
        "SELECT category, SUM(amount) FROM expenses WHERE account_id = ? GROUP BY category",
        (account_id,),
    )
    expense_data = cursor.fetchall()

    if not income_data and not expense_data:
        show_error("No data available for the selected account.")
        return

    # Prepare data for plotting
    income_categories = [item[0] for item in income_data]
    income_amounts = [item[1] for item in income_data]
    expense_categories = [item[0] for item in expense_data]
    expense_amounts = [item[1] for item in expense_data]

    # Create subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

    # Plot income
    ax1.bar(income_categories, income_amounts, color="g", alpha=0.7)
    ax1.set_title("Income by Category")
    ax1.set_ylabel("Amount (USD)")
    ax1.tick_params(axis="x", rotation=45)

    # Plot expenses
    ax2.bar(expense_categories, expense_amounts, color="r", alpha=0.7)
    ax2.set_title("Expenses by Category")
    ax2.set_ylabel("Amount (USD)")
    ax2.tick_params(axis="x", rotation=45)

    plt.tight_layout()

    # Clear previous chart and display the new one
    for widget in visualization_tab.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=visualization_tab)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10, expand=True, fill="both")


def create_pie_chart(account_name, conn):
    plt.clf()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()

    if not account_id:
        show_error(f"No account found for '{account_name}'")
        return

    account_id = account_id[0]

    # Fetch expense data
    cursor.execute(
        "SELECT category, SUM(amount) FROM expenses WHERE account_id = ? GROUP BY category",
        (account_id,),
    )
    expense_data = cursor.fetchall()

    if not expense_data:
        show_error("No expense data available for the selected account.")
        return

    # Prepare data for plotting
    categories = [item[0] for item in expense_data]
    amounts = [item[1] for item in expense_data]

    # Create pie chart
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title("Expense Distribution")

    # Clear previous chart and display the new one
    for widget in visualization_tab.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=visualization_tab)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10, expand=True, fill="both")


def create_line_chart(account_name, conn):
    plt.clf()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()

    if not account_id:
        show_error(f"No account found for '{account_name}'")
        return

    account_id = account_id[0]

    # Fetch income and expense data
    cursor.execute(
        "SELECT date, SUM(amount) FROM income WHERE account_id = ? GROUP BY date",
        (account_id,),
    )
    income_data = cursor.fetchall()
    cursor.execute(
        "SELECT date, SUM(amount) FROM expenses WHERE account_id = ? GROUP BY date",
        (account_id,),
    )
    expense_data = cursor.fetchall()

    if not income_data and not expense_data:
        show_error("No data available for the selected account.")
        return

    # Prepare data for plotting
    income_dates = [
        datetime.strptime(item[0], "%Y-%m-%d %H:%M:%S").date() for item in income_data
    ]
    income_amounts = [item[1] for item in income_data]
    expense_dates = [
        datetime.strptime(item[0], "%Y-%m-%d %H:%M:%S").date() for item in expense_data
    ]
    expense_amounts = [item[1] for item in expense_data]

    # Create line chart
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(income_dates, income_amounts, label="Income", marker="o")
    ax.plot(expense_dates, expense_amounts, label="Expenses", marker="o")
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount (USD)")
    ax.set_title("Income and Expenses Over Time")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Clear previous chart and display the new one
    for widget in visualization_tab.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=visualization_tab)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10, expand=True, fill="both")


def budget_analysis(account_name, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()

    if not account_id:
        show_error(f"No account found for '{account_name}'")
        return

    account_id = account_id[0]

    # Fetch income and expense data
    cursor.execute("SELECT SUM(amount) FROM income WHERE account_id = ?", (account_id,))
    total_income = cursor.fetchone()[0] or 0
    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE account_id = ?", (account_id,)
    )
    total_expenses = cursor.fetchone()[0] or 0

    # Calculate net income and savings rate
    net_income = total_income - total_expenses
    savings_rate = (net_income / total_income * 100) if total_income > 0 else 0

    # Fetch top expense categories
    cursor.execute(
        """
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE account_id = ?
        GROUP BY category
        ORDER BY total DESC
        LIMIT 3
    """,
        (account_id,),
    )
    top_expenses = cursor.fetchall()

    # Prepare analysis text
    analysis = f"Budget Analysis for {account_name}:\n\n"
    analysis += f"Total Income: ${total_income:.2f}\n"
    analysis += f"Total Expenses: ${total_expenses:.2f}\n"
    analysis += f"Net Income: ${net_income:.2f}\n"
    analysis += f"Savings Rate: {savings_rate:.2f}%\n\n"
    analysis += "Top 3 Expense Categories:\n"
    for category, amount in top_expenses:
        percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
        analysis += (
            f"- {category}: ${amount:.2f} ({percentage:.2f}% of total expenses)\n"
        )

    # Provide some basic advice
    if savings_rate < 20:
        analysis += "\nConsider reducing expenses to increase your savings rate."
    elif savings_rate > 50:
        analysis += "\nGreat job on savings! Consider investing for long-term growth."

    if total_expenses > total_income:
        analysis += "\nWarning: Your expenses exceed your income. Review your budget to reduce expenses."

    # Update the analysis text widget
    analysis_text.configure(state=tk.NORMAL)
    analysis_text.delete(1.0, tk.END)
    analysis_text.insert(tk.END, analysis)
    analysis_text.configure(state=tk.DISABLED)


def export_to_csv(account_name, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()

    if not account_id:
        show_error(f"No account found for '{account_name}'")
        return

    account_id = account_id[0]

    # Fetch all data
    cursor.execute(
        "SELECT 'Income' as type, category, amount, currency, date FROM income WHERE account_id = ? "
        "UNION ALL "
        "SELECT 'Expense' as type, category, amount, currency, date FROM expenses WHERE account_id = ? "
        "UNION ALL "
        "SELECT 'Goal' as type, category, amount, currency, target_date FROM goals WHERE account_id = ?",
        (account_id, account_id, account_id),
    )
    data = cursor.fetchall()

    if not data:
        show_error("No data available to export.")
        return

    # Ask user for save location
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
    )
    if not file_path:
        return  # User cancelled the save operation

    # Write data to CSV file
    with open(file_path, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(
            ["Type", "Category", "Amount", "Currency", "Date"]
        )  # Header row
        csv_writer.writerows(data)

    messagebox.showinfo(
        "Export Successful", f"Data exported successfully to {file_path}"
    )


def add_goal(account_name, category, amount, target_date, conn):
    if not account_name or not category or amount <= 0 or not target_date:
        show_error(
            "Please provide valid inputs for account name, category, amount, and target date."
        )
        return

    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
    account_id = cursor.fetchone()

    if not account_id:
        cursor.execute("INSERT INTO accounts (name) VALUES (?)", (account_name,))
        conn.commit()
        cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
        account_id = cursor.fetchone()

    account_id = account_id[0]
    cursor.execute(
        "INSERT INTO goals (account_id, category, amount, currency, target_date) "
        "VALUES (?, ?, ?, ?, ?)",
        (account_id, category, amount, "USD", target_date),
    )
    conn.commit()
    update_summary_text(account_name, conn)


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

# Initialize database connection
conn = create_or_open_database("Default")

# Create widgets for Income and Expense tabs
create_transaction_widgets(income_tab, "income", conn)
create_transaction_widgets(expense_tab, "expenses", conn)

# Create widgets for Goals tab
ctk.CTkLabel(goals_tab, text="Account Name:").pack(pady=5)
goal_account_entry = ctk.CTkEntry(goals_tab)
goal_account_entry.pack(pady=5)

ctk.CTkLabel(goals_tab, text="Goal Category:").pack(pady=5)
goal_category_entry = ctk.CTkEntry(goals_tab)
goal_category_entry.pack(pady=5)

ctk.CTkLabel(goals_tab, text="Goal Amount:").pack(pady=5)
goal_amount_entry = ctk.CTkEntry(goals_tab)
goal_amount_entry.pack(pady=5)

ctk.CTkLabel(goals_tab, text="Target Date (YYYY-MM-DD):").pack(pady=5)
goal_date_entry = ctk.CTkEntry(goals_tab)
goal_date_entry.pack(pady=5)

add_goal_button = ctk.CTkButton(
    goals_tab,
    text="Add Goal",
    command=lambda: add_goal(
        goal_account_entry.get(),
        goal_category_entry.get(),
        float(goal_amount_entry.get() or 0),
        goal_date_entry.get(),
        conn,
    ),
)
add_goal_button.pack(pady=10)

# Create widgets for Visualization tab
ctk.CTkLabel(visualization_tab, text="Account Name:").pack(pady=5)
viz_account_entry = ctk.CTkEntry(visualization_tab)
viz_account_entry.pack(pady=5)

bar_chart_button = ctk.CTkButton(
    visualization_tab,
    text="Show Bar Chart",
    command=lambda: create_bar_chart(viz_account_entry.get(), conn),
)
bar_chart_button.pack(pady=5)

pie_chart_button = ctk.CTkButton(
    visualization_tab,
    text="Show Pie Chart",
    command=lambda: create_pie_chart(viz_account_entry.get(), conn),
)
pie_chart_button.pack(pady=5)

line_chart_button = ctk.CTkButton(
    visualization_tab,
    text="Show Line Chart",
    command=lambda: create_line_chart(viz_account_entry.get(), conn),
)
line_chart_button.pack(pady=5)

# Create widgets for Summary tab
ctk.CTkLabel(summary_tab, text="Account Name:").pack(pady=5)
summary_account_entry = ctk.CTkEntry(summary_tab)
summary_account_entry.pack(pady=5)

summary_text = ctk.CTkTextbox(summary_tab, height=400, width=500)
summary_text.pack(pady=10)

display_summary_button = ctk.CTkButton(
    summary_tab,
    text="Display Summary",
    command=lambda: update_summary_text(summary_account_entry.get(), conn),
)
display_summary_button.pack(pady=10)

# Create widgets for Budget Analysis tab
ctk.CTkLabel(analysis_tab, text="Account Name:").pack(pady=5)
analysis_account_entry = ctk.CTkEntry(analysis_tab)
analysis_account_entry.pack(pady=5)

analysis_text = ctk.CTkTextbox(analysis_tab, height=400, width=500)
analysis_text.pack(pady=10)

analysis_button = ctk.CTkButton(
    analysis_tab,
    text="Calculate Budget Analysis",
    command=lambda: budget_analysis(analysis_account_entry.get(), conn),
)
analysis_button.pack(pady=10)

# Create Export to CSV button (you can place this in any tab or create a new tab for data management)
export_button = ctk.CTkButton(
    summary_tab,
    text="Export to CSV",
    command=lambda: export_to_csv(summary_account_entry.get(), conn),
)
export_button.pack(pady=10)

# Load user data and initialize app with accounts
user_data = load_to_json()
if user_data:
    for account in user_data.get("accounts", []):
        conn = create_or_open_database(account)

root.mainloop()
