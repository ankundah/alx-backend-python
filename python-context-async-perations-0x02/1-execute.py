import sqlite3

class ExecuteQuery:
    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params or ()
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        """Open connection and execute query when entering context"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        return self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close cursor and connection when exiting context"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        return False

def initialize_database():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        
        # Create table with age column if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                age INTEGER
            )
        """)
        
        # Check if we need to add the age column (for existing databases)
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'age' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN age INTEGER")
        
        # Update existing users with ages
        cursor.execute("UPDATE users SET age = 30 WHERE name = 'John Doe'")
        cursor.execute("UPDATE users SET age = 28 WHERE name = 'Jane Smith'")
        
        # Add new users with ages
        cursor.execute("SELECT COUNT(*) FROM users WHERE name IN ('Mike Brown', 'Sarah Connor')")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users VALUES (3, 'Mike Brown', 'mike@example.com', 35)")
            cursor.execute("INSERT INTO users VALUES (4, 'Sarah Connor', 'sarah@example.com', 42)")
        
        conn.commit()

# Initialize/update the database
initialize_database()

# Execute our age-based query
query = "SELECT * FROM users WHERE age > ?"
params = (25,)

print("Users over 25 years old:")
with ExecuteQuery('users.db', query, params) as cursor:
    for row in cursor:
        print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Age: {row[3]}")

print("\nAll users:")
with ExecuteQuery('users.db', "SELECT * FROM users") as cursor:
    for row in cursor:
        print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Age: {row[3]}")