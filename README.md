
# Budget Tracker

### Overview
Originally a half-yearly CS group project where (almost) no one contributed, this Budget Tracker has transformed into an ambitious project that I now aim to complete with friends (again, this time for real!). The goal is to create a functional, user-friendly budget tracker that helps people manage their income, expenses, and financial goals efficiently.

This project is a part of Hacktoberfest, and we're welcoming contributions! Whether it's bug fixes, new features, or improvements, there's room for everyone to help!

---

## Features
- **Add Income & Expenses**: Users can easily log their income and expenses, categorize them, and store them in an SQLite database.
- **Financial Goals**: Set savings goals, track progress, and visualize how close you are to achieving them.
- **Visualizations**: Bar charts, pie charts, and line graphs provide a clear picture of your financial habits.
- **Summary & Analysis**: View detailed summaries and analysis of your spending habits and overall budget health.

---

## Getting Started

### Prerequisites
- Python 3.x
- Tkinter
- SQLite3
- Matplotlib

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-github-username/budget-tracker.git
   ```
2. Create virtual environment
   ```bash
   python -m venv env
         or
   peotry init
   ```
3. Activate virtual environment
   ```bash
   source env/bin/activate
         or
   poetry shell
   ```

4. Install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
         or
   poetry install
   ```
5. Run the application:
   ```bash
   python src/Main.py
   ```

---

## Contributing
We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) for more details.

---
## To-Do List
### Core Functionalities
1. [ ] **Fix the Visuals**: Improve the UI/UX, adjust layout, and ensure the design is clean and user-friendly.
2. [ ] **Fix Visualization Tab**: Ensure that charts (bar, line, pie) display properly without overlapping or layout issues.
3. [ ] **Work on Lendings Tab**: Add a feature where users can track money lent to others, with options to set deadlines and reminders.
4. [ ] **Work on Borrowing Tab**: Implement a tab to track loans or borrowed amounts, including deadlines and reminders.
5. [ ] **Make Data Permanent**: Enhance the database functionality to ensure persistent data storage, so users can retrieve past transactions after restarting the app.
6. [x] **Replace Tkinter with CustomTkinter**: Enhance the look and feel of the app by integrating `CustomTkinter` for modern, polished widgets.

### Enhancements
7. [ ] **User Authentication**: Add basic login functionality to allow different users to manage their accounts separately.
8. [ ] **Currency Conversion**: Implement a feature to convert between currencies, pulling exchange rates from an API.
9. [ ] **Recurring Transactions**: Enable users to set recurring transactions (monthly bills, salary, etc.) that auto-log at set intervals.
10. [ ] **Export Data**: Allow users to export their data (income, expenses, goals) to CSV or Excel format for easier analysis.
11. [ ] **Add Notifications**: Implement a system to notify users when they exceed budget limits or reach savings goals.
12. [ ] **Mobile App Version**: Plan and develop a mobile version (possibly using Kivy or other frameworks).

---

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

