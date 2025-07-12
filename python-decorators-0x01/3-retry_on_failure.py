import time
import sqlite3
import functools
from random import random  # For simulating transient errors

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            if 'conn' not in kwargs and (len(args) == 0 or not isinstance(args[0], sqlite3.Connection)):
                kwargs['conn'] = conn
            return func(*args, **kwargs)
        finally:
            conn.close()
    return wrapper

def retry_on_failure(retries=3, delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
                    last_exception = e
                    if attempt < retries:
                        print(f"Attempt {attempt} failed. Retrying in {delay} seconds...")
                        time.sleep(delay)
            print(f"All {retries} attempts failed")
            raise last_exception
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    # Simulate a transient error (remove in production)
    if random() < 0.5:  # 50% chance of failure for demonstration
        raise sqlite3.OperationalError("Simulated transient database error")
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Initialize database (if needed)
def initialize_database():
    conn = sqlite3.connect('users.db')
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        """)
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (id, name, email) VALUES (1, 'John Doe', 'john@example.com')")
            cursor.execute("INSERT INTO users (id, name, email) VALUES (2, 'Jane Smith', 'jane@example.com')")
        conn.commit()
    finally:
        conn.close()

initialize_database()

# Attempt to fetch users with automatic retry on failure
try:
    users = fetch_users_with_retry()
    print("Successfully fetched users:")
    for user in users:
        print(user)
except Exception as e:
    print(f"Failed to fetch users after retries: {e}")