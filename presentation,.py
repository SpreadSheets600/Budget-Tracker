import customtkinter as ctk
import tkinter as tk
from ttkbootstrap import Style


class BudgetTracker(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Budget Tracker")
        self.geometry("900x600")

        # tabs creation
        self.tabs = TabsCreate(self)
        tabs_name = [
            "Income",
            "Expenses",
            "Goals",
            "Visualization",
            "Summary",
            "Budget Analysis",
        ]
        for tab_name in tabs_name:
            self.tabs.add(tab_name)
            # tabs.tab(tab_name)

        for tab_name in tabs_name[:3]:
            forms = InputForm(self.tabs.tab(tab_name))


class TabsCreate(ctk.CTkTabview):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=ctk.BOTH, expand=True, pady=10, padx=10)


class InputForm(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        labels = ["Account Name:", "Category:", "Amount:", "Date (YYYY-MM-DD):"]
        for label_text in labels:
            label = ctk.CTkLabel(self, text=label_text)
            label.pack(pady=5)

            entry = ctk.CTkEntry(self)
            entry.pack(pady=5)
        self.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)


def main():
    style = Style(theme="darkly")
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    app = BudgetTracker()
    app.mainloop()


if __name__ == "__main__":
    main()
