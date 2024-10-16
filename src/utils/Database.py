import sqlite3
import bcrypt


def create_tables(conn) -> None:
    """Create necessary tables."""
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER,
            type TEXT,
            category TEXT,
            amount REAL,
            currency TEXT,
            date TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
        """
    )
    conn.commit()


def create_user_account(self, conn: sqlite3.Connection, username: str, password: str) -> None:
        """Create a new user account."""
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO accounts (username, password) VALUES (?, ?)",
                    (username, hashed_password),
                )
            print("User account created successfully.")
        except sqlite3.IntegrityError:
            raise ValueError("Username already exists. Please choose a different username.")
        except sqlite3.Error as e:
            raise RuntimeError(f"Database error: {e}")



def validate_user(conn: sqlite3.Connection, username: str, password: str) -> bool:
    """Validate user credentials against the stored hashed password."""
    if conn is None:
        raise ValueError("Database connection is not valid.")

    try:
        # Create a cursor without a context manager
        cursor = conn.cursor()
        
        # Execute the query to fetch the hashed password for the given username
        cursor.execute("SELECT password FROM accounts WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        # Close the cursor explicitly
        cursor.close()
        
        # Check if user exists and if the password matches the hashed password
        if result and bcrypt.checkpw(password.encode("utf-8"), result[0]):
            return True
        else:
            return False

    except sqlite3.Error as e:
        # Handle database errors (logging can be added here)
        print(f"Database error occurred: {e}")

    return False



def get_account_id(conn, username: str) -> int:
    """Get account ID by username."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        return result[0]
    raise ValueError("Account not found.")


def fetch_data(conn, account_id: int) -> list:
    """Fetch transactions for a given account ID."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE account_id = ?", (account_id,))
    return cursor.fetchall()


def fetch_total(conn, account_id: int) -> float:
    """Fetch total balance for a given account ID."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUM(amount) FROM transactions WHERE account_id = ?", (account_id,)
    )
    result = cursor.fetchone()
    if result:
        return result[0]
    return 0.0


def create_or_open_database(db_name: str):
    """Create or open a database."""
    conn = sqlite3.connect(db_name)
    create_tables(conn)
    return conn
