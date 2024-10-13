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
