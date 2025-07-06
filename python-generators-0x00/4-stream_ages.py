import mysql.connector

def connect_to_prodev():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="ALX_prodev"
    )

def stream_user_ages():
    conn = connect_to_prodev()
    cursor = conn.cursor()
    cursor.execute("SELECT age FROM user_data")
    for (age,) in cursor:
        yield age
    cursor.close()
    conn.close()

def calculate_average_age():
    total_age = 0
    count = 0
    for age in stream_user_ages():
        total_age += float(age)
        count += 1
    if count > 0:
        avg = total_age / count
        print(f"Average age of users: {avg:.2f}")
    else:
        print("No users found.")

# Call the function
calculate_average_age()
