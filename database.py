import sqlite3
from typing import TextIO


class DatabaseManager:
    def __init__(self, filename: TextIO) -> None:
        self.connection = sqlite3.connect(filename)

    def __del__(self) -> None:
        self.connection.close()

    def _execute(self, statement: str, value=None):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(statement, value or [])
            return cursor

    def create_table(self, table_name) -> None:
        self._execute(
            f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            account_name TEXT,
            category TEXT,
            amount REAL,
            date TEXT
        )
    """
        )

    def insert_data(self, table_name, data) -> None:

        self._execute(
            f"""
                INSERT INTO {table_name} (account_name, category,amount, date) VALUES (?, ?, ?,?)
            """,
            tuple(data.values()),
        )
