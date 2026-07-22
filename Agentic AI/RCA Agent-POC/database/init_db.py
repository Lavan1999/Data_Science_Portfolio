import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "db.sqlite"
CUSTOMERS_CSV = BASE_DIR / "dataset" / "customers.csv"
TRANSACTIONS_CSV = BASE_DIR / "dataset" / "transactions.csv"


customers_df = pd.read_csv(CUSTOMERS_CSV)
transactions_df = pd.read_csv(TRANSACTIONS_CSV)


conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


cursor.execute("DROP TABLE IF EXISTS customers")
cursor.execute("DROP TABLE IF EXISTS transactions")


cursor.execute("""
CREATE TABLE customers (
    customerId TEXT PRIMARY KEY,
    customerName TEXT NOT NULL,
    email TEXT,
    phone TEXT
)
""")


cursor.execute("""
CREATE TABLE transactions (
    transactionId TEXT PRIMARY KEY,
    customerId TEXT,
    traceId TEXT,
    amount REAL,
    status TEXT,
    failureScenario TEXT,
    timestamp TEXT,
    FOREIGN KEY(customerId) REFERENCES customers(customerId)
)
""")


customers_df.to_sql(
    "customers",
    conn,
    if_exists="append",
    index=False
)

transactions_df.to_sql(
    "transactions",
    conn,
    if_exists="append",
    index=False
)

conn.commit()

customer_count = cursor.execute(
    "SELECT COUNT(*) FROM customers"
).fetchone()[0]

transaction_count = cursor.execute(
    "SELECT COUNT(*) FROM transactions"
).fetchone()[0]

print(f"Customers Loaded    : {customer_count}")
print(f"Transactions Loaded : {transaction_count}")
print(f"Database Created    : {DB_PATH}")

conn.close()