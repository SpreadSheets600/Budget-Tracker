import tkinter as tk
from tkinter import ttk
import csv

budget = {'Accounts': {}}

# Create the main window
root = tk.Tk()
root.title("Budget Tracker")

# Create a notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Create tabs for adding income and expenses
income_tab = ttk.Frame(notebook)
expense_tab = ttk.Frame(notebook)
goals_tab = ttk.Frame(notebook)

notebook.add(income_tab, text="Add Income")
notebook.add(expense_tab, text="Add Expense")
notebook.add(goals_tab, text="Goals")


# Labels and entry fields for income
account_name_label_income = tk.Label(income_tab, text="Account Name:")
account_name_label_income.pack()

account_name_entry_income = tk.Entry(income_tab)
account_name_entry_income.pack()

category_label_income = tk.Label(income_tab, text="Category:")
category_label_income.pack()

category_entry_income = tk.Entry(income_tab)
category_entry_income.pack()

amount_label_income = tk.Label(income_tab, text="Amount:")
amount_label_income.pack()

amount_entry_income = tk.Entry(income_tab)
amount_entry_income.pack()

def add_income(account_name, category, amount):
    if account_name not in budget['Accounts']:
        create_account(account_name)
    data = load_csv_data(account_name, 'income')
    data.append({'Category': category, 'Amount': amount, 'Currency': 'USD'})
    save_csv_data(account_name, data, 'income')


def add_expense(account_name, category, amount):
    if account_name not in budget['Accounts']:
        create_account(account_name)
    data = load_csv_data(account_name, 'expenses')
    data.append({'Category': category, 'Amount': amount, 'Currency': 'USD'})
    save_csv_data(account_name, data, 'expenses')



add_income_button = tk.Button(income_tab, text="Add Income", command=lambda: add_income(account_name_entry_income.get(), category_entry_income.get(), float(amount_entry_income.get())))
add_income_button.pack()

# Labels and entry fields for expenses
account_name_label_expense = tk.Label(expense_tab, text="Account Name:")
account_name_label_expense.pack()

account_name_entry_expense = tk.Entry(expense_tab)
account_name_entry_expense.pack()

category_label_expense = tk.Label(expense_tab, text="Category:")
category_label_expense.pack()

category_entry_expense = tk.Entry(expense_tab)
category_entry_expense.pack()

amount_label_expense = tk.Label(expense_tab, text="Amount:")
amount_label_expense.pack()

amount_entry_expense = tk.Entry(expense_tab)
amount_entry_expense.pack()

add_expense_button = tk.Button(expense_tab, text="Add Expense", command=lambda: add_expense(account_name_entry_expense.get(), category_entry_expense.get(), float(amount_entry_expense.get())))
add_expense_button.pack()

# Labels and entry fields for goals
account_name_label_goals = tk.Label(goals_tab, text="Account Name:")
account_name_label_goals.pack()

account_name_entry_goals = tk.Entry(goals_tab)
account_name_entry_goals.pack()

category_label_goals = tk.Label(goals_tab, text="Category:")
category_label_goals.pack()

category_entry_goals = tk.Entry(goals_tab)
category_entry_goals.pack()

amount_label_goals = tk.Label(goals_tab, text="Amount:")
amount_label_goals.pack()

amount_entry_goals = tk.Entry(goals_tab)
amount_entry_goals.pack()

def add_goal(account_name, category, amount):
    data = load_csv_data(account_name, 'goals')
    data.append({'Category': category, 'Amount': amount, 'Currency': 'USD'})
    save_csv_data(account_name, data, 'goals')

add_goal_button = tk.Button(goals_tab, text="Set Goal", command=lambda: add_goal(account_name_entry_goals.get(), category_entry_goals.get(), float(amount_entry_goals.get())))
add_goal_button.pack()

def create_account(account_name):
    budget['Accounts'][account_name] = {'Income': [], 'Expenses': [], 'Goals': []}
    create_account_csv(account_name)

def create_account_csv(account_name):
    with open(f'{account_name}_income.csv', mode='w', newline='') as income_file:
        fieldnames = ['Category', 'Amount', 'Currency']
        writer = csv.DictWriter(income_file, fieldnames=fieldnames)
        writer.writeheader()

    with open(f'{account_name}_expenses.csv', mode='w', newline='') as expenses_file:
        fieldnames = ['Category', 'Amount', 'Currency']
        writer = csv.DictWriter(expenses_file, fieldnames=fieldnames)
        writer.writeheader()

    with open(f'{account_name}_goals.csv', mode='w', newline='') as goals_file:
        fieldnames = ['Category', 'Amount', 'Currency']
        writer = csv.DictWriter(goals_file, fieldnames=fieldnames)
        writer.writeheader()

def load_csv_data(account_name, data_type):
    data = []
    filename = f'{account_name}_{data_type.lower()}.csv'
    try:
        with open(filename, mode='r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:

                row['Amount'] = float(row['Amount'])
                data.append(row)
    except FileNotFoundError:
        pass
    budget['Accounts'][account_name][data_type] = data
    return data


def save_csv_data(account_name, data, data_type):
    filename = f'{account_name}_{data_type.lower()}.csv'
    with open(filename, mode='w', newline='') as csv_file:
        fieldnames = ['Category', 'Amount', 'Currency']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

def update_summary_text():
    account_name = summary_account_entry.get()
    summary_text.config(state=tk.NORMAL)
    summary_text.delete(1.0, tk.END)
    summary_text.insert(tk.END, f"Summary for Account: {account_name}\n\n")
    summary_text.insert(tk.END, "Income:\n")
    income_data = load_csv_data(account_name, 'income')
    for item in income_data:
        summary_text.insert(tk.END, f"{item['Category']}: ${item['Amount']:.2f}\n")
    summary_text.insert(tk.END, "\nExpenses:\n")
    expenses_data = load_csv_data(account_name, 'expenses')
    for item in expenses_data:
        summary_text.insert(tk.END, f"{item['Category']}: ${item['Amount']:.2f}\n")
    summary_text.insert(tk.END, "\nGoals:\n")
    goals_data = load_csv_data(account_name, 'goals')
    for item in goals_data:
        summary_text.insert(tk.END, f"{item['Category']}: ${item['Amount']:.2f}\n")
    summary_text.config(state=tk.DISABLED)

# Create a frame for the "Display Summary" tab
summary_tab = ttk.Frame(notebook)
notebook.add(summary_tab, text="Display Summary")

# Label and entry field for account name in the "Display Summary" tab
summary_account_label = tk.Label(summary_tab, text="Account Name:")
summary_account_label.pack()

summary_account_entry = tk.Entry(summary_tab)
summary_account_entry.pack()

# Button to display the summary in the "Display Summary" tab
display_summary_button = tk.Button(summary_tab, text="Display Summary", command=lambda: update_summary_text())
display_summary_button.pack()

# Text widget to display the summary
summary_text = tk.Text(summary_tab, height=10, width=40)
summary_text.pack()
summary_text.config(state=tk.DISABLED)

root.mainloop()
