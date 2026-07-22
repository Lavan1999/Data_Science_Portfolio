import requests
from state import RCAState
from config import MOCK_API_URL


def api_tool(state: RCAState) -> RCAState:

    transaction_id = state["transaction_id"]

    response = requests.get(
        f"{MOCK_API_URL}/transaction/{transaction_id}",
        timeout=10
    )

    if response.status_code != 200:
        raise Exception(
            f"Failed to retrieve API data for {transaction_id}"
        )

    state["api_result"] = response.json()

    return state