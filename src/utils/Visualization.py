from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.ERROR)


def plot_bar_chart(data: list, labels: list, title: str, parent) -> None:
    """Plots a bar chart using provided data and labels."""
    try:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(labels, data)
        
        # Setting the chart title with custom styling
        ax.set_title(title, fontsize=16, color='white', pad=20, loc='center')
        
        # Setting labels and title for the axes
        ax.set_xlabel("Category", fontsize=12, color='lightgray')
        ax.set_ylabel("Amount (USD)", fontsize=12, color='lightgray')
        
        # Styling x-axis labels
        plt.xticks(rotation=45, ha="right", fontsize=10, color='lightgray')
        plt.yticks(fontsize=10, color='lightgray')
        
        # Customizeing chart background and grid
        ax.set_facecolor("#000000")  
        fig.patch.set_facecolor("#1E90FF")  
        
        plt.tight_layout()

        display_chart(fig, parent)

    except Exception as e:
        logging.error(f"Error plotting bar chart: {e}")


def plot_pie_chart(data: list, labels: list, title: str, parent) -> None:
    """Plots a pie chart."""
    try:
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Pie chart with custom colors and percentages
        ax.pie(data, labels=labels, autopct="%1.1f%%", startangle=90, textprops={'color': 'white'})
        
        # Set title with custom styling
        ax.set_title(title, fontsize=16, color='white', pad=20, loc='center')

        # Set background colors
        ax.set_facecolor("#000000")  
        fig.patch.set_facecolor("#1E90FF")  

        plt.tight_layout()

        display_chart(fig, parent)
    except Exception as e:
        logging.error(f"Error plotting pie chart: {e}")


def plot_line_chart(income_data: list, expense_data: list, parent) -> None:
    """Plots a line chart for income and expenses over time."""
    try:
        fig, ax = plt.subplots(figsize=(12, 6))

        if income_data:
            income_dates, income_amounts = zip(*income_data)
            income_dates = [
                datetime.strptime(date, "%Y-%m-%d").date() for date in income_dates
            ]
            ax.plot(income_dates, income_amounts, label="Income", marker="o", color='#66b3ff')

        if expense_data:
            expense_dates, expense_amounts = zip(*expense_data)
            expense_dates = [
                datetime.strptime(date, "%Y-%m-%d").date() for date in expense_dates
            ]
            ax.plot(expense_dates, expense_amounts, label="Expenses", marker="o", color='#ff9999')

        
        ax.set_title("Income and Expenses Over Time", fontsize=16, color='white', pad=20, loc='center')
        
        # Set labels and grid
        ax.set_xlabel("Date", fontsize=12, color='lightgray')
        ax.set_ylabel("Amount (USD)", fontsize=12, color='lightgray')
        ax.legend()

        
        plt.xticks(color='lightgray')
        plt.yticks(color='lightgray')
        ax.set_facecolor("#000000")  
        fig.patch.set_facecolor("#1E90FF")  

        plt.gcf().autofmt_xdate()  
        plt.tight_layout()

        display_chart(fig, parent)
    except Exception as e:
        logging.error(f"Error plotting line chart: {e}")

def plot_stacked_bar_chart(income_data: list, expense_data: list, parent) -> None:
    """Plots a stacked bar chart comparing income and expenses by category."""
    try:
        fig, ax = plt.subplots(figsize=(12, 6))

        income_categories, income_amounts = zip(*income_data)
        expense_categories, expense_amounts = zip(*expense_data)

        x = np.arange(len(income_categories))
        width = 0.35

        ax.bar(x - width / 2, income_amounts, width, label="Income", color="#66b3ff")
        ax.bar(x + width / 2, expense_amounts, width, label="Expenses", color="#ff9999")

        ax.set_title("Income vs Expenses by Category", fontsize=16, color='white', pad=20, loc='center')
        
    
        ax.set_xlabel("Category", fontsize=12, color='lightgray')
        ax.set_ylabel("Amount (USD)", fontsize=12, color='lightgray')
        ax.set_xticks(x)
        ax.set_xticklabels(income_categories, rotation=45, ha="right", fontsize=10, color='lightgray')

        
        ax.legend()
        ax.set_facecolor("#000000")  
        fig.patch.set_facecolor("#1E90FF")  

        plt.tight_layout()
        display_chart(fig, parent)
    except Exception as e:
        logging.error(f"Error plotting stacked bar chart: {e}")



def display_chart(fig, parent) -> None:
    """Clears previous chart and displays a new chart."""
    for widget in parent.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10, expand=True, fill="both")


def create_summary_chart(
    income_total: float, expense_total: float, savings_total: float, parent
) -> None:
    """Creates a summary chart showing total income, expenses, and savings."""
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        categories = ["Income", "Expenses", "Savings"]
        amounts = [income_total, expense_total, savings_total]
        colors = ["#66b3ff", "#ff9999", "#99ff99"]

        ax.bar(categories, amounts, color=colors)
        ax.set_title("Financial Summary")
        ax.set_ylabel("Amount (USD)")

        for i, v in enumerate(amounts):
            ax.text(i, v, f"${v:,.2f}", ha="center", va="bottom")

        plt.tight_layout()
        display_chart(fig, parent)
    except Exception as e:
        logging.error(f"Error creating summary chart: {e}")
