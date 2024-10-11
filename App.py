import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import sqlite3
import time
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Set the appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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
class BudgetTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Budget Tracker")
        self.geometry("800x600")
        
        # Create a notebook for tabs
        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        # Create tabs
        self.income_tab = self.notebook.add("Add Income")
        self.expense_tab = self.notebook.add("Add Expense")
        self.visualization_tab = self.notebook.add("Visualization")
        self.summary_tab = self.notebook.add("Display Summary")
        self.analysis_tab = self.notebook.add("Budget Analysis")
        
        # Create database connection
        self.conn = create_or_open_database("Default")
        
        # Initialize tabs
        self.init_transaction_tab(self.income_tab, 'income')
        self.init_transaction_tab(self.expense_tab, 'expenses')
        self.init_summary_tab()
        self.init_visualization_tab()
        self.init_analysis_tab()

    def init_transaction_tab(self, tab, transaction_type):
        account_name_label = ctk.CTkLabel(tab, text="Account Name:")
        account_name_label.pack(pady=5)
        
        account_name_entry = ctk.CTkEntry(tab, width=300)
        account_name_entry.pack(pady=5)
        
        category_label = ctk.CTkLabel(tab, text="Category:")
        category_label.pack(pady=5)
        
        category_entry = ctk.CTkEntry(tab, width=300)
        category_entry.pack(pady=5)
        
        amount_label = ctk.CTkLabel(tab, text="Amount:")
        amount_label.pack(pady=5)
        
        amount_entry = ctk.CTkEntry(tab, width=300)
        amount_entry.pack(pady=5)
        
        add_transaction_button = ctk.CTkButton(
            tab,
            text=f"Add {transaction_type.capitalize()}",
            command=lambda: self.add_transaction(
                account_name_entry.get(),
                category_entry.get(),
                amount_entry.get(),
                transaction_type
            )
        )
        add_transaction_button.pack(pady=10)

    def init_summary_tab(self):
        summary_account_label = ctk.CTkLabel(self.summary_tab, text="Account Name:")
        summary_account_label.pack(pady=5)
        
        self.summary_account_entry = ctk.CTkEntry(self.summary_tab, width=300)
        self.summary_account_entry.pack(pady=5)
        
        self.summary_text = ctk.CTkTextbox(self.summary_tab, height=200, width=400)
        self.summary_text.pack(pady=5)
        
        display_summary_button = ctk.CTkButton(
            self.summary_tab,
            text="Display Summary",
            command=lambda: self.update_summary_text(self.summary_account_entry.get(), "income")
        )
        display_summary_button.pack(pady=5)

    def init_visualization_tab(self):
        visualization_account_label = ctk.CTkLabel(self.visualization_tab, text="Account Name:")
        visualization_account_label.pack(pady=5)
        
        self.visualization_account_entry = ctk.CTkEntry(self.visualization_tab, width=300)
        self.visualization_account_entry.pack(pady=5)
        
        visualization_button = ctk.CTkButton(
            self.visualization_tab,
            text="Generate Bar Chart",
            command=lambda: self.create_bar_chart(self.visualization_account_entry.get())
        )
        visualization_button.pack(pady=5)

    def init_analysis_tab(self):
        analysis_account_label = ctk.CTkLabel(self.analysis_tab, text="Account Name:")
        analysis_account_label.pack(pady=5)
        
        self.analysis_account_entry = ctk.CTkEntry(self.analysis_tab, width=300)
        self.analysis_account_entry.pack(pady=5)
        
        self.analysis_text = ctk.CTkTextbox(self.analysis_tab, height=200, width=400)
        self.analysis_text.pack(pady=5)
        
        analysis_button = ctk.CTkButton(
            self.analysis_tab,
            text="Calculate Budget Analysis",
            command=lambda: self.budget_analysis(self.analysis_account_entry.get())
        )
        analysis_button.pack(pady=20)

    def add_transaction(self, account_name, category, amount, transaction_type):
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
            account_id = cursor.fetchone()
            if account_id is None:
                cursor.execute("INSERT INTO accounts (name) VALUES (?)", (account_name,))
                self.conn.commit()
                account_id = cursor.lastrowid
            else:
                account_id = account_id[0]
            cursor.execute(f"INSERT INTO {transaction_type} (account_id, category, amount, currency, date) VALUES (?, ?, ?, ?, ?)",
                           (account_id, category, float(amount), 'USD', timestamp))
            self.conn.commit()
            self.update_summary_text(account_name, transaction_type)
        except ValueError:
            print("Invalid amount")
        except Exception as e:
            print(f"Error adding transaction: {e}")

    def update_summary_text(self, account_name, transaction_type):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM accounts WHERE name = ?", (account_name,))
        account_id = cursor.fetchone()
        
        if account_id is not None:
            account_id = account_id[0]
            cursor.execute(f"SELECT category, amount FROM {transaction_type} WHERE account_id = ?", (account_id,))
            data = cursor.fetchall()
            
            self.summary_text.delete("0.0", tk.END)
            self.summary_text.insert("0.0", f"Summary for Account: {account_name}\n\n")
            self.summary_text.insert(tk.END, f"{transaction_type.capitalize()}:\n")
            for item in data:
                self.summary_text.insert(tk.END, f"{item[0]}: ${item[1]:.2f}\n")
        else:
            self.summary_text.delete("0.0", tk.END)
            self.summary_text.insert("0.0", f"No account found with name: {account_name}")

    def create_bar_chart(self, account_name):
        plt.clf()  # Avoid overlap
        cursor = self.conn.cursor()
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
            
            # Embed the matplotlib figure in the CustomTkinter window
            canvas = FigureCanvasTkAgg(plt.gcf(), master=self.visualization_tab)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)
        else:
            print("Account not found for bar chart.")

    def budget_analysis(self, account_name):
        self.analysis_text.delete("0.0", tk.END)
        self.analysis_text.insert("0.0", f"Budget analysis for {account_name} will be implemented.\n")

if __name__ == "__main__":
    app = BudgetTrackerApp()
    app.mainloop()