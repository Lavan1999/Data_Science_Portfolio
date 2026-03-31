from typing import Optional, Dict, Any
import requests
import json
import re

from src.memory.agentstate import (
    ValuationExtractedData,
    ValuationFeedback,
    CDMDecision,
    OrchestratorAgentState,
    RiskProfile
)
#from langgraph.prebuilt import agent
from src.utils.client_llm import llm


# Valuation Verifier Agent
#@agent(name="valuation_verifier_agent", description="Verify valuation details using rule-based checks and LLM.")
def valuation_verifier_agent(
    orch_data: OrchestratorAgentState,
    risk_profile: RiskProfile
) -> None:
    """
    Verifies valuation using rule-based checks + LLM explanation.
    Reads from orch_data.cdm_extracted
    Assigns CDMDecision into orch_data.cdm_decision
    """

    risk_id = risk_profile.risk_id

    # Extract Required Data
    cdm_extracted = orch_data.cdm_extracted

    declaration = (
        cdm_extracted.declaration_details
        if cdm_extracted
        else None
    )

    valuation_data: Optional[ValuationExtractedData] = (
        cdm_extracted.valuation_extracted_data
        if cdm_extracted
        else None
    )

    # Validation
    if not declaration:
        orch_data.cdm_decision = CDMDecision(
            risk_id=risk_id,
            valuation_feedback=ValuationFeedback(
                status="NEED REVIEW",
                explanation="Declaration details are missing; valuation verification could not be performed."
            )
        )
        return

    if valuation_data is None:
        orch_data.cdm_decision = CDMDecision(
            risk_id=risk_id,
            valuation_feedback=ValuationFeedback(
                status="DATA MISSING",
                explanation="No valuation reference data found for the declared HS code; please revalidate."
            )
        )
        return

    # Prepare Numeric Values
    try:
        declared_price = float(declaration.goods_value or 0)
        quantity = float(declaration.static_quantity_unit or 1)

        db_unit_price = float(valuation_data.price or 0)
        allowed_variation = float(valuation_data.variation_percentage or 0)
    except ValueError:
        orch_data.cdm_decision = CDMDecision(
            risk_id=risk_id,
            valuation_feedback=ValuationFeedback(
                status="NEED REVIEW",
                explanation="Invalid numeric values encountered during valuation verification."
            )
        )
        return

    db_total_price = db_unit_price * quantity

    # Discrepancy Percentage Calculation
    if db_total_price > 0:
        discrepancy_percentage = abs(
            ((declared_price - db_total_price) / db_total_price) * 100
        )
    else:
        discrepancy_percentage = 0

    lower_limit = db_total_price * (1 - allowed_variation / 100)
    upper_limit = db_total_price * (1 + allowed_variation / 100)

    # Deterministic Decision
    if declared_price < lower_limit:
        status = "UNDER VALUED"
    elif declared_price > upper_limit:
        status = "OVER VALUED"
    else:
        status = "ACCEPTED"

    # Build LLM Prompt -- correct failed field
    prompt = f"""
            You are a customs valuation verification specialist.

            ### USER DECLARATION INPUT
            HS Code: {declaration.hs_code}
            Quantity: {quantity}
            Declared Total Price: {declared_price}

            ### DATABASE REFERENCE VALUES
            Unit Price: {db_unit_price}
            Allowed Variation: ±{allowed_variation}%
            DB Total Price: {db_total_price}
            Acceptable Range: {lower_limit:.2f} - {upper_limit:.2f}

            ### RISK PROFILE REASON
            Reason: {risk_profile.risk_description}

            ### RESULT (ALREADY DETERMINED)
            Status: {status}

            ### TASK
            - Write a concise technical explanation (max 50 words) justifying the status.
            - Do NOT recalculate values.
            - Do NOT change the status.
            - If status is UNDERVALUED or OVERVALUED, provide the correct valuation amount.

            ### RESPONSE FORMAT

            Status: {status}

            [Only if Status is UNDERVALUED or OVERVALUED]
            Failed_Field: goods_value
            Correct_Value: {db_total_price}

            Explanation: <text>

            """
    
    # Call LLM & Store Decision
    try:
        reply = llm(prompt).strip()

        # Default values
        explanation = reply
        failed_field = None
        correct_value = None

        # Try JSON parsing first
        if reply.startswith("{"):
            try:
                parsed = json.loads(reply)
                status = parsed.get("Status", status)
                explanation = parsed.get("Explanation", "")
                failed_field = parsed.get("Failed_Field", None)
                correct_value = parsed.get("Correct_Value", None)
            except (json.JSONDecodeError, ValueError):
                # Fallback to text parsing
                if "Explanation:" in reply:
                    explanation = reply.split("Explanation:")[1].strip()
                if "Failed_Field:" in reply:
                    failed_field = reply.split("Failed_Field:")[1].split("\n")[0].strip()
                if "Correct_Value:" in reply:
                    correct_value = reply.split("Correct_Value:")[1].split("\n")[0].strip()
        else:
            # Text format parsing
            if "Explanation:" in reply:
                explanation = reply.split("Explanation:")[1].strip()
            if "Failed_Field:" in reply:
                failed_field = reply.split("Failed_Field:")[1].split("\n")[0].strip()
            if "Correct_Value:" in reply:
                correct_value = reply.split("Correct_Value:")[1].split("\n")[0].strip()

        # AUTO-CORRECTION (safe)
        if failed_field == "goods_value" and correct_value and declaration:
            declaration.goods_value = correct_value

        # STORE FEEDBACK
        orch_data.cdm_decision = CDMDecision(
            risk_id=risk_id,
            valuation_feedback=ValuationFeedback(
                status=status,
                explanation=explanation,
                failed_field=failed_field,
                correct_value=correct_value,
                discrepancy_percentage=round(discrepancy_percentage, 2)
            )
        )

    except Exception:
        # Fallback: Still provide failed_field and correct_value for UNDER/OVER VALUED
        failed_field_fallback = "goods_value" if status in ["UNDER VALUED", "OVER VALUED"] else None
        correct_value_fallback = str(round(db_total_price, 2)) if status in ["UNDER VALUED", "OVER VALUED"] else None
        
        orch_data.cdm_decision = CDMDecision(
            risk_id=risk_id,
            valuation_feedback=ValuationFeedback(
                status=status,
                explanation="Valuation status determined by rule-based checks; LLM explanation unavailable.",
                failed_field=failed_field_fallback,
                correct_value=correct_value_fallback,
                discrepancy_percentage=round(discrepancy_percentage, 2)
            )
        )