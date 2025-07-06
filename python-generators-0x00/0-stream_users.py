import mysql.connector

def stream_users():
    """
    Generator that yields rows from the user_data table one by one.
    Uses a single loop and minimizes memory usage.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",      # replace with your MySQL username
            password="root",  # replace with your MySQL password
            database="ALX_prodev"
        )

        cursor = connection.cursor(dictionary=True)  # return rows as dicts
        cursor.execute("SELECT * FROM user_data")

        for row in cursor:
            yield row

    except mysql.connector.Error as err:
        print(f"[❌] Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Example usage (optional):
if __name__ == "__main__":
    for user in stream_users():
        print(user)
