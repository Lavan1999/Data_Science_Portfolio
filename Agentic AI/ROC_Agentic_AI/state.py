from typing import Any, Dict, List, Optional

from typing_extensions import TypedDict


class RCAState(TypedDict):
    customer_id: str
    transaction_id: str

    db_result: Optional[Dict[str, Any]]
    api_result: Optional[Dict[str, Any]]
    log_result: Optional[List[str]]

    trace_id: Optional[str]

    correlated_data: Optional[Dict[str, Any]]

    analysis: Optional[Dict[str, Any]]

    response: Optional[Dict[str, Any]]