import asyncio
import aiosqlite

# Database initialization (now async)
async def initialize_database():
    async with aiosqlite.connect('users.db') as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                age INTEGER
            )
        """)
        
        # Check if we need to add sample data
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        count = (await cursor.fetchone())[0]
        if count == 0:
            await db.executemany(
                "INSERT INTO users VALUES (?, ?, ?, ?)",
                [
                    (1, 'John Doe', 'john@example.com', 30),
                    (2, 'Jane Smith', 'jane@example.com', 28),
                    (3, 'Mike Brown', 'mike@example.com', 35),
                    (4, 'Sarah Connor', 'sarah@example.com', 42),
                    (5, 'Robert Johnson', 'robert@example.com', 21)
                ]
            )
        await db.commit()

async def async_fetch_users():
    """Fetch all users from the database"""
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users")
        return await cursor.fetchall()

async def async_fetch_older_users():
    """Fetch users older than 40"""
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > ?", (40,))
        return await cursor.fetchall()

async def fetch_concurrently():
    """Run both queries concurrently"""
    # Initialize database first
    await initialize_database()
    
    # Run both queries concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    print("\nAll users:")
    for user in all_users:
        print(f"ID: {user[0]}, Name: {user[1]}, Age: {user[3]}")
    
    print("\nUsers over 40:")
    for user in older_users:
        print(f"ID: {user[0]}, Name: {user[1]}, Age: {user[3]}")

# Run the main async function
if __name__ == "__main__":
    asyncio.run(fetch_concurrently())