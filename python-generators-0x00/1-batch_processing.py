import mysql.connector

def stream_users_in_batches(batch_size):
    """
    Generator that yields users from the user_data table in batches.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="your_username",        # Replace with your MySQL username
            password="your_password",    # Replace with your MySQL password
            database="ALX_prodev"
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")

        batch = []
        for row in cursor:  # Loop 1
            batch.append(row)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    except mysql.connector.Error as err:
        print(f"[❌] Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def batch_processing(batch_size):
    """
    Generator that yields filtered users (age > 25) in batches.
    """
    for batch in stream_users_in_batches(batch_size):  # Loop 2
        filtered = [user for user in batch if user["age"] > 25]  # Loop 3
        yield filtered
