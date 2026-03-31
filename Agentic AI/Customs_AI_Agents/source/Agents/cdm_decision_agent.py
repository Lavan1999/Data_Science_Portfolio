from typing import Optional
from src.memory.agentstate import (
    OrchestratorAgentState,
    TariffFeedback,
    ValuationFeedback,
    InspectionFeedback
)
from src.utils.client_llm import llm
import json


def _normalize_status(status: Optional[str]) -> str:
    if not status:
        return ""
    return str(status).strip().upper()


#@agent(name="cdm_decision_agent", description="Make final cdm decision based on verifier feedback.")
def cdm_decision_agent(orch_data: OrchestratorAgentState) -> OrchestratorAgentState:
    """
    Deterministic CDM Decision Layer
    - Uses ONLY feedback.status
    - Never overrides from explanation
    - Never double-encodes JSON
    - Never directly DECLINES (inspection handles illegal)
    """

    print("[CDM DECISION NODE] Executing")

    decision = orch_data.cdm_decision
    if decision is None:
        raise ValueError("CDMDecision missing in OrchestratorAgentState")

    # Select feedback based on risk_type
    feedback: Optional[
        TariffFeedback | ValuationFeedback | InspectionFeedback
    ] = None

    risk_type = getattr(decision, "risk_type", None)
    if risk_type:
        rt = str(risk_type).strip().upper()
        if rt == "TARIFF":
            feedback = decision.tariff_feedback
        elif rt == "VALUATION":
            feedback = decision.valuation_feedback
        elif rt == "INSPECTION":
            feedback = decision.inspection_feedback

    if feedback is None:
        feedback = (
            decision.tariff_feedback
            or decision.valuation_feedback
            or decision.inspection_feedback
        )

    if feedback is None:
        decision.cdm_decision = "NEED REVIEW"
        decision.cdm_feedback = {
            "Explanation": "No verifier feedback available."
        }
        orch_data.orchestrator_status = "DECIDING"
        return orch_data
        

    #status = _normalize_status(feedback.status)
    #  SINGLE SOURCE OF TRUTH
    if feedback.explanation:
        try:
            explanation_json = json.loads(feedback.explanation) if isinstance(feedback.explanation, str) else feedback.explanation
            if isinstance(explanation_json, dict) and "Status" in explanation_json:
                # Synchronize feedback.status with explanation['Status']
                feedback.status = explanation_json["Status"]
                status = _normalize_status(explanation_json["Status"])
            else:
                status = _normalize_status(feedback.status) if feedback.status else None
        except Exception:
            status = _normalize_status(feedback.status) if feedback.status else None
    else:
        status = _normalize_status(feedback.status) if feedback.status else None

    # RULE-BASED MAPPING

    if "UNDER" in status or "OVER" in status:
        final_decision = "CORRECTION"

    elif "MANUAL INSPECTION" in status:
        final_decision = "INSPECTION"

    elif "INVALID" in status or "INCORRECT HS CODE" in status or "NO DATA" in status:
        final_decision = "INVALID HS CODE"

    elif "ACCEPT" in status or "ACCEPTED" in status:
        final_decision = "ACCEPTED"

    elif "NEED REVIEW" in status or "ERROR" in status:
        final_decision = "NEED REVIEW"

    else:
        final_decision = None #Fallback to LLM if status is ambiguous or missing

    # LLM FOR EXPLANATION ONLY

    if final_decision:
        try:
            prompt = f"""you are a senior customs officer.
            Verifier Status:
            {feedback.status}

            Verifier Explanation:
            {feedback.explanation}

            Final CDM Decision:
            {final_decision}

            Write a concise technical justification (max 50 words).

                    Response format:
                    Explanation: <text>
                    """
            out = llm(prompt).strip()
            
            # Try JSON parsing first
            explanation = out
            if out.startswith("{"):
                try:
                    parsed = json.loads(out)
                    explanation = parsed.get("Explanation", out)
                except (json.JSONDecodeError, ValueError):
                    # Fallback to text parsing
                    explanation = (
                        out.split("Explanation:")[1].strip()
                        if "Explanation:" in out
                        else out
                    )
            else:
                # Text format parsing
                explanation = (
                    out.split("Explanation:")[1].strip()
                    if "Explanation:" in out
                    else out
                )
            
            
            
        except Exception:
            explanation = f"Final decision derived from verifier status: {feedback.status}"

            carried_failed_field = feedback.failed_field if final_decision == "CORRECTION" else None
            carried_correct_value = feedback.correct_value if final_decision == "CORRECTION" else None

            decision.cdm_decision = final_decision
            decision.cdm_feedback = explanation
            decision.failed_field = carried_failed_field
            decision.correct_value = carried_correct_value

            orch_data.orchestrator_status = "DECIDING"
            return orch_data
        
    # Fallback to LLM for final decision if status is ambiguous or missing

    try:
        prompt = f"""
        You are a senior customs officer.

        Verifier Status:
        {feedback.status}

        Verifier Explanation:
        {feedback.explanation}

        Final CDM Decision:
        {final_decision}

        Your task:
        Provide a concise technical justification (maximum 25 words).

        STRICT RULES:
        - Output must be valid JSON.
        - Output must contain ONLY one key: "Explanation".
        - Explanation must be plain text.
        - Do NOT include additional JSON inside the explanation.
        - Do NOT include line breaks.
        - Do NOT include extra fields.
        - Do NOT add commentary outside JSON.

        Expected Output Format (example):

        {{
        "Explanation": "Declared value aligns with regulation; no discrepancies identified."
        }}

        Now produce the final output.
        """

        out = llm(prompt).strip()

        # Try JSON parsing first
        explanation = out
        if out.startswith("{"):
            try:
                parsed = json.loads(out)
                explanation = parsed.get("Explanation", out)
            except (json.JSONDecodeError, ValueError):
                # Fallback to text parsing
                explanation = (
                    out.split("Explanation:")[1].strip()
                    if "Explanation:" in out
                    else out
                )
        else:
            # Text format parsing
            explanation = (
                out.split("Explanation:")[1].strip()
                if "Explanation:" in out
                else out
            )

        decision_label = (
            out.split("Decision:")[1].split("\n")[0].strip().upper()
            if "Decision:" in out
            else out.split("\n")[0].strip().upper()
        )

        if "ACCEPT" in decision_label:
            final_decision = "ACCEPTED"
        elif "CORRECT" in decision_label:
            final_decision = "CORRECTION"
        elif "INSPECT" in decision_label:
            final_decision = "INSPECTION"
        elif "DECLINE" in decision_label or "REJECT" in decision_label:
            final_decision = "DECLINED"
        else:
            final_decision = "NEED REVIEW"

        # Carry forward failed_field & correct_value only if CORRECTION
        carried_failed_field = feedback.failed_field if final_decision == "CORRECTION" else None
        carried_correct_value = feedback.correct_value if final_decision == "CORRECTION" else None        

        # STRUCTURED OUTPUT
        decision.cdm_decision = final_decision
        decision.cdm_feedback = explanation
        decision.failed_field = carried_failed_field
        decision.correct_value = carried_correct_value  

    except Exception:
        explanation = f"Final decision derived from verifier status: {feedback.status}"

        decision.cdm_decision = final_decision
        decision.cdm_feedback = explanation

    # Final metadata assignment
    if final_decision == "CORRECTION":
        decision.failed_field = feedback.failed_field
        decision.correct_value = feedback.correct_value
    else:
        decision.failed_field = None
        decision.correct_value = None

    orch_data.orchestrator_status = "DECIDING"
    return orch_data