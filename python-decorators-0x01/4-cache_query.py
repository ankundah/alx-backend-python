import time
import sqlite3
import functools
from functools import wraps

query_cache = {}

def cache_query(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from kwargs or args
        query = kwargs.get('query', None)
        if query is None and len(args) > 1:  # First arg is usually 'conn'
            query = args[1] if isinstance(args[1], str) else None
        
        if query is None:
            return func(*args, **kwargs)  # No query to cache
        
        # Check if query is in cache
        if query in query_cache:
            print("Returning cached result")
            return query_cache[query]
        
        # Execute and cache the result
        result = func(*args, **kwargs)
        query_cache[query] = result
        print("Caching new result")
        return result
    return wrapper

def with_db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            if 'conn' not in kwargs and (len(args) == 0 or not isinstance(args[0], sqlite3.Connection)):
                kwargs['conn'] = conn
            return func(*args, **kwargs)
        finally:
            conn.close()
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# Initialize database (if needed)
# def initialize_database():
#     conn = sqlite3.connect('users.db')
#     try:
#         cursor = conn.cursor()
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS users (
#                 id INTEGER PRIMARY KEY,
#                 name TEXT,
#                 email TEXT
#             )
#         """)
#         cursor.execute("SELECT COUNT(*) FROM users")
#         if cursor.fetchone()[0] == 0:
#             cursor.execute("INSERT INTO users (id, name, email) VALUES (1, 'John Doe', 'john@example.com')")
#             cursor.execute("INSERT INTO users (id, name, email) VALUES (2, 'Jane Smith', 'jane@example.com')")
#         conn.commit()
#     finally:
#         conn.close()

# initialize_database()

# First call will cache the result
print("First call:")
users = fetch_users_with_cache(query="SELECT * FROM users")
print(users)

# Second call will use the cached result
print("\nSecond call:")
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(users_again)