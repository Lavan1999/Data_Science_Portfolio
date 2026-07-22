from state import RCAState


def formatter_agent(state: RCAState) -> RCAState:
    print("===== FORMATTER AGENT INPUT =====")
    print(state)
    print("===========================")
    analysis = state.get("analysis")
    db_result = state.get("db_result")

    if not analysis:
        raise ValueError("Analysis agent did not return any result")

    state["response"] = {
        "customerId": db_result.get("customerId"),
        "transactionId": db_result.get("transactionId"),
        "rootCause": analysis.get("rootCause", ""),
        "failureFlow": analysis.get("failureFlow", []),
        "evidence": analysis.get("evidence", []),
        "recommendation": analysis.get("recommendation", [])
    }
    print(state)
    print("db_result:", state.get("db_result"))
    print("analysis:", state.get("analysis"))

    return state