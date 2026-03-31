from typing import List, Dict, Any
from src.tools.declaration_details_retriever import fetch_declaration_details
from src.memory.agentstate import (
    RiskProfile,
    CDMInput,
    CDMExtracted,
    OrchestratorAgentState,
    CDMDecision
)
from src.workflow.cdm_graph import run_cdm_manager


def run_orchestrator(
    declaration_id: str,
    risk_profiles: List[RiskProfile]
) -> Dict[str, Any]:

    print("\n---> STARTING MULTI-RISK CDM AGENT FLOW\n")

    final_output: Dict[str, Any] = {
        "declaration_id": declaration_id,
        "declaration_details": None,
        "results": []
    }

    # 1. Fetch Declaration Details (ONCE)
    try:
        declaration_details = fetch_declaration_details(declaration_id)
    except Exception as e:
        print(f"\n---> Failed to fetch declaration details: {e}")
        return final_output

    if not declaration_details or not declaration_details.hs_code:
        print("\n---> No HS Code found for this declaration ID")
        return final_output

    print("---> Declaration details fetched")
    print("HS Code:", declaration_details.hs_code)

    # Store ONLY required fields
    final_output["declaration_details"] = {
        "hs_code": declaration_details.hs_code,
        "product_name": declaration_details.goods_description,
        "country": declaration_details.country
    }

    # 2. Process EACH Risk Independently
    for risk_profile in risk_profiles:

        print(f"\n---> Processing Risk ID: {risk_profile.risk_id}")

        # Create NEW CDM Input (per risk)
        cdm_input = CDMInput(
            declaration_id=declaration_id,
            risk_profile=risk_profile
        )

        # Task 1: Create NEW OrchestratorAgentState
        orch_state = OrchestratorAgentState(
            cdm_input=cdm_input,
            cdm_extracted=CDMExtracted(
                declaration_details=declaration_details
            ),
            cdm_decision=None
        )

        decision: CDMDecision | None = None

        try:
            orch_state = run_cdm_manager(orch_state)
            decision = orch_state.cdm_decision
        except Exception as e:
            print(f"---> CDM failed for risk {risk_profile.risk_id}: {e}")

        # Store Output (JSON-safe)
        # final_output["results"].append({
        #     "risk_id": risk_profile.risk_id,
        #     "output": {
        #         "tariff_feedback": decision.tariff_feedback if decision else None,
        #         "valuation_feedback": decision.valuation_feedback if decision else None,
        #         "cdm_decision": decision.cdm_decision if decision else None,
        #         "cdm_feedback": decision.cdm_feedback if decision else None,
        #         "failed_field": decision.failed_field if decision else None,
        #         "correct_value": decision.correct_value if decision else None
        #     }
        # })

        # Store Output (JSON-safe)
        # Build output dict
        output_dict = {
            "cdm_decision": decision.cdm_decision if decision else None,
            "cdm_feedback": decision.cdm_feedback if decision else None,
        }


        # Include other fields only if they are not None
        import json
        def parse_explanation(feedback):
            if feedback is None:
                return None
            feedback_dict = feedback.dict() if hasattr(feedback, 'dict') else dict(feedback)
            explanation = feedback_dict.get('explanation')
            if isinstance(explanation, str):
                try:
                    parsed = json.loads(explanation)
                    feedback_dict['explanation'] = parsed
                except Exception:
                    pass
            return feedback_dict

        if decision:
            if decision.tariff_feedback is not None:
                output_dict["tariff_feedback"] = parse_explanation(decision.tariff_feedback)
            if decision.valuation_feedback is not None:
                output_dict["valuation_feedback"] = parse_explanation(decision.valuation_feedback)
            if decision.inspection_feedback is not None:
                output_dict["inspection_feedback"] = parse_explanation(decision.inspection_feedback)
            if decision.failed_field is not None:
                output_dict["failed_field"] = decision.failed_field
            if decision.correct_value is not None:
                output_dict["correct_value"] = decision.correct_value

        final_output["results"].append({
            "risk_id": risk_profile.risk_id,
            "output": output_dict
        })



        # Optional debug prints
        print(
            decision.tariff_feedback
            if hasattr(decision, "tariff_feedback")
            else "---> No tariff feedback available"
        )
        print(
            decision.valuation_feedback
            if hasattr(decision, "valuation_feedback")
            else "---> No valuation feedback available"
        )
        print(
            decision.inspection_feedback
            if hasattr(decision, "inspection_feedback")
            else "---> No inspection feedback available"
        )

        # Task 2: DELETE Orchestrator State
        del orch_state
        del decision

    print("\n---> MULTI-RISK CDM AGENT FLOW COMPLETED\n")

    def format_cdm_response(response: dict) -> dict:
        import copy

        def clean_dict(d):
            # Remove keys with None/null values
            return {k: v for k, v in d.items() if v is not None}

        resp = copy.deepcopy(response)
        for result in resp.get("results", []):
            output = result.get("output", {})
            # For each feedback type
            for fb_key in ["tariff_feedback", "valuation_feedback", "inspection_feedback"]:
                fb = output.get(fb_key)
                if isinstance(fb, dict):
                    # If explanation is a dict, extract failed_field/correct_value if present
                    explanation = fb.get("explanation")
                    if isinstance(explanation, dict):
                        # Set failed_field/correct_value from explanation if not already set
                        if not fb.get("failed_field") and explanation.get("Failed_Field"):
                            fb["failed_field"] = explanation["Failed_Field"]
                        if not fb.get("correct_value") and explanation.get("Correct_Value") is not None:
                            fb["correct_value"] = explanation["Correct_Value"]
                        # If failed_field is 'none', ensure correct_value is also None
                        if fb.get("failed_field") == "none":
                            fb["correct_value"] = None
                    # Remove null fields from feedback
                    output[fb_key] = clean_dict(fb)
            # Remove null fields from output
            result["output"] = clean_dict(output)
        return resp

    return format_cdm_response(final_output)

