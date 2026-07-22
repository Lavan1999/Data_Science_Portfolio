import sqlite3
from pathlib import Path
from datetime import datetime, timedelta


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

DB_PATH = PROJECT_DIR / "database" / "db.sqlite"
LOG_FILE = BASE_DIR / "application.log"


conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

transactions = cursor.execute("""
SELECT
    transactionId,
    customerId,
    traceId,
    status,
    failureScenario,
    timestamp
FROM transactions
""").fetchall()


def generate_logs(transaction):

    transaction_id = transaction[0]
    customer_id = transaction[1]
    trace_id = transaction[2]
    status = transaction[3]
    failure = transaction[4]
    timestamp = transaction[5]

    start_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    logs = []

    def add_log(seconds, level, service, message):
        log_time = start_time + timedelta(seconds=seconds)

        logs.append(
            f"{log_time.strftime('%Y-%m-%d %H:%M:%S')} "
            f"{level} "
            f"traceId={trace_id} "
            f"customerId={customer_id} "
            f"transactionId={transaction_id} "
            f"service={service} "
            f"message=\"{message}\""
        )

    add_log(0, "INFO", "CustomerService", "Customer request received")

    add_log(2, "INFO", "OrderService", "Order validation completed")

    add_log(4, "INFO", "PaymentService", "Payment processing started")

    if status == "SUCCESS":

        add_log(6, "INFO", "PaymentGateway", "Payment completed successfully")

        add_log(8, "INFO", "NotificationService", "Confirmation notification sent")

    else:

        if failure == "Gateway Timeout":

            add_log(6, "ERROR", "PaymentGateway", "HTTP 504 Gateway Timeout")

            add_log(8, "ERROR", "PaymentService", "Transaction marked as FAILED")

        elif failure == "Inventory Unavailable":

            add_log(6, "ERROR", "InventoryService", "Requested item out of stock")

            add_log(8, "ERROR", "OrderService", "Order cancelled")

        elif failure == "Database Connection Error":

            add_log(6, "ERROR", "DatabaseService", "Unable to connect to database")

            add_log(8, "ERROR", "PaymentService", "Transaction rolled back")

        elif failure == "Authentication Failure":

            add_log(6, "ERROR", "AuthService", "Token validation failed")

            add_log(8, "ERROR", "PaymentService", "Unauthorized request")

    return logs


all_logs = []

for transaction in transactions:
    all_logs.extend(generate_logs(transaction))


with open(LOG_FILE, "w", encoding="utf-8") as file:

    for log in all_logs:
        file.write(log + "\n")


print(f"Generated {len(all_logs)} log entries.")
print(f"Log file created at:\n{LOG_FILE}")

conn.close()