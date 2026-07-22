import sqlite3
from pathlib import Path

from state import RCAState


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "db.sqlite"


def database_tool(state: RCAState) -> RCAState:

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    query = """
        SELECT
            c.customerId,
            c.customerName,
            c.email,
            c.phone,
            t.transactionId,
            t.traceId,
            t.amount,
            t.status,
            t.failureScenario,
            t.timestamp
        FROM customers c
        JOIN transactions t
            ON c.customerId = t.customerId
        WHERE
            c.customerId = ?
        AND
            t.transactionId = ?
    """

    cursor.execute(
        query,
        (
            state["customer_id"],
            state["transaction_id"]
        )
    )

    result = cursor.fetchone()

    conn.close()

    if result is None:
        raise ValueError(
            f"Transaction '{state['transaction_id']}' not found."
        )

    db_result = dict(result)

    state["db_result"] = db_result
    state["trace_id"] = db_result["traceId"]

    return state