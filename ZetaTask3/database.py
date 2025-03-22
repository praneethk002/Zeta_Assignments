import sqlite3

def get_db():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('bank.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
    return conn