import json
import sqlite3
from pathlib import Path
from random import choice, randint


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

DB_PATH = PROJECT_DIR / "database" / "db.sqlite"
OUTPUT_FILE = BASE_DIR / "mock_data.json"


conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

transactions = cursor.execute("""
SELECT
    transactionId,
    traceId,
    status,
    failureScenario
FROM transactions
""").fetchall()


gateways = [
    "Stripe",
    "Razorpay",
    "PayPal",
    "Adyen",
    "Authorize.Net"
]


responses = []

for transaction in transactions:

    transaction_id = transaction[0]
    trace_id = transaction[1]
    status = transaction[2]
    failure = transaction[3]

    gateway = choice(gateways)

    response = {
        "transactionId": transaction_id,
        "traceId": trace_id,
        "service": "PaymentGateway",
        "gateway": gateway,
        "endpoint": "/payments/process"
    }

    if status == "SUCCESS":

        response.update({
            "httpStatus": 200,
            "latencyMs": randint(120, 650),
            "retryCount": 0,
            "errorCode": None,
            "errorMessage": None,
            "gatewayStatus": "SUCCESS"
        })

    elif failure == "Gateway Timeout":

        response.update({
            "httpStatus": 504,
            "latencyMs": randint(6000, 9000),
            "retryCount": 3,
            "errorCode": "GW_TIMEOUT_504",
            "errorMessage": "Gateway Timeout",
            "gatewayStatus": "FAILED"
        })

    elif failure == "Inventory Unavailable":

        response.update({
            "httpStatus": 409,
            "latencyMs": randint(200, 600),
            "retryCount": 0,
            "errorCode": "INV_OUT_OF_STOCK",
            "errorMessage": "Inventory Unavailable",
            "gatewayStatus": "FAILED"
        })

    elif failure == "Database Connection Error":

        response.update({
            "httpStatus": 500,
            "latencyMs": randint(2500, 4500),
            "retryCount": 1,
            "errorCode": "DB_CONN_500",
            "errorMessage": "Database Connection Error",
            "gatewayStatus": "FAILED"
        })

    elif failure == "Authentication Failure":

        response.update({
            "httpStatus": 401,
            "latencyMs": randint(150, 400),
            "retryCount": 0,
            "errorCode": "AUTH_401",
            "errorMessage": "Authentication Failure",
            "gatewayStatus": "FAILED"
        })

    responses.append(response)


with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(responses, file, indent=4)


print(f"Generated {len(responses)} API records.")
print(f"Saved to: {OUTPUT_FILE}")

conn.close()