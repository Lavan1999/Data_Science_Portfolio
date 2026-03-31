from datetime import datetime
import json
from src.utils.client_llm import llm


def extract_last_json(text: str) -> dict:
    decoder = json.JSONDecoder()
    idx = 0
    last_obj = None

    while idx < len(text):
        try:
            obj, end = decoder.raw_decode(text[idx:])
            if isinstance(obj, dict) and "declaration_status" in obj:
                last_obj = obj
            idx += end
        except json.JSONDecodeError:
            idx += 1

    if last_obj is None:
        raise ValueError("No complete final declaration JSON found")

    return last_obj


def ai_verify_and_decide(cdm_payload: dict) -> dict:
    """
    Decide final declaration status based on CDM agent output
    """

    # 1 Extract declaration_id
    declaration_id = cdm_payload["result"]["declaration_id"]

    # 2 Collect all CDM decisions
    cdm_decisions = []
    for item in cdm_payload["result"]["results"]:
        decision = item.get("output", {}).get("cdm_decision")
        if decision:
            cdm_decisions.append(decision.upper())

    # Safety check
    if not cdm_decisions:
        raise ValueError("No CDM decisions found in payload")

    # 3 Build prompt (reasoning + strict output)
    prompt = f"""
        You are an Agentic AI responsible for deciding the FINAL DECLARATION STATUS
        after CDM approval.

        --------------------------------------------------
        CDM DECISION INTERPRETATION RULES (STRICT)

        - If cdm_decision contains "UNDER" or "OVER" → CORRECTION
        - If cdm_decision contains "INVALID", "INCORRECT HS", or "NO DATA" → CORRECTION
        - If cdm_decision contains "ACCEPT" → ACCEPTED
        - If cdm_decision contains "NEED REVIEW" or "ERROR" → NEED_REVIEW
        - If cdm_decision contains "PENDING" or "WAIT" → PENDING
        - If cdm_decision contains "REJECT" or "BLOCK" → REJECTED

        If multiple signals exist, choose the STRICTEST outcome.

        --------------------------------------------------
        FINAL DECLARATION STATUS RULES (PRIORITY ORDER)

        1. Any REJECTED → "On-hold"
        2. Any CORRECTION → "Sent for Correction"
        3. Any PENDING → "Pending"
        4. Any NEED_REVIEW → "On-hold"
        5. All ACCEPTED → "Approved"

        --------------------------------------------------
        OUTPUT FORMAT (JSON ONLY)

        {{
        "declaration_id": "{declaration_id}",
        "declaration_status": "<final_declaration_status>",
        "status_reason": "<clear explanation>",
        "updated_by": "Agentic AI",
        "updated_timestamp": "{datetime.utcnow().isoformat()}Z"
        }}

        DO NOT add extra fields.
        DO NOT explain outside JSON.

        --------------------------------------------------
        CDM DECISIONS:
        {cdm_decisions}
        """

    response_text = llm(prompt)
    print("Raw LLM Response:", response_text)

    result = extract_last_json(response_text)

    # HARD TYPE CHECK
    if not isinstance(result, dict):
        raise ValueError(f"Expected dict, got {type(result)}")

    required_keys = {
        "declaration_id",
        "declaration_status",
        "status_reason",
        "updated_by",
        "updated_timestamp"
    }

    if not required_keys.issubset(result.keys()):
        raise ValueError("Final declaration JSON missing required fields")

    return result

