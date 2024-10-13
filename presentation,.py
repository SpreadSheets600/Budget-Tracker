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

        tabs_dict_items = {
            "Income": InputForm,
            "Expenses": InputForm,
            "Goals": InputForm,
            "Visualization": VisualizationInputForm,
            "Summary": SummaryInputForm,
            "Budget Analysis": AnalysisInputForm,
        }

        # for tab_name in tabs_name:
        #     self.tabs.add(tab_name)
        #     # tabs.tab(tab_name)

        # for i, tab_name in enumerate(tabs_name[:3]):
        #     InputForm(self.tabs.tab(tab_name))

        for tab_name, form_class in tabs_dict_items.items():
            self.tabs.add(tab_name)
            form_class(self.tabs.tab(tab_name), tab_name)


class TabsCreate(ctk.CTkTabview):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=ctk.BOTH, expand=True, pady=10, padx=10)


class InputForm(ctk.CTkFrame):
    def __init__(self, parent, button_label=None) -> None:
        super().__init__(parent)

        labels = ["Account Name:", "Category:", "Amount:", "Date (YYYY-MM-DD):"]
        for label_text in labels:
            label = ctk.CTkLabel(self, text=label_text)
            label.pack(pady=5)

            entry = ctk.CTkEntry(self)
            entry.pack(pady=5)

        button = ctk.CTkButton(self, text=f"Add {button_label}")
        button.pack(pady=5)
        self.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)


class VisualizationInputForm(ctk.CTkFrame):
    def __init__(self, parent, button_label=None) -> None:
        super().__init__(parent)
        self.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)

        label = ctk.CTkLabel(self, text="Account Name")
        label.pack(pady=5)

        entry = ctk.CTkEntry(self)
        entry.pack(pady=5)

        button_texts = ["Bar", "Pie", "Line"]
        for txt in button_texts:
            button = ctk.CTkButton(self, text=f"Show {txt} Chart")
            button.pack(pady=5)


class SummaryInputForm(ctk.CTkFrame):
    def __init__(self, parent, button_label=None):
        super().__init__(parent)

        label = ctk.CTkLabel(self, text="Account Name")
        label.pack(pady=5)
        entry = ctk.CTkEntry(self)
        entry.pack(pady=5)

        textbox = ctk.CTkTextbox(self, height=400, width=500)
        textbox.pack(pady=10)

        button = ctk.CTkButton(self, text="Display Summary")
        button.pack(pady=10)
        self.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)


class AnalysisInputForm(ctk.CTkFrame):
    def __init__(self, parent, button_label=None):
        super().__init__(parent)

        label = ctk.CTkLabel(self, text="Account Name")
        label.pack(pady=5)
        entry = ctk.CTkEntry(self)
        entry.pack(pady=5)
        textbox = ctk.CTkTextbox(self, height=400, width=500)
        textbox.pack(pady=10)

        button = ctk.CTkButton(self, text="Calculate Budget Analysis")
        button.pack(pady=10)
        self.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)


def main():
    style = Style(theme="darkly")
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    app = BudgetTracker()
    app.mainloop()


if __name__ == "__main__":
    main()
