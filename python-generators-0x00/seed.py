import requests

CSV_URL = "https://s3.amazonaws.com/alx-intranet.hbtn.io/uploads/misc/2024/12/3888260f107e3701e3cd81af49ef997cf70b6395.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDDGGGOUSBVO6H7D%2F20250706%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250706T094152Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=e7ed1615ffdca0c06a4400686bae4f78a0091f8f3ed91dda5853ceec0dcefda8"

def download_csv():
    response = requests.get(CSV_URL)
    with open("user_data.csv", "wb") as f:
        f.write(response.content)
    print("[✓] CSV downloaded successfully.")

import mysql.connector
import pandas as pd
import uuid

# ----- Configuration -----
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'root'  # Replace with your actual MySQL root password
DB_NAME = 'ALX_prodev'
TABLE_NAME = 'user_data'
CSV_FILE = 'user_data.csv'

# ----- Prototypes -----

def connect_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )

def create_database(connection):
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.close()

def connect_to_prodev():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def create_table(connection):
    cursor = connection.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(3,0) NOT NULL,
            INDEX (user_id)
        )
    """)
    connection.commit()
    cursor.close()

def insert_data(connection, data):
    cursor = connection.cursor()
    for _, row in data.iterrows():
        user_id = str(uuid.uuid4())
        # Check if email already exists
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE email = %s", (row['email'],))
        if cursor.fetchone() is None:
            cursor.execute(f"""
                INSERT INTO {TABLE_NAME} (user_id, name, email, age)
                VALUES (%s, %s, %s, %s)
            """, (user_id, row['name'], row['email'], row['age']))
    connection.commit()
    cursor.close()

# ----- Main Script -----
def main():
    print("[*] Connecting to MySQL server...")
    conn = connect_db()
    create_database(conn)
    conn.close()

    print("[*] Connecting to ALX_prodev...")
    prodev_conn = connect_to_prodev()
    create_table(prodev_conn)

    print(f"[*] Loading data from {CSV_FILE}...")
    data = pd.read_csv(CSV_FILE)

    print("[*] Inserting data into user_data table...")
    insert_data(prodev_conn, data)

    prodev_conn.close()
    print("[✓] Database seeded successfully.")

if __name__ == '__main__':
    main()
