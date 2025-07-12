import sqlite3

class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
    
    def __enter__(self):
        """Open the database connection when entering the context"""
        self.conn = sqlite3.connect(self.db_name)
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the database connection when exiting the context"""
        if self.conn:
            self.conn.close()
        # Return False to propagate any exceptions, True would suppress them
        return False

# Initialize the database (create table and sample data if needed)
def initialize_database():
    with DatabaseConnection('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        """)
        # Insert sample data if table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users VALUES (3, 'Jacob Elordi', 'jac@example.com')")
            cursor.execute("INSERT INTO users VALUES (4, 'Jessica Bell', 'jess@example.com')")
        conn.commit()

# Initialize the database first
initialize_database()

# Use the context manager to perform a query
with DatabaseConnection('users.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    print("Users in the database:")
    for row in results:
        print(row)