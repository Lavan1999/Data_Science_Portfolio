import json
from pathlib import Path

from fastapi import FastAPI, HTTPException


app = FastAPI(
    title="Mock Payment Gateway API",
    version="1.0"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "mock_data.json"


with open(DATA_FILE, "r", encoding="utf-8") as file:
    transactions = json.load(file)


@app.get("/")
def home():
    return {
        "message": "Mock Payment Gateway API is running."
    }


@app.get("/transaction/{transaction_id}")
def get_transaction(transaction_id: str):

    for transaction in transactions:

        if transaction["transactionId"] == transaction_id:
            return transaction

    raise HTTPException(
        status_code=404,
        detail="Transaction not found"
    )