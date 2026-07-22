from pathlib import Path

from state import RCAState


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "application.log"


def log_tool(state: RCAState) -> RCAState:

    trace_id = state["trace_id"]

    matched_logs = []

    with open(LOG_FILE, "r", encoding="utf-8") as file:

        for line in file:

            if f"traceId={trace_id}" in line:
                matched_logs.append(line.strip())

    state["log_result"] = matched_logs

    return state