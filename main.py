import sqlite3
import requests
import customtkinter as ctk
from datetime import datetime

from src.utils.Components import (
    create_labeled_entry,
    create_button,
    create_textbox,
    update_textbox,
    create_dropdown,
)
from src.utils.Database import (
    create_or_open_database,
    get_account_id,
    create_user_account,
    validate_user,
)
from src.utils.Export import export_to_csv
from src.utils.Visualization import plot_bar_chart, plot_pie_chart, plot_line_chart


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

        # Δημιουργία πεδίων εισαγωγής για το όνομα χρήστη και τον κωδικό πρόσβασης
        username_entry = create_labeled_entry(page, "Username")
        password_entry = create_labeled_entry(page, "Password", show="*")

        # Κουμπί για σύνδεση
        create_button(
            page,
            "Login",
            lambda: self.login(username_entry.get(), password_entry.get()),
        )


        # Κουμπί για εγγραφή που ανοίγει νέο παράθυρο
        create_button(
            page,
            "Register",
            lambda: self.open_register_window(),  # Κλήση νέας μεθόδου για το παράθυρο εγγραφής
        )


    def open_register_window(self):
        # Κλείσιμο του κύριου παραθύρου (ή οποιουδήποτε άλλου παραθύρου είναι ανοιχτό)

        self.root.withdraw()
        # Δημιουργία νέου παραθύρου για το Register
        self.register_window = ctk.CTkToplevel()  # Δημιουργία του παραθύρου ως ιδιότητα της κλάσης
        self.register_window.title("Register")
        self.register_window.geometry("300x200")  # Ρύθμιση μεγέθους παραθύρου

        # Δημιουργία πεδίων για το όνομα χρήστη και τον κωδικό πρόσβασης
        username_entry = create_labeled_entry(self.register_window, "Username")
        password_entry = create_labeled_entry(self.register_window, "Password", show="*")

        # Κουμπί εγγραφής στο νέο παράθυρο
        create_button(
            self.register_window,
            "Submit Registration",
            lambda: self.register(username_entry.get(), password_entry.get())
        )

        # Ορισμός ενέργειας για την καταστροφή του παραθύρου όταν κλείνει
        self.register_window.protocol("WM_DELETE_WINDOW", lambda: self.close_register_window())

    def close_register_window(self):
        # Κλείσιμο του παραθύρου εγγραφής και απομάκρυνση της αναφοράς
        if hasattr(self, 'register_window'):
            self.register_window.destroy()
            del self.register_window

    def setup_income_page(self):
        page = self.pages["Income"]

        income_account_entry = create_labeled_entry(page, "Account Name")
        income_category_entry = create_labeled_entry(page, "Category")
        income_amount_entry = create_labeled_entry(page, "Amount")
        #income_date_entry = create_labeled_entry(page, "Date (YYYY-MM-DD)")
        current_date = datetime.now().strftime("%d/%m/%Y")

        create_button(
            page,
            "Add Income",
            lambda: self.add_income(
                income_account_entry.get(),
                income_category_entry.get(),
                income_amount_entry.get(),
                current_date,
            ),
        )

    def setup_expense_page(self):
        page = self.pages["Expenses"]

        expense_account_entry = create_labeled_entry(page, "Account Name")
        expense_category_entry = create_labeled_entry(page, "Category")
        expense_amount_entry = create_labeled_entry(page, "Amount")
        #expense_date_entry = create_labeled_entry(page, "Date (YYYY-MM-DD)")
        current_date = datetime.now().strftime("%d/%m/%Y")

        create_button(
            page,
            "Add Expense",
            lambda: self.add_expense(
                expense_account_entry.get(),
                expense_category_entry.get(),
                expense_amount_entry.get(),
                current_date,
            ),
        )

    def setup_visualization_page(self):
        page = self.pages["Visualization"]
        
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(3, weight=2) 
      
        header_frame = ctk.CTkFrame(page, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 5))
        
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Financial Visualization",
            font=ctk.CTkFont(family="Arial", size=-24, weight="bold"), 
            text_color="white"
        )
        title_label.pack(anchor="w")
       
        self.cards_frame = ctk.CTkFrame(page, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)
      
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")
        self.cards_frame.grid_rowconfigure(0, minsize=100)
        
        self.active_chart_var = ctk.StringVar(value="bar")
        charts = [
            ("Bar Chart", "Income Distribution", self.show_bar_chart),
            ("Pie Chart", "Expense Distribution", self.show_pie_chart),
            ("Line Chart", "Income vs Expenses", self.show_line_chart)
        ]
        
        for i, (title, desc, command) in enumerate(charts):
            card = self.create_responsive_chart_card(
                self.cards_frame,
                title,
                desc,
                command,
                chart_type=title.split()[0].lower()
            )
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
   
        input_frame = ctk.CTkFrame(page, fg_color="#1a1a1a")
        input_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=5)
        
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=0) 
        input_frame.grid_rowconfigure(0, minsize=70)
        
        self.viz_account_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter Account Name",
            height=35,
            font=ctk.CTkFont(family="Arial", size=-12)
        )
        self.viz_account_entry.grid(row=0, column=0, padx=(20, 10), pady=17, sticky="ew")
        
        update_btn = ctk.CTkButton(
            input_frame,
            text="Update Chart",
            command=self.update_chart_with_debounce,
            height=35,
            width=120,
            font=ctk.CTkFont(family="Arial", size=-12, weight="bold")
        )
        update_btn.grid(row=0, column=1, padx=(0, 20), pady=17)
       
        self.chart_frame = ctk.CTkFrame(
            page,
            fg_color="#000000",
            corner_radius=15
        )
        self.chart_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(5, 10))
        
        self.chart_frame.grid_columnconfigure(0, weight=2)
        self.chart_frame.grid_rowconfigure(0, weight=2)
        
        def on_resize(event):
            if hasattr(self, 'current_chart'):
                self.update_chart_with_debounce()
        
        self.chart_frame.bind('<Configure>', on_resize)

    def create_responsive_chart_card(self, parent, title, description, command, chart_type):
        card = ctk.CTkFrame(
            parent,
            fg_color="#1a1a1a",
            corner_radius=10,
            border_width=2,
            border_color="#2a2a2a"
        )
        
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure((0, 1), weight=1)
        
        card.name = chart_type
        
        def on_click(event=None):
            if self.active_chart_var.get() != chart_type:
                self.active_chart_var.set(chart_type)
                self.update_card_styles()
                self.update_chart_with_debounce()
        
        card.bind("<Button-1>", on_click)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family="Arial", size=-16, weight="bold"),
            text_color="white"
        )
        title_label.bind("<Button-1>", on_click)
        title_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(family="Arial", size=-11),
            text_color="gray"
        )
        desc_label.bind("<Button-1>", on_click)
        desc_label.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")
        
        return card

    def update_card_styles(self):
        active_type = self.active_chart_var.get()
        for child in self.cards_frame.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                is_active = child.name == active_type
                child.configure(
                    border_color="#1E90FF" if is_active else "#2a2a2a",
                    fg_color="#162032" if is_active else "#1a1a1a"
                )

    def update_chart_with_debounce(self, *args):
        if hasattr(self, '_update_timer'):
            self.root.after_cancel(self._update_timer)
        
        self._update_timer = self.root.after(300, lambda: self.update_active_chart(self.viz_account_entry.get()))

    def update_active_chart(self, account_name):
        if not account_name:
            self.show_notification("Please enter an account name", "error")
            return
            
        try:
            chart_type = self.active_chart_var.get()
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            loading_label = ctk.CTkLabel(
                self.chart_frame,
                text="Loading...",
                font=("Arial", 14),
                text_color="white"
            )
            loading_label.pack(expand=True)
            self.chart_frame.update()
            if chart_type == "bar":
                self.show_bar_chart(account_name)
            elif chart_type == "pie":
                self.show_pie_chart(account_name)
            elif chart_type == "line":
                self.show_line_chart(account_name)
                
        except Exception as e:
            self.show_notification(f"Error updating chart: {str(e)}", "error")
        finally:
            if 'loading_label' in locals():
                loading_label.destroy()

    # Summary Page 
    def setup_summary_page(self):
        page = self.pages["Summary"]

        summary_account_entry = create_labeled_entry(page, "Account Name")
        self.summary_text = create_textbox(page)

        # The create_dropdown function to add a currency selection dropdown
        currency_options = ["USD", "EUR", "GBP", "INR"]
        self.currency_var = create_dropdown(page, currency_options, default="USD")
    
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
        
    # Currency Conversion
    def convert_currency(self, amount, from_currency, to_currency):
        try:
            # API endpoint for getting the latest rates for the from_currency
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            response = requests.get(url)
            response.raise_for_status()

            # Get the conversion rate for the desired currency
            rates = response.json().get('rates', {})
            conversion_rate = rates.get(to_currency, 1)

            # Calculate the converted amount
            converted_amount = round(amount * conversion_rate, 2)
            return converted_amount
        except requests.exceptions.RequestException as e:
            self.show_notification(f"Currency conversion failed: {str(e)}", "error")
            return amount

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

    def is_valid_input(self, username: str, password: str) -> bool:
        """
        Validates the input for the username and password.
        Ensures that neither is empty and that they meet other criteria (if any).
        """
        if not username or not password:
            self.show_notification("Username and password are required.", "error")
        return True

    def register(self, username: str, password: str) -> None:
        """Register a new user with the given username and password."""
        if not self.is_valid_input(username, password):
            return
        
        try:
            create_user_account(self, self.db, username, password)
            self.show_notification("Registration successful!", "success")
            self.register_window.destroy()
            self.root.deiconify()
        except ValueError as ve:
            self.show_notification(str(ve), "error")
        except RuntimeError as re:
            self.show_notification(str(re), "error")
        except Exception as e:
            self.show_notification(str(e), "error")

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

    # Updated Summary
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
            
            selected_currency = self.currency_var.get()
        
            converted_income = self.convert_currency(total_income, "USD", selected_currency)
            converted_expenses = self.convert_currency(total_expenses, "USD", selected_currency)

            update_textbox(
                summary_text,
                f"Total Income: {converted_income:.2f} {selected_currency}\n"
                f"Total Expenses: {converted_expenses:.2f} {selected_currency}"
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
        """Get income data for line chart"""
        try:
            account_id = get_account_id(self.db, account_name)
            if account_id is None:
                raise ValueError("Account does not exist.")
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT date, SUM(amount) FROM transactions "
                "WHERE account_id = ? AND type = 'income' "
                "GROUP BY date ORDER BY date",
                (account_id,)
            )
            results = cursor.fetchall()
            if not results:
                return [], []
            
            # Separate dates and amounts, keeping the date format as is
            dates = [row[0] for row in results]
            amounts = [row[1] for row in results]
            return dates, amounts
        except Exception as e:
            print(f"Error getting income data: {e}")
            return [], []

    def get_expense_time_data(self, account_name):
        """Get expense data for line chart"""
        try:
            account_id = get_account_id(self.db, account_name)
            if account_id is None:
                raise ValueError("Account does not exist.")
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT date, SUM(amount) FROM transactions "
                "WHERE account_id = ? AND type = 'expense' "
                "GROUP BY date ORDER BY date",
                (account_id,)
            )
            results = cursor.fetchall()
            if not results:
                return [], []
            
            # Separate dates and amounts, keeping the date format as is
            dates = [row[0] for row in results]
            amounts = [row[1] for row in results]
            return dates, amounts
        except Exception as e:
            print(f"Error getting expense data: {e}")
            return [], []

    def show_notification(self, message: str, message_type: str) -> None:
        """Display a pop-up notification in the bottom-right corner."""
        # Create a Toplevel window (pop-up)
        popup = ctk.CTkToplevel(self.root)
        popup.overrideredirect(True)  # Remove window decorations (close, minimize, etc.)
        popup.configure(fg_color="#000000")  # Set background color to black

        # Create a label in the pop-up with dynamic text
        self.notification_label = ctk.CTkLabel(
            popup,
            text=message,
            text_color="white",
            fg_color="#1E90FF",  # Blue background color
            bg_color="#000000",   # Black background color
            font=("Arial", 12, "bold"),  # Font style, smaller for less height
            corner_radius=8,      # Rounded corners
            padx=10,
            pady=5  # Decreased padding to reduce overall height
        )
        color = {
            "error": "red",
            "success": "green"
        }.get(message_type, "white")
        self.notification_label.pack(expand=True, fill="both", padx=10, pady=10)
        self.notification_label.configure(text=message, text_color=color)

        size, root_x, root_y = self.root.geometry().split('+')
        root_x = int(root_x)
        root_y = int(root_y)

        root_w, root_h = size.split('x')
        root_w = int(root_w)
        root_h = int(root_h)

        # Update the popup size based on the label text
        popup.update_idletasks()  # Update "requested size" from geometry manager
        popup_width = self.notification_label.winfo_width() + 20  # Adding padding
        popup_height = self.notification_label.winfo_height() + 20  # Adding padding
        popup.minsize(250, 50)  # Set minimum size for the pop-up

        popup_y = root_y + (root_h - popup_height - popup_height // 2) # Almost bottom
        popup_x = root_x + (root_w - (popup_width + 20 if popup_width >= 250 else 270)) # FIXME: why isn't popup_width the exact width?

        popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")

        # Automatically destroy the pop-up after a certain duration
        popup.after(3000, popup.destroy)  # Automatically close after 3 seconds

        # Bind the resize event of the main window to update the position
        def update_popup_position(event):
            popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")

        # Update position when the main window is resized
        self.root.bind("<Configure>", update_popup_position)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = ctk.CTk()
    app = BudgetTrackerApp(root)
    app.run()