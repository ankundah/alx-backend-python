# Database Seeder - `seed.py`

This script sets up and seeds a MySQL database named `ALX_prodev` with user data sourced from a remote CSV file. It automates the creation of the database, table structure, and populates it with sample data using Python.

---

## 📦 Features

- Automatically downloads `user_data.csv` from a public S3 link
- Creates the `ALX_prodev` MySQL database if it doesn't exist
- Creates a table called `user_data` with the following schema:
  - `user_id`: UUID, Primary Key, Indexed
  - `name`: VARCHAR, Not Null
  - `email`: VARCHAR, Not Null
  - `age`: DECIMAL, Not Null
- Loads CSV data and inserts it into the table
- Skips duplicates based on primary key

---

## 🛠️ Table Schema

```sql
CREATE TABLE user_data (
    user_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    age DECIMAL NOT NULL
);
