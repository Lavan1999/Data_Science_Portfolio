from typing import List, Dict, Any, Optional
from fastapi import WebSocket
import asyncio
import time
from src.tools.declaration_details_retriever import fetch_declaration_details
from src.memory.agentstate import (
    RiskProfile,
    CDMInput,
    CDMExtracted,
    OrchestratorAgentState,
    CDMDecision
)
from src.workflow.cdm_graph import run_cdm_manager
from declaration_status import ai_verify_and_decide

def filter_declaration_details(declaration_details):
    return {
        "hs_code": declaration_details.hs_code,
        "goods_description": declaration_details.goods_description,
        "country": declaration_details.country
    }

async def send_progress(websocket: WebSocket, stage: str, message: str, data: Optional[Dict] = None):
    """Helper function to send progress updates via WebSocket."""
    try:
        await websocket.send_json({
            "type": "progress",
            "stage": stage,
            "message": message,
            "data": data or {}
        })
    except Exception as e:
        print(f"Failed to send WebSocket message: {e}")


async def emit_progress_bar_update(
    websocket: WebSocket,
    declaration_id: str,
    current_agent: str,
    action_type: str,
    next_agent: str = None,
    event_type: str = None,
    details: Optional[Dict] = None
):
    """Emit ai-update-progress-bar event for frontend tracking."""
    try:
        payload = {
            "event": "ai-update-progress-bar",
            "declaration_id": declaration_id,
            "project_type": "AI-Automation",
            "current_agent": current_agent,
            "action_type": action_type,
            "next_agent": next_agent,
            "details": details or {}
        }
        if event_type:
            payload["event_type"] = event_type
        
        await websocket.send_json(payload)
    except Exception as e:
        print(f"Failed to emit progress bar update: {e}")


