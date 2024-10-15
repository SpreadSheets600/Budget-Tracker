import sqlite3
import tkinter as tk
import customtkinter as ctk
from utils.Components import (
    create_labeled_entry,
    create_button,
    create_textbox,
    update_textbox,
)
from utils.Database import (
    create_or_open_database,
    get_account_id,
    create_user_account,
    validate_user,
)
from utils.Visualization import plot_bar_chart, plot_pie_chart, plot_line_chart
from utils.Export import export_to_csv


class BudgetTrackerApp:
    PAGES = [
        "User Authentication",
        "Income",
        "Expenses",
        "Visualization",
        "Summary",
        "Budget Analysis",
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("Budget Tracker")
        self.root.geometry("1000x600")

        self.root.iconbitmap("Icon.ico")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        try:
            self.db = create_or_open_database("budget_tracker.db")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return

        self.setup_ui()

    def setup_ui(self):
        # Create main layout
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)

        self.main_content = ctk.CTkFrame(self.root)
        self.main_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Create sidebar buttons
        self.sidebar_buttons = {}
        for page in self.PAGES:
            btn = ctk.CTkButton(
                self.sidebar, text=page, command=lambda p=page: self.show_page(p)
            )
            btn.pack(pady=10, padx=20)
            self.sidebar_buttons[page] = btn

        # Disable all buttons except User Authentication initially
        self.update_sidebar_buttons("User Authentication")

        # Create pages
        self.pages = {}
        for page in self.PAGES:
            self.pages[page] = ctk.CTkFrame(self.main_content)

        # Setup individual pages
        self.setup_authentication_page()
        self.setup_income_page()
        self.setup_expense_page()
        self.setup_visualization_page()
        self.setup_summary_page()
        self.setup_budget_analysis_page()

        # Show initial page
        self.show_page("User Authentication")

        # Create a label for notifications
        self.notification_label = ctk.CTkLabel(self.root, text="", text_color="white")
        self.notification_label.pack(side="bottom", pady=5)

    def show_page(self, page_name):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[page_name].pack(fill="both", expand=True)

    def update_sidebar_buttons(self, active_page):
        for page, button in self.sidebar_buttons.items():
            if page == active_page or (
                active_page != "User Authentication" and page != "User Authentication"
            ):
                button.configure(state="normal")
            else:
                button.configure(state="disabled")

    def setup_authentication_page(self):
        page = self.pages["User Authentication"]

        username_entry = create_labeled_entry(page, "Username")
        password_entry = create_labeled_entry(page, "Password", show="*")

        create_button(
            page,
            "Register",
            lambda: self.register(username_entry.get(), password_entry.get()),
        )

        create_button(
            page,
            "Login",
            lambda: self.login(username_entry.get(), password_entry.get()),
        )

    def setup_income_page(self):
        page = self.pages["Income"]

        income_account_entry = create_labeled_entry(page, "Account Name")
        income_category_entry = create_labeled_entry(page, "Category")
        income_amount_entry = create_labeled_entry(page, "Amount")
        income_date_entry = create_labeled_entry(page, "Date (YYYY-MM-DD)")

        create_button(
            page,
            "Add Income",
            lambda: self.add_income(
                income_account_entry.get(),
                income_category_entry.get(),
                income_amount_entry.get(),
                income_date_entry.get(),
            ),
        )

    def setup_expense_page(self):
        page = self.pages["Expenses"]

        expense_account_entry = create_labeled_entry(page, "Account Name")
        expense_category_entry = create_labeled_entry(page, "Category")
        expense_amount_entry = create_labeled_entry(page, "Amount")
        expense_date_entry = create_labeled_entry(page, "Date (YYYY-MM-DD)")

        create_button(
            page,
            "Add Expense",
            lambda: self.add_expense(
                expense_account_entry.get(),
                expense_category_entry.get(),
                expense_amount_entry.get(),
                expense_date_entry.get(),
            ),
        )

    def setup_visualization_page(self):
        page = self.pages["Visualization"]

        viz_account_entry = create_labeled_entry(page, "Account Name")

        create_button(
            page,
            "Show Bar Chart",
            lambda: self.show_bar_chart(viz_account_entry.get()),
        )

        create_button(
            page,
            "Show Pie Chart",
            lambda: self.show_pie_chart(viz_account_entry.get()),
        )

        create_button(
            page,
            "Show Line Chart",
            lambda: self.show_line_chart(viz_account_entry.get()),
        )

        self.chart_frame = ctk.CTkFrame(page)
        self.chart_frame.pack(fill=ctk.BOTH, expand=True, pady=10)

    def setup_summary_page(self):
        page = self.pages["Summary"]

        summary_account_entry = create_labeled_entry(page, "Account Name")
        self.summary_text = create_textbox(page)

        create_button(
            page,
            "Display Summary",
            lambda: self.update_summary(summary_account_entry.get(), self.summary_text),
        )

        create_button(
            page,
            "Export All Data",
            lambda: self.export_all_data(summary_account_entry.get()),
        )

    def setup_budget_analysis_page(self):
        page = self.pages["Budget Analysis"]

        analysis_account_entry = create_labeled_entry(page, "Account Name")
        self.analysis_text = create_textbox(page)

        create_button(
            page,
            "Calculate Budget Analysis",
            lambda: self.budget_analysis(
                analysis_account_entry.get(), self.analysis_text
            ),
        )

    def register(self, username: str, password: str) -> None:
        """Register a new user with the given username and password."""
        if not self.is_valid_input(username, password):
            return
        
        try:
            self.create_user_account(self.db, username, password)
            self.show_notification("Registration successful!", "success")
        except ValueError as ve:
            self.show_notification(str(ve), "error")
        except RuntimeError as re:
            self.show_notification(str(re), "error")
        except Exception as e:
            self.show_notification("An unexpected error occurred.", "error")

    def login(self, username, password):
        if not username or not password:
            self.show_notification("Username and password are required.", "error")
            return
        if validate_user(self.db, username, password):
            self.show_notification("Login successful!", "success")
            self.update_sidebar_buttons("Income")  # Enable all buttons after login
            self.show_page("Income")  # Show Income page after successful login
        else:
            self.show_notification("Invalid username or password.", "error")

    def add_income(self, account_name, category, amount, date):
        try:
            if not account_name or not category or not amount or not date:
                raise ValueError("All fields are required.")
            amount = float(amount)
            account_id = get_account_id(self.db, account_name)
            if account_id is None:
                raise ValueError("Account does not exist.")
            cursor = self.db.cursor()
            cursor.execute(
                "INSERT INTO transactions (account_id, type, category, amount, date) VALUES (?, 'income', ?, ?, ?)",
                (account_id, category, amount, date),
            )
            self.db.commit()
            self.show_notification("Income added successfully.", "success")
        except ValueError as ve:
            self.show_notification(str(ve), "error")
        except Exception as e:
            self.show_notification(f"An error occurred: {str(e)}", "error")

    def add_expense(self, account_name, category, amount, date):
        try:
            if not account_name or not category or not amount or not date:
                raise ValueError("All fields are required.")
            amount = float(amount)
            account_id = get_account_id(self.db, account_name)
            if account_id is None:
                raise ValueError("Account does not exist.")
            cursor = self.db.cursor()
            cursor.execute(
                "INSERT INTO transactions (account_id, type, category, amount, date) VALUES (?, 'expense', ?, ?, ?)",
                (account_id, category, amount, date),
            )
            self.db.commit()
            self.show_notification("Expense added successfully.", "success")
        except ValueError as ve:
            self.show_notification(str(ve), "error")
        except Exception as e:
            self.show_notification(f"An error occurred: {str(e)}", "error")

    def show_bar_chart(self, account_name):
        try:
            data, labels = self.get_income_data(account_name)
            plot_bar_chart(data, labels, "Income by Category", self.chart_frame)
        except Exception as e:
            self.show_notification(f"Error displaying chart: {str(e)}", "error")

    def show_pie_chart(self, account_name):
        try:
            data, labels = self.get_expense_data(account_name)
            plot_pie_chart(data, labels, "Expenses by Category", self.chart_frame)
        except Exception as e:
            self.show_notification(f"Error displaying chart: {str(e)}", "error")

    def show_line_chart(self, account_name):
        try:
            income_data = self.get_income_time_data(account_name)
            expense_data = self.get_expense_time_data(account_name)
            plot_line_chart(income_data, expense_data, self.chart_frame)
        except Exception as e:
            self.show_notification(f"Error displaying chart: {str(e)}", "error")

    def update_summary(self, account_name, summary_text):
        try:
            account_id = get_account_id(self.db, account_name)
            if account_id is None:
                raise ValueError("Account does not exist.")

            cursor = self.db.cursor()
            cursor.execute(
                "SELECT SUM(amount) FROM transactions WHERE account_id = ? AND type = 'income'",
                (account_id,),
            )
            total_income = cursor.fetchone()[0] or 0

            cursor.execute(
                "SELECT SUM(amount) FROM transactions WHERE account_id = ? AND type = 'expense'",
                (account_id,),
            )
            total_expenses = cursor.fetchone()[0] or 0

            update_textbox(
                summary_text,
                f"Total Income: ${total_income:.2f}\nTotal Expenses: ${total_expenses:.2f}",
            )
        except Exception as e:
            self.show_notification(f"Error updating summary: {str(e)}", "error")

    def budget_analysis(self, account_name, analysis_text):
        try:
            account_id = get_account_id(self.db, account_name)
            if account_id is None:
                raise ValueError("Account does not exist.")

            cursor = self.db.cursor()
            cursor.execute(
                "SELECT SUM(amount) FROM transactions WHERE account_id = ? AND type = 'income'",
                (account_id,),
            )
            total_income = cursor.fetchone()[0] or 0

            cursor.execute(
                "SELECT SUM(amount) FROM transactions WHERE account_id = ? AND type = 'expense'",
                (account_id,),
            )
            total_expenses = cursor.fetchone()[0] or 0

            if total_income > total_expenses:
                analysis_result = "You are within your budget."
            elif total_income == total_expenses:
                analysis_result = "You are breaking even."
            else:
                analysis_result = "You are over budget!"

            update_textbox(
                analysis_text,
                f"Total Income: ${total_income:.2f}\nTotal Expenses: ${total_expenses:.2f}\n{analysis_result}",
            )
        except Exception as e:
            self.show_notification(f"Error in budget analysis: {str(e)}", "error")

    def export_all_data(self, account_name):
        try:
            result = export_to_csv(account_name, self.db)
            if result:
                income_file, expenses_file, summary_file = result
                self.show_notification(
                    f"Data exported successfully:\n{income_file}\n{expenses_file}\n{summary_file}",
                    "success",
                )
            else:
                self.show_notification("Failed to export data.", "error")
        except Exception as e:
            self.show_notification(f"Error during export: {str(e)}", "error")

    def get_income_data(self, account_name):
        account_id = get_account_id(self.db, account_name)
        if account_id is None:
            raise ValueError("Account does not exist.")
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT category, SUM(amount) FROM transactions WHERE account_id = ? AND type = 'income' GROUP BY category",
            (account_id,),
        )
        results = cursor.fetchall()
        data = [row[1] for row in results]
        labels = [row[0] for row in results]
        return data, labels

    def get_expense_data(self, account_name):
        account_id = get_account_id(self.db, account_name)
        if account_id is None:
            raise ValueError("Account does not exist.")
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT category, SUM(amount) FROM transactions WHERE account_id = ? AND type = 'expense' GROUP BY category",
            (account_id,),
        )
        results = cursor.fetchall()
        data = [row[1] for row in results]
        labels = [row[0] for row in results]
        return data, labels

    def get_income_time_data(self, account_name):
        account_id = get_account_id(self.db, account_name)
        if account_id is None:
            raise ValueError("Account does not exist.")
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT date, SUM(amount) FROM transactions WHERE account_id = ? AND type = 'income' GROUP BY date",
            (account_id,),
        )
        results = cursor.fetchall()
        data = [row[1] for row in results]
        labels = [row[0] for row in results]
        return data, labels

    def get_expense_time_data(self, account_name):
        account_id = get_account_id(self.db, account_name)
        if account_id is None:
            raise ValueError("Account does not exist.")
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT date, SUM(amount) FROM transactions WHERE account_id = ? AND type = 'expense' GROUP BY date",
            (account_id,),
        )
        results = cursor.fetchall()
        data = [row[1] for row in results]
        labels = [row[0] for row in results]
        return data, labels

    def show_notification(self, message: str, message_type: str) -> None:
        """Display a notification with the specified message and type."""
        color = {
            "error": "red",
            "success": "green"
        }.get(message_type, "white")

        self.notification_label.configure(text=message, text_color=color)
        self.notification_label.after(5000, lambda: self.notification_label.configure(text=""))


    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = ctk.CTk()
    app = BudgetTrackerApp(root)
    app.run()
