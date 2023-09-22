import tkinter as tk
from tkinter import ttk
import csv

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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

# Create a frame for the "Visualization" tab
visualization_tab = ttk.Frame(notebook)
notebook.add(visualization_tab, text="Visualization")

# Function to add income
def add_income(account_name, category, amount):
    if account_name not in budget['Accounts']:
        create_account(account_name)
    data = load_csv_data(account_name, 'income')
    data.append({'Category': category, 'Amount': amount, 'Currency': 'USD'})
    save_csv_data(account_name, data, 'income')
    update_summary_text(account_name)

# Function to add expense
def add_expense(account_name, category, amount):
    if account_name not in budget['Accounts']:
        create_account(account_name)
    data = load_csv_data(account_name, 'expenses')
    data.append({'Category': category, 'Amount': amount, 'Currency': 'USD'})
    save_csv_data(account_name, data, 'expenses')
    update_summary_text(account_name)

# Function to add goal
def add_goal(account_name, category, amount):
    data = load_csv_data(account_name, 'goals')
    data.append({'Category': category, 'Amount': amount, 'Currency': 'USD'})
    save_csv_data(account_name, data, 'goals')
    update_summary_text(account_name)

# Create labels and entry fields for income
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

# Create button for adding income
add_income_button = tk.Button(income_tab, text="Add Income", command=lambda: add_income(account_name_entry_income.get(), category_entry_income.get(), float(amount_entry_income.get())))
add_income_button.pack()

# Create labels and entry fields for expenses
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

# Create button for adding expense
add_expense_button = tk.Button(expense_tab, text="Add Expense", command=lambda: add_expense(account_name_entry_expense.get(), category_entry_expense.get(), float(amount_entry_expense.get())))
add_expense_button.pack()

# Create labels and entry fields for goals
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

# Create button for adding goal
add_goal_button = tk.Button(goals_tab, text="Set Goal", command=lambda: add_goal(account_name_entry_goals.get(), category_entry_goals.get(), float(amount_entry_goals.get())))
add_goal_button.pack()

# Function to create an account and CSV files
def create_account(account_name):
    budget['Accounts'][account_name] = {'Income': [], 'Expenses': [], 'Goals': []}
    create_account_csv(account_name)

# Function to create account CSV files
def create_account_csv(account_name):
    for data_type in ['income', 'expenses', 'goals']:
        filename = f'{account_name}_{data_type}.csv'
        with open(filename, mode='w', newline='') as file:
            fieldnames = ['Category', 'Amount', 'Currency']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

# Function to load data from CSV file
def load_csv_data(account_name, data_type):
    data = []
    filename = f'{account_name}_{data_type}.csv'
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

# Function to save data to CSV file
def save_csv_data(account_name, data, data_type):
    filename = f'{account_name}_{data_type}.csv'
    with open(filename, mode='w', newline='') as csv_file:
        fieldnames = ['Category', 'Amount', 'Currency']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

# Create a frame for the "Display Summary" tab
summary_tab = ttk.Frame(notebook)
notebook.add(summary_tab, text="Display Summary")

# Label and entry field for account name in the "Display Summary" tab
summary_account_label = tk.Label(summary_tab, text="Account Name:")
summary_account_label.pack()

summary_account_entry = tk.Entry(summary_tab)
summary_account_entry.pack()

# Text widget to display the summary
summary_text = tk.Text(summary_tab, height=10, width=40)
summary_text.pack()

# Function to update the summary text
def update_summary_text(account_name):
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

# Button to display the summary in the "Display Summary" tab
display_summary_button = tk.Button(summary_tab, text="Display Summary", command=lambda: update_summary_text(summary_account_entry.get()))
display_summary_button.pack()

def create_bar_chart(account_name):
    income_data = load_csv_data(account_name, 'income')
    categories = [item['Category'] for item in income_data]
    amounts = [item['Amount'] for item in income_data]

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

# Function to create a pie chart
def create_pie_chart(account_name):
    expenses_data = load_csv_data(account_name, 'expenses')
    categories = [item['Category'] for item in expenses_data]
    amounts = [item['Amount'] for item in expenses_data]

    plt.figure(figsize=(8, 6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title('Expense Distribution by Category')

    # Embed the matplotlib figure in the Tkinter window
    canvas = FigureCanvasTkAgg(plt.gcf(), master=visualization_tab)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()

# Create a button to generate a bar chart
bar_chart_button = tk.Button(visualization_tab, text="Generate Income Bar Chart", command=lambda: create_bar_chart(account_name_entry_income.get()))
bar_chart_button.pack()

# Create a button to generate a pie chart
pie_chart_button = tk.Button(visualization_tab, text="Generate Expense Pie Chart", command=lambda: create_pie_chart(account_name_entry_income.get()))
pie_chart_button.pack()

root.mainloop()
