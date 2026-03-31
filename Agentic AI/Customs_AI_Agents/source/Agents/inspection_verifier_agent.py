from typing import Optional
from src.memory.agentstate import (
    InspectionFeedback,
    CDMDecision,
    OrchestratorAgentState,
    RiskProfile
)
from src.utils.client_llm import llm
import json

def inspection_agent(
    orch_data: OrchestratorAgentState,
    risk_profile: RiskProfile
) -> OrchestratorAgentState:
    """
    LLM-based Inspection Agent.
    Checks goods_description for restricted/prohibited items.
    """

    risk_id = risk_profile.risk_id

    declaration = (
        orch_data.cdm_extracted.declaration_details
        if orch_data.cdm_extracted
        else None
    )

    # Initialize CDMDecision if not already present
    if orch_data.cdm_decision is None:
        orch_data.cdm_decision = CDMDecision(risk_id=risk_id)
    else:
        orch_data.cdm_decision.risk_id = risk_id

    if not declaration or not declaration.goods_description:
        orch_data.cdm_decision.inspection_feedback = InspectionFeedback(
            status="NEED REVIEW",
            explanation="Goods description missing; inspection validation could not be performed."
        )
        return orch_data

    description = declaration.goods_description

    # LLM Prompt
    
    prompt = f"""
You are a Dubai Customs Inspection Risk Assessment Assistant.

### USER DECLARATION INPUT
Goods Description: {description}

### TASK
Analyze the goods description and determine whether it belongs to any of the following categories:

1. Alcohol or Tobacco products
2. Illegal or controlled medical drugs
3. Prohibited or restricted items in Dubai
   (e.g., narcotics, weapons, counterfeit goods, gambling devices, hazardous materials, banned publications)

### IMPORTANT RULES
- Use semantic understanding (not keyword matching only).
- Consider synonyms, indirect references, and disguised wording.
- If the item clearly belongs to any listed category → MANUAL INSPECTION REQUIRED.
- If the description is suspicious or unclear → MANUAL INSPECTION REQUIRED.
- If the item is clearly safe and unrelated to all categories → ACCEPTED.
- DO NOT make a final customs clearance decision.
- Your role is only to recommend whether inspection is required.
- Keep explanation under 60 words.
- Be strict and risk-aware.

### RESPONSE FORMAT (STRICT — DO NOT DEVIATE)

Inspection_Status: <ACCEPTED / MANUAL INSPECTION REQUIRED>
Matched_Category: <Alcohol/Tobacco / Illegal Drugs / Prohibited Items / None>
Risk_Level: <LOW / MEDIUM / HIGH>
Inspection_Feedback: <Short justification under 60 words>
"""

    try:
        reply = llm(prompt).strip()
        print(f"[INSPECTION AGENT] LLM Response for Risk {risk_id}:\n{reply}\n")

        status = "NEED REVIEW"
        explanation = reply
        matched_category = None

        # Try JSON parsing first
        if reply.startswith("{"):
            try:
                parsed = json.loads(reply)
                status = parsed.get("Inspection_Status", status)
                matched_category = parsed.get("Matched_Category", matched_category)
                explanation = parsed.get("Inspection_Feedback", "")
            except (json.JSONDecodeError, ValueError):
                # Fallback to text parsing
                if "Inspection_Status:" in reply:
                    status = reply.split("Inspection_Status:")[1].split("\n")[0].strip()
                if "Matched_Category:" in reply:
                    matched_category = reply.split("Matched_Category:")[1].split("\n")[0].strip()
                    if matched_category.lower() == "none":
                        matched_category = None
                if "Inspection_Feedback:" in reply:
                    explanation = reply.split("Inspection_Feedback:")[1].strip()
        else:
            # Text format parsing
            if "Inspection_Status:" in reply:
                status = reply.split("Inspection_Status:")[1].split("\n")[0].strip()
            if "Matched_Category:" in reply:
                matched_category = reply.split("Matched_Category:")[1].split("\n")[0].strip()
                if matched_category and matched_category.lower() == "none":
                    matched_category = None
            if "Inspection_Feedback:" in reply:
                explanation = reply.split("Inspection_Feedback:")[1].strip()

        print(f"[INSPECTION AGENT] Parsed - Status: {status}, Matched_Category: {matched_category}\n")

        orch_data.cdm_decision.inspection_feedback = InspectionFeedback(
            status=status,
            explanation=explanation,
            matched_category=matched_category
        )

    except Exception as e:
        print(f"[INSPECTION AGENT ERROR] {str(e)}")
        orch_data.cdm_decision.inspection_feedback = InspectionFeedback(
            status="NEED REVIEW",
            explanation="Inspection verification failed due to internal processing error."
        )

    return orch_data