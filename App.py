import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import sqlite3
import time
import os
import matplotlib.pyplot as plt
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("Dark")
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

    def add_income(self):
        account = self.income_account_entry.get()
        category = self.income_category_entry.get()
        amount = self.income_amount_entry.get()
        
        # Add income to database
        conn = create_or_open_database(account)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO income (account_id, category, amount, currency, date) VALUES ((SELECT id FROM accounts WHERE name = ?), ?, ?, 'USD', ?)",
                       (account, category, amount, time.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        # Clear input fields
        self.income_account_entry.delete(0, 'end')
        self.income_category_entry.delete(0, 'end')
        self.income_amount_entry.delete(0, 'end')

        # Show confirmation message
        ctk.CTkMessagebox(title="Success", message="Income added successfully!")

    def add_expense(self):
        account = self.expense_account_entry.get()
        category = self.expense_category_entry.get()
        amount = self.expense_amount_entry.get()
        
        # Add expense to database
        conn = create_or_open_database(account)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (account_id, category, amount, currency, date) VALUES ((SELECT id FROM accounts WHERE name = ?), ?, ?, 'USD', ?)",
                       (account, category, amount, time.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        # Clear input fields
        self.expense_account_entry.delete(0, 'end')
        self.expense_category_entry.delete(0, 'end')
        self.expense_amount_entry.delete(0, 'end')

        # Show confirmation message
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
        # Implement summary update logic here
        ctk.CTkMessagebox(title="Info", message="Summary update not implemented yet.")

    def perform_analysis(self):
        # Implement budget analysis logic here
        ctk.CTkMessagebox(title="Info", message="Budget analysis not implemented yet.")

if __name__ == "__main__":
    app = BudgetTrackerApp()
    app.mainloop()