async def run_orchestrator_with_updates(
    declaration_id: str,
    risk_profiles: List[RiskProfile],
    websocket: WebSocket
) -> Dict[str, Any]:
    """
    Orchestrator with WebSocket real-time updates.
    
    Sends progress updates at each major stage:
    - Declaration fetching
    - Each risk processing (retrieve, execute, decide)
    - Final completion
    """
    
    final_output: Dict[str, Any] = {
        "declaration_id": declaration_id,
        "declaration_details": None,
        "results": []
    }

    # STEP 1: FETCH DECLARATION DETAILS
    await send_progress(
        websocket,
        stage="fetching_declaration",
        message=f"Fetching declaration details",
        data={"declaration_id": declaration_id, "stage": "fetching_declaration"}
    )
    
    try:
        declaration_details = fetch_declaration_details(declaration_id)
    except Exception as e:
        await send_progress(
            websocket,
            stage="error",
            message=f"Failed to fetch declaration details: {str(e)}"
        )
        return final_output

    if not declaration_details or not declaration_details.hs_code:
        await send_progress(
            websocket,
            stage="error",
            message="No HS Code found for this declaration ID"
        )
        return final_output

    filtered_details = filter_declaration_details(declaration_details)
    final_output["declaration_details"] = filtered_details
    # Declaration Received
    await send_progress(
        websocket,
        stage="declaration_received",
        message="Declaration successfully submitted and registered in CDM",
        data={
            "hs_code": declaration_details.hs_code,
            "goods_description": declaration_details.goods_description,
            "goods_value": declaration_details.goods_value,
            "status": "completed",
            "stage": "declaration_received"
        }
    )

    # # AI Risk Assessment Started
    # await send_progress(
    #     websocket,
    #     stage="ai_risk_assessment_started",
    #     message="AI Risk Assessment Started\nAI-Automation engine triggered for declaration",
    #     data={
    #         "declaration_id": declaration_id,
    #         "total_risks": len(risk_profiles),
    #         "status": "completed",
    #         "stage": "ai_risk_assessment_started"
    #     }
    # )

    #  CDM AI Evaluation in Progress
    await send_progress(
        websocket,
        stage="cdm_ai_evaluation",
        message="CDM AI Evaluation in Progress\nInitial risk assessment by CDM AI Agent",
        data={
            "declaration_id": declaration_id,
            "total_risks": len(risk_profiles),
            "status": "completed",
            "stage": "cdm_ai_evaluation"
        }
    )
    
    # STEP 2: PROCESS EACH RISK
    total_risks = len(risk_profiles)
    
    for index, risk_profile in enumerate(risk_profiles, start=1):
        # DOCUMENTATION GAP 
        if risk_profile.risk_type.upper() == "DOCUMENTATION_GAP":
            risk_start_time = time.time()

            await send_progress(
                websocket,
                stage="documentation_gap_detected",
                message=f"Documentation Gap detected for risk {risk_profile.risk_id}",
                data={
                    "risk_id": risk_profile.risk_id,
                    "risk_type": risk_profile.risk_type
                }
            )

            # Calculate response time
            risk_end_time = time.time()
            response_time_seconds = risk_end_time - risk_start_time
            response_time_formatted = f"{response_time_seconds:.2f} seconds"

            output_dict = {
                "cdm_decision": "SENT FOR CORRECTION",
                "cdm_feedback": risk_profile.risk_description,
                "tariff_feedback": {
                    "status": "Sent for correction",
                    "explanation": risk_profile.risk_description,
                    "failed_field": None,
                    "correct_value": None
                },
                "response_time": response_time_formatted
            }

            final_output["results"].append({
                "risk_id": risk_profile.risk_id,
                "output": output_dict
            })

            continue

        # EVENT: Risk Agent Processing - Determine agent based on risk type
        if risk_profile.risk_type.upper() == "TARIFF":
            risk_agent_name = "Tariff Verifier Agent"
        elif risk_profile.risk_type.upper() == "VALUATION":
            risk_agent_name = "Valuation Verifier Agent"
        elif risk_profile.risk_type.upper() == "INSPECTION":
            risk_agent_name = "Inspection Verifier Agent"
        else:
            risk_agent_name = "Unknown Verifier Agent"
        
        await emit_progress_bar_update(
            websocket,
            declaration_id=declaration_id,
            current_agent="CDM Decision Agent",
            action_type="Route Risk to Verifier",
            next_agent=risk_agent_name,
            event_type=f"Processing Risk {index}/{total_risks}",
            details={
                "risk_id": risk_profile.risk_id,
                "risk_type": risk_profile.risk_type,
                "risk_description": risk_profile.risk_description
            }
        )
        
        await send_progress(
            websocket,
            stage="processing_risk",
            message=f"Processing risk {index}/{total_risks}: {risk_profile.risk_id}",
            data={
                "risk_id": risk_profile.risk_id,
                "risk_type": risk_profile.risk_type,
                "current": index,
                "total": total_risks
            }
        )
        
        # Create CDM Input
        cdm_input = CDMInput(
            declaration_id=declaration_id,
            risk_profile=risk_profile
        )
        
        # Create Orchestrator State
        orch_state = OrchestratorAgentState(
            cdm_input=cdm_input,
            cdm_extracted=CDMExtracted(
                declaration_details=declaration_details
            ),
            cdm_decision=None
        )
        
        decision: CDMDecision | None = None
        risk_start_time = time.time()
        
        try:
            # RETRIEVE NODE
            # EVENT: Transfer to specific agent - Determine based on risk type
            if risk_profile.risk_type.upper() == "TARIFF":
                verifier_agent_name = "Tariff Verifier Agent"
            elif risk_profile.risk_type.upper() == "VALUATION":
                verifier_agent_name = "Valuation Verifier Agent"
            elif risk_profile.risk_type.upper() == "INSPECTION":
                verifier_agent_name = "Inspection Verifier Agent"
            else:
                verifier_agent_name = "Unknown Verifier Agent"
            
            await emit_progress_bar_update(
                websocket,
                declaration_id=declaration_id,
                current_agent=verifier_agent_name,
                action_type="Retrieve Reference Data",
                next_agent="CDM Executor Agent",
                event_type="Data Retrieval in Progress",
                details={
                    "risk_id": risk_profile.risk_id,
                    "hs_code": declaration_details.hs_code,
                    "risk_type": risk_profile.risk_type
                }
            )
            
            await send_progress(
                websocket,
                stage="retrieve",
                message=f"Fetching tariff and valuation data for risk {risk_profile.risk_id}",
                data={"risk_id": risk_profile.risk_id, "hs_code": declaration_details.hs_code}
            )
            
            # Give UI time to update
            await asyncio.sleep(0.1)
            
            # EXECUTE NODE
            # EVENT: Executor Agent
            await emit_progress_bar_update(
                websocket,
                declaration_id=declaration_id,
                current_agent="CDM Executor Agent",
                action_type="Execute Verification",
                next_agent="CDM Decision Agent",
                event_type="Running Verification Logic",
                details={
                    "risk_id": risk_profile.risk_id,
                    "risk_type": risk_profile.risk_type,
                    "verification_type": f"{risk_profile.risk_type} Compliance Check"
                }
            )
            
            await send_progress(
                websocket,
                stage="execute",
                message=f"Running {risk_profile.risk_type} verification for risk {risk_profile.risk_id}",
                data={"risk_id": risk_profile.risk_id, "risk_type": risk_profile.risk_type}
            )
            # Show specific progress based on risk type
            if risk_profile.risk_type.upper() == "TARIFF":
                #  Traffic Risk Analysis in Progress
                await send_progress(
                    websocket,
                    stage="tariff_risk_analysis_progress",
                    message="Tariff Risk Analysis in Progress\nDeclaration forwarded to Tariff Risk Agent",
                    data={
                        "risk_id": risk_profile.risk_id,
                        "risk_type": risk_profile.risk_type,
                        "hs_code": declaration_details.hs_code,
                        "status": "in_progress",
                        "stage": "tariff_risk_analysis_progress"
                    }
                )
            elif risk_profile.risk_type.upper() == "VALUATION":
                # Valuation Analysis in Progress
                await send_progress(
                    websocket,
                    stage="valuation_analysis_progress",
                    message="Valuation Analysis in Progress\nDeclaration forwarded to Valuation Agent",
                    data={
                        "risk_id": risk_profile.risk_id,
                        "risk_type": risk_profile.risk_type,
                        "goods_value": declaration_details.goods_value,
                        "status": "in_progress",
                        "stage": "valuation_analysis_progress"
                    }
                )
            elif risk_profile.risk_type.upper() == "INSPECTION":
                # Inspection Analysis in Progress
                await send_progress(
                    websocket,
                    stage="inspection_analysis_progress",
                    message="Inspection Analysis in Progress\nDeclaration forwarded to Inspection Verifier Agent",
                    data={
                        "risk_id": risk_profile.risk_id,
                        "risk_type": risk_profile.risk_type,
                        "hs_code": declaration_details.hs_code,
                        "goods_description": declaration_details.goods_description,
                        "status": "in_progress",
                        "stage": "inspection_analysis_progress"
                    }
                )
            
            await asyncio.sleep(0.1)
            
            # Run the actual workflow (synchronous, but we can wrap it)
            orch_state = await asyncio.to_thread(run_cdm_manager, orch_state)
            decision = orch_state.cdm_decision
            
            # Send completion result based on risk type
            if decision:
                if risk_profile.risk_type.upper() == "TARIFF":
                    # Traffic Risk Analysis Completed
                    await send_progress(
                        websocket,
                        stage="tariff_risk_analysis_completed",
                        message="Tariff Risk Analysis Completed\nTariff Agent response received",
                        data={
                            "risk_id": risk_profile.risk_id,
                            "risk_type": risk_profile.risk_type,
                            "decision": decision.cdm_decision,
                            "feedback": decision.cdm_feedback,
                            "status": "completed",
                            "stage": "tariff_risk_analysis_completed"
                        }
                    )
                elif risk_profile.risk_type.upper() == "VALUATION":
                    # Valuation Analysis Completed
                    await send_progress(
                        websocket,
                        stage="valuation_analysis_completed",
                        message="Valuation Analysis Completed\nValuation Agent response received",
                        data={
                            "risk_id": risk_profile.risk_id,
                            "risk_type": risk_profile.risk_type,
                            "decision": decision.cdm_decision,
                            "feedback": decision.cdm_feedback,
                            "status": "completed",
                            "stage": "valuation_analysis_completed"
                        }
                    )
                elif risk_profile.risk_type.upper() == "INSPECTION":
                    # Inspection Analysis Completed
                    await send_progress(
                        websocket,
                        stage="inspection_analysis_completed",
                        message="Inspection Analysis Completed\nInspection Verifier Agent response received",
                        data={
                            "risk_id": risk_profile.risk_id,
                            "risk_type": risk_profile.risk_type,
                            "decision": decision.cdm_decision,
                            "feedback": decision.cdm_feedback,
                            "status": "completed",
                            "stage": "inspection_analysis_completed"
                        }
                    )
            
        except Exception as e:
            await send_progress(
                websocket,
                stage="error",
                message=f"CDM failed for risk {risk_profile.risk_id}: {str(e)}",
                data={"risk_id": risk_profile.risk_id}
            )
        
        # Calculate response time
        risk_end_time = time.time()
        response_time_seconds = risk_end_time - risk_start_time
        response_time_formatted = f"{response_time_seconds:.2f} seconds"
        
        # Build output dict
        output_dict = {
            "cdm_decision": decision.cdm_decision if decision else None,
            "cdm_feedback": decision.cdm_feedback if decision else None,
        }
        
        # Include other fields only if they are not None
        if decision:
            if decision.tariff_feedback is not None:
                output_dict["tariff_feedback"] = decision.tariff_feedback.model_dump() if hasattr(decision.tariff_feedback, 'model_dump') else decision.tariff_feedback.dict()
            if decision.valuation_feedback is not None:
                output_dict["valuation_feedback"] = decision.valuation_feedback.model_dump() if hasattr(decision.valuation_feedback, 'model_dump') else decision.valuation_feedback.dict()
            if hasattr(decision, 'inspection_feedback') and decision.inspection_feedback is not None:
                output_dict["inspection_feedback"] = decision.inspection_feedback.model_dump() if hasattr(decision.inspection_feedback, 'model_dump') else decision.inspection_feedback.dict()
            if decision.failed_field is not None:
                output_dict["failed_field"] = decision.failed_field
            if decision.correct_value is not None:
                output_dict["correct_value"] = decision.correct_value
        
        # Add response time
        output_dict["response_time"] = response_time_formatted
        
        final_output["results"].append({
            "risk_id": risk_profile.risk_id,
            "output": output_dict
        })
        
        # Cleanup
        del orch_state
        del decision
    
    # STEP 3: COMPLETION
    #  AI Risk Consolidation
    await send_progress(
        websocket,
        stage="CDM_Agent_decision_consolidation",
        message="CDM Agent Decision Consolidation",
        data={
            "total_risks": total_risks,
            "results_count": len(final_output["results"]),
            "status": "completed",
            "stage": "ai_risk_consolidation"
        }
    )
    
    await asyncio.sleep(0.1)
    
    # AI Recommendation Generated
    await send_progress(
        websocket,
        stage="CDM_agent_decision",
        message="CDM Agent decision Generated\nRisk category and decision suggested",
        data={
            "declaration_id": declaration_id,
            "total_risks": total_risks,
            "results_count": len(final_output["results"]),
            "status": "completed",
            "stage": "CDM_agent_generated"
        }
    )
    
    return final_output


