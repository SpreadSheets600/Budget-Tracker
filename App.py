import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY, name TEXT UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY, account_id INTEGER, category TEXT, amount REAL,
            currency TEXT, date TEXT, FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY, account_id INTEGER, category TEXT, amount REAL,
            currency TEXT, date TEXT, FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY, account_id INTEGER, category TEXT, amount REAL,
            currency TEXT, date TEXT, FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO accounts (name) VALUES (?)", (account_name,))
    conn.commit()
    return conn

# Helper function for error notifications
def show_error(message):
    messagebox.showerror("Error", message)

class BudgetTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Budget Tracker")
        self.geometry("1000x600")
        self.minsize(800, 600)

        self.create_widgets()

    def create_widgets(self):
        # Create main layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Budget Tracker", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, text="Add Income", command=self.show_income_tab)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame, text="Add Expense", command=self.show_expense_tab)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_3 = ctk.CTkButton(self.sidebar_frame, text="Visualization", command=self.show_visualization_tab)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        self.sidebar_button_4 = ctk.CTkButton(self.sidebar_frame, text="Summary", command=self.show_summary_tab)
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)

        self.sidebar_button_5 = ctk.CTkButton(self.sidebar_frame, text="Analysis", command=self.show_analysis_tab)
        self.sidebar_button_5.grid(row=5, column=0, padx=20, pady=10)

        # Create main content area
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Create tabs (frames)
        self.income_tab = self.create_income_tab()
        self.expense_tab = self.create_expense_tab()
        self.visualization_tab = self.create_visualization_tab()
        self.summary_tab = self.create_summary_tab()
        self.analysis_tab = self.create_analysis_tab()

        # Show income tab by default
        self.show_income_tab()

    def create_income_tab(self):
        frame = ctk.CTkFrame(self.main_frame)
        label = ctk.CTkLabel(frame, text="Add Income", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=(20, 40))

        # Create input fields
        self.income_account_entry = self.create_input_field(frame, "Account Name")
        self.income_category_entry = self.create_input_field(frame, "Category")
        self.income_amount_entry = self.create_input_field(frame, "Amount")

        button = ctk.CTkButton(frame, text="Add Income", command=self.add_income)
        button.pack(pady=(20, 0))

        return frame

    def create_expense_tab(self):
        frame = ctk.CTkFrame(self.main_frame)
        label = ctk.CTkLabel(frame, text="Add Expense", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=(20, 40))

        # Create input fields
        self.expense_account_entry = self.create_input_field(frame, "Account Name")
        self.expense_category_entry = self.create_input_field(frame, "Category")
        self.expense_amount_entry = self.create_input_field(frame, "Amount")

        button = ctk.CTkButton(frame, text="Add Expense", command=self.add_expense)
        button.pack(pady=(20, 0))

        return frame

    def create_visualization_tab(self):
        frame = ctk.CTkFrame(self.main_frame)
        label = ctk.CTkLabel(frame, text="Visualization", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=(20, 20))

        # Create a frame for chart options
        options_frame = ctk.CTkFrame(frame)
        options_frame.pack(pady=(0, 20), padx=20, fill="x")

        # Account selection
        account_label = ctk.CTkLabel(options_frame, text="Account:")
        account_label.pack(side="left", padx=(0, 10))
        self.viz_account_entry = ctk.CTkEntry(options_frame, width=120)
        self.viz_account_entry.pack(side="left", padx=(0, 20))

        # Chart type selection
        chart_label = ctk.CTkLabel(options_frame, text="Chart Type:")
        chart_label.pack(side="left", padx=(0, 10))
        self.chart_type_var = ctk.StringVar(value="Bar")
        chart_type_menu = ctk.CTkOptionMenu(options_frame, values=["Bar", "Pie", "Line"], variable=self.chart_type_var)
        chart_type_menu.pack(side="left", padx=(0, 20))

        # Data type selection
        data_label = ctk.CTkLabel(options_frame, text="Data:")
        data_label.pack(side="left", padx=(0, 10))
        self.data_type_var = ctk.StringVar(value="Income")
        data_type_menu = ctk.CTkOptionMenu(options_frame, values=["Income", "Expenses"], variable=self.data_type_var)
        data_type_menu.pack(side="left")

        # Create a frame for the chart
        self.chart_frame = ctk.CTkFrame(frame)
        self.chart_frame.pack(pady=(0, 20), padx=20, fill="both", expand=True)

        # Button to generate chart
        generate_button = ctk.CTkButton(frame, text="Generate Chart", command=self.generate_chart)
        generate_button.pack(pady=(0, 20))

        return frame

    def create_summary_tab(self):
        frame = ctk.CTkFrame(self.main_frame)
        label = ctk.CTkLabel(frame, text="Summary", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=(20, 40))

        self.summary_text = ctk.CTkTextbox(frame, height=300, width=500)
        self.summary_text.pack(pady=(0, 20))

        button = ctk.CTkButton(frame, text="Update Summary", command=self.update_summary)
        button.pack(pady=(0, 20))

        return frame

    def create_analysis_tab(self):
        frame = ctk.CTkFrame(self.main_frame)
        label = ctk.CTkLabel(frame, text="Budget Analysis", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=(20, 40))

        # Add analysis content here
        # For example, you can add a button to perform budget analysis
        button = ctk.CTkButton(frame, text="Perform Analysis", command=self.perform_analysis)
        button.pack(pady=(20, 0))

        return frame

    def create_input_field(self, parent, label_text):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=20, pady=5)

        label = ctk.CTkLabel(frame, text=label_text, width=100)
        label.pack(side="left", padx=(0, 10))

        entry = ctk.CTkEntry(frame)
        entry.pack(side="left", expand=True, fill="x")

        return entry

    def show_income_tab(self):
        self.show_frame(self.income_tab)

    def show_expense_tab(self):
        self.show_frame(self.expense_tab)

    def show_visualization_tab(self):
        self.show_frame(self.visualization_tab)

    def show_summary_tab(self):
        self.show_frame(self.summary_tab)

    def show_analysis_tab(self):
        self.show_frame(self.analysis_tab)

    def show_frame(self, frame):
        for widget in self.main_frame.winfo_children():
            widget.grid_forget()
        frame.grid(row=0, column=0, sticky="nsew")

    def add_transaction(self, account_name, category, amount, transaction_type):
        if not account_name or not category or amount <= 0:
            show_error("Please provide valid inputs for account name, category, and amount.")
            return

        conn = create_or_open_database(account_name)
        cursor = conn.cursor()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
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
        conn.close()

    def add_income(self):
        self.add_transaction(
            self.income_account_entry.get(),
            self.income_category_entry.get(),
            float(self.income_amount_entry.get() or 0),
            "income"
        )
        # Clear input fields and show confirmation message
        self.income_account_entry.delete(0, 'end')
        self.income_category_entry.delete(0, 'end')
        self.income_amount_entry.delete(0, 'end')
        ctk.CTkMessagebox(title="Success", message="Income added successfully!")

    def add_expense(self):
        self.add_transaction(
            self.expense_account_entry.get(),
            self.expense_category_entry.get(),
            float(self.expense_amount_entry.get() or 0),
            "expenses"
        )
        # Clear input fields and show confirmation message
        self.expense_account_entry.delete(0, 'end')
        self.expense_category_entry.delete(0, 'end')
        self.expense_amount_entry.delete(0, 'end')
        ctk.CTkMessagebox(title="Success", message="Expense added successfully!")

    def generate_chart(self):
        account = self.viz_account_entry.get()
        chart_type = self.chart_type_var.get()
        data_type = self.data_type_var.get()

        if not account:
            ctk.CTkMessagebox(title="Error", message="Please enter an account name.")
            return

        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Fetch data from database
        conn = create_or_open_database(account)
        cursor = conn.cursor()
        cursor.execute(f"SELECT category, SUM(amount) FROM {data_type.lower()} WHERE account_id = (SELECT id FROM accounts WHERE name = ?) GROUP BY category", (account,))
        data = cursor.fetchall()
        conn.close()

        if not data:
            ctk.CTkMessagebox(title="Error", message=f"No {data_type.lower()} data found for this account.")
            return

        categories, amounts = zip(*data)

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 6))

        if chart_type == "Bar":
            ax.bar(categories, amounts)
            ax.set_xlabel("Categories")
            ax.set_ylabel("Amount (USD)")
            ax.set_title(f"{data_type} by Category")
            plt.xticks(rotation=45, ha='right')
        elif chart_type == "Pie":
            ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
            ax.set_title(f"{data_type} Distribution")
        elif chart_type == "Line":
            ax.plot(categories, amounts, marker='o')
            ax.set_xlabel("Categories")
            ax.set_ylabel("Amount (USD)")
            ax.set_title(f"{data_type} Trend")
            plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        # Embed the chart in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)
        canvas.draw()

    def update_summary(self):
        account = self.summary_account_entry.get()
        if not account:
            show_error("Please enter an account name.")
            return

        conn = create_or_open_database(account)
        cursor = conn.cursor()

        # Fetch income data
        cursor.execute("SELECT SUM(amount) FROM income WHERE account_id = (SELECT id FROM accounts WHERE name = ?)", (account,))
        total_income = cursor.fetchone()[0] or 0

        # Fetch expense data
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE account_id = (SELECT id FROM accounts WHERE name = ?)", (account,))
        total_expenses = cursor.fetchone()[0] or 0

        # Fetch top 5 income categories
        cursor.execute("SELECT category, SUM(amount) FROM income WHERE account_id = (SELECT id FROM accounts WHERE name = ?) GROUP BY category ORDER BY SUM(amount) DESC LIMIT 5", (account,))
        top_income_categories = cursor.fetchall()

        # Fetch top 5 expense categories
        cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE account_id = (SELECT id FROM accounts WHERE name = ?) GROUP BY category ORDER BY SUM(amount) DESC LIMIT 5", (account,))
        top_expense_categories = cursor.fetchall()

        conn.close()

        # Clear previous summary
        self.summary_text.delete("1.0", ctk.END)

        # Update summary text
        summary = f"Summary for Account: {account}\n\n"
        summary += f"Total Income: ${total_income:.2f}\n"
        summary += f"Total Expenses: ${total_expenses:.2f}\n"
        summary += f"Net Balance: ${total_income - total_expenses:.2f}\n\n"

        summary += "Top 5 Income Categories:\n"
        for category, amount in top_income_categories:
            summary += f"  {category}: ${amount:.2f}\n"

        summary += "\nTop 5 Expense Categories:\n"
        for category, amount in top_expense_categories:
            summary += f"  {category}: ${amount:.2f}\n"

        self.summary_text.insert(ctk.END, summary)

    def perform_analysis(self):
        account = self.analysis_account_entry.get()
        if not account:
            show_error("Please enter an account name.")
            return

        conn = create_or_open_database(account)
        cursor = conn.cursor()

        # Fetch total income and expenses
        cursor.execute("SELECT SUM(amount) FROM income WHERE account_id = (SELECT id FROM accounts WHERE name = ?)", (account,))
        total_income = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM expenses WHERE account_id = (SELECT id FROM accounts WHERE name = ?)", (account,))
        total_expenses = cursor.fetchone()[0] or 0

        # Calculate savings rate
        savings_rate = ((total_income - total_expenses) / total_income) * 100 if total_income > 0 else 0

        # Fetch top expense categories
        cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE account_id = (SELECT id FROM accounts WHERE name = ?) GROUP BY category ORDER BY SUM(amount) DESC LIMIT 3", (account,))
        top_expenses = cursor.fetchall()

        conn.close()

        # Prepare analysis text
        analysis = f"Budget Analysis for Account: {account}\n\n"
        analysis += f"Total Income: ${total_income:.2f}\n"
        analysis += f"Total Expenses: ${total_expenses:.2f}\n"
        analysis += f"Net Savings: ${total_income - total_expenses:.2f}\n"
        analysis += f"Savings Rate: {savings_rate:.2f}%\n\n"

        analysis += "Top 3 Expense Categories:\n"
        for category, amount in top_expenses:
            percentage = (amount / total_expenses) * 100 if total_expenses > 0 else 0
            analysis += f"  {category}: ${amount:.2f} ({percentage:.2f}% of total expenses)\n"

        # Provide some basic advice
        if savings_rate < 20:
            analysis += "\nAdvice: Consider reducing expenses to increase your savings rate."
        elif savings_rate >= 20 and savings_rate < 50:
            analysis += "\nAdvice: You're doing well! Consider setting specific savings goals."
        else:
            analysis += "\nAdvice: Excellent savings rate! Make sure you're investing wisely."

        # Update the analysis text
        self.analysis_text.configure(text=analysis)

if __name__ == "__main__":
    app = BudgetTrackerApp()
    
    # Loading user data and initializing app with accounts
    user_data = load_to_json()
    if user_data:
        for account in user_data.get("accounts", []):
            create_or_open_database(account)
    
    app.mainloop()