async def process_declaration_status_with_updates(
    cdm_payload: Dict[str, Any],
    websocket: WebSocket
) -> Dict[str, Any]:
    """
    Process declaration status with WebSocket real-time updates.
    
    Sends progress updates at each stage:
    - Parsing CDM results
    - Analyzing decisions
    - Calling AI for final status
    - Finalizing response
    """
    
    #  Awaiting Final Decision
    await send_progress(
        websocket,
        stage="awaiting_final_decision",
        message="Awaiting CDM Final Decision\nPending CDM Officer review",
        data={"status": "pending"}
    )
    
    # STEP 1: PARSE CDM PAYLOAD
    await send_progress(
        websocket,
        stage="parsing",
        message="Parsing CDM agent results",
        data={}
    )
    
    try:
        declaration_id = cdm_payload["result"]["declaration_id"]
        results = cdm_payload["result"]["results"]
    except KeyError as e:
        await send_progress(
            websocket,
            stage="error",
            message=f"Invalid payload structure: missing {str(e)}"
        )
        raise ValueError(f"Invalid payload structure: missing {str(e)}")
    
    await asyncio.sleep(0.1)
    
    # STEP 2: ANALYZE CDM DECISIONS
    await send_progress(
        websocket,
        stage="analyzing",
        message=f"Analyzing CDM decisions for {len(results)} risk(s)",
        data={
            "declaration_id": declaration_id,
            "total_risks": len(results)
        }
    )
    
    # Collect all CDM decisions
    cdm_decisions = []
    for item in results:
        decision = item.get("output", {}).get("cdm_decision")
        if decision:
            cdm_decisions.append(decision.upper())
    
    if not cdm_decisions:
        await send_progress(
            websocket,
            stage="error",
            message="No CDM decisions found in payload"
        )
        raise ValueError("No CDM decisions found in payload")
    
    await send_progress(
        websocket,
        stage="analyzing_complete",
        message=f"Collected {len(cdm_decisions)} CDM decision(s)",
        data={
            "cdm_decisions": cdm_decisions,
            "decision_summary": {
                "accepted": sum(1 for d in cdm_decisions if "ACCEPT" in d),
                "corrections": sum(1 for d in cdm_decisions if "CORRECTION" in d or "UNDER" in d or "OVER" in d),
                "rejected": sum(1 for d in cdm_decisions if "REJECT" in d or "DECLINED" in d),
                "review_needed": sum(1 for d in cdm_decisions if "REVIEW" in d)
            }
        }
    )
    
    await asyncio.sleep(0.2)
    
    # STEP 3: AI DECISION MAKING
    await send_progress(
        websocket,
        stage="deciding",
        message="Calling Agentic AI to determine final declaration status",
        data={
            "declaration_id": declaration_id,
            "ai_model": "LLM Decision Engine"
        }
    )
    
    try:
        # Run AI decision in thread (it's synchronous)
        final_decision = await asyncio.to_thread(ai_verify_and_decide, cdm_payload)
    except Exception as e:
        await send_progress(
            websocket,
            stage="error",
            message=f"AI decision failed: {str(e)}"
        )
        raise
    
    await asyncio.sleep(0.1)
    
    # STEP 4: FINALIZE RESPONSE
    await send_progress(
        websocket,
        stage="finalizing",
        message="Finalizing declaration status decision",
        data={
            "declaration_id": final_decision.get("declaration_id"),
            "declaration_status": final_decision.get("declaration_status"),
            "updated_by": final_decision.get("updated_by")
        }
    )
    
    await asyncio.sleep(0.1)
    
    # Final Decision Completed
    await send_progress(
        websocket,
        stage="CDM_final_decision_completed",
        message=" CDM final Decision Completed\nDeclaration validation completed",
        data={
            "declaration_id": final_decision.get("declaration_id"),
            "final_status": final_decision.get("declaration_status"),
            "reason": final_decision.get("status_reason"),
            "status": "completed"
        }
    )
    
    return final_decision
