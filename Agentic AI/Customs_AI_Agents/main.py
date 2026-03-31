from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, List, Dict
import json
import asyncio
import logging
from config import MODEL_NAME, OLLAMA_URL
from declaration_status import ai_verify_and_decide
from src.memory.agentstate import RiskProfile
from websocket_orchestrator import run_orchestrator_with_updates, process_declaration_status_with_updates
from trade_advisor.models import RAGBasedTariffValuationRequest, RAGBasedTariffValuationResponse, ErrorResponse
from trade_advisor.trade_advisor_automation import automation_process

# Setup logging for trade advisor
logger = logging.getLogger(__name__)

app = FastAPI(title="CDM Orchestrator API with WebSocket")


# Pydantic Models
class RiskProfileRequest(BaseModel):
    risk_id: str
    risk_type: str
    risk_description: str
    risk_confidence_score: str
    risk_recommended_action: str

class RunCDMRequest(BaseModel):
    declaration_id: str
    risk_profiles: List[RiskProfileRequest]

class DeclarationStatusPayload(BaseModel):
    status: str
    result: Dict[str, Any]

# WEBSOCKET: CDM AGENT

@app.websocket("/ws/cdm_agent")
async def websocket_cdm_agent(websocket: WebSocket):

    await websocket.accept()

    try:
        data = await websocket.receive_text()
        request_data = json.loads(data)
        #Validate requst structure
        if "declaration_id" not in request_data or "risk_profiles" not in request_data:
            await websocket.send_json({
                "type": "error",
                "message": "Invalid request format. Required: declaration_id and risk_profiles"
            })
            await websocket.close()
            return
        
        # Convert to internal models and normalize risk_type
        declaration_id = request_data["declaration_id"]
        risk_profiles = []
        for r in request_data["risk_profiles"]:
            risk_type_raw = r["risk_type"].strip().lower()
            if risk_type_raw in ["TARIFF","tariff", "tariff misclassification", "Tariff Misclassification", "origin based risk", "Origin Based Risk", "origin_based_risk", "origin risk", "Origin Risk", "Origin-Based Risk", "origin based", "Origin based", "origin_based", "origin-based"]:
                normalized_risk_type = "TARIFF"
            elif risk_type_raw in ["VALUATION", "valuation", "valuation risk", "valuationrisk", "Valuation Risk"]:
                normalized_risk_type = "VALUATION"
            elif risk_type_raw in ["documentation gap", "documentation_gap", "Documentation Gap", "Documentation_Gap"]:
                normalized_risk_type = "DOCUMENTATION_GAP"
            else:
                normalized_risk_type = r["risk_type"]
            risk_profiles.append(RiskProfile(
                risk_id=r["risk_id"],
                risk_type=normalized_risk_type,
                risk_description=r["risk_description"],
                risk_confidence_score=r["risk_confidence_score"],
                risk_recommended_action=r["risk_recommended_action"]
            ))
        
        # Send acknowledgment
        await websocket.send_json({
            "type": "started",
            "message": f"Processing {len(risk_profiles)} risks for declaration",
            "total_risks": len(risk_profiles)
        })

        
        # Run orchestrator with WebSocket updates
        output = await run_orchestrator_with_updates(
            declaration_id=declaration_id,
            risk_profiles=risk_profiles,
            websocket=websocket
        )

        await websocket.send_json({
            "type": "complete",
            "status": "success",
            "result": output
        })

    except WebSocketDisconnect:
        print("Client disconnected")

    except json.JSONDecodeError:
        await websocket.send_json({
            "type": "error",
            "message": "Invalid JSON format"
        })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Processing failed: {str(e)}"
        })

    finally:
        await websocket.close()

# WEBSOCKET: DECLARATION STATUS

@app.websocket("/ws/declaration_status")
async def websocket_declaration_status(websocket: WebSocket):

    await websocket.accept()


    try:
        data = await websocket.receive_text()
        request_data = json.loads(data)

        if "status" not in request_data or "result" not in request_data:
            await websocket.send_json({
                "type": "error",
                "message": "Invalid request format. Required: status and result"
            })
            await websocket.close()
            return

        if "declaration_id" not in request_data["result"]:
            await websocket.send_json({
                "type": "error",
                "message": "Invalid result format. Required: declaration_id in result"
            })
            await websocket.close()
            return

        declaration_id = request_data["result"]["declaration_id"]

        await websocket.send_json({
            "type": "started",
            "message": f"Processing declaration status for {declaration_id}",
            "declaration_id": declaration_id
        })

        final_decision = await process_declaration_status_with_updates(
            cdm_payload=request_data,
            websocket=websocket
        )

        await websocket.send_json({
            "type": "complete",
            "status": "success",
            "result": final_decision
        })

    except WebSocketDisconnect:
        print("Client disconnected")

    except json.JSONDecodeError:
        await websocket.send_json({
            "type": "error",
            "message": "Invalid JSON format"
        })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Processing failed: {str(e)}"
        })

    finally:
        await websocket.close()


# HTTP: CDM AGENT

@app.post("/cdm_agent")
def run_cdm_api(request: RunCDMRequest):

    try:
        risk_profiles = [
            RiskProfile(
                risk_id=r.risk_id,
                risk_type=r.risk_type,
                risk_description=r.risk_description,
                risk_confidence_score=r.risk_confidence_score,
                risk_recommended_action=r.risk_recommended_action
            )
            for r in request.risk_profiles
        ]

        from agent_automation import run_orchestrator

        output = run_orchestrator(
            declaration_id=request.declaration_id,
            risk_profiles=risk_profiles
        )

        return {"status": "success", "result": output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HTTP: DECLARATION STATUS

@app.post("/declaration_status")
def declaration_status(payload: DeclarationStatusPayload):


    try:
        final_decision = ai_verify_and_decide(payload.dict())

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(final_decision)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agentic AI decision failed: {str(e)}"
        )

# HTTP: TARIFF & VALUATION VERIFICATION

@app.post("/agent_tariff_valuation", response_model=RAGBasedTariffValuationResponse, responses={500: {"model": ErrorResponse}})
async def verify_tariff_valuation_rag(request: RAGBasedTariffValuationRequest):
    """
    Verify tariff and valuation using RAG-sourced reference data.
    Returns results in the standardized output format.
    """
    try:
        logger.info(f"Processing RAG-based declaration: {request.declaration_id}")
        results = []
        all_issues = []

        for idx, item in enumerate(request.items):
            logger.info(f"Processing item {idx}: {item.description}")
            result, issues = automation_process(
                item=item,
                rag_data=request.context.rag_data,
                declaration_type=request.declaration_type,
                idx=idx,
            )
            results.append(result)
            all_issues.extend(issues)

        # Build summary
        if all_issues:
            short_issues = "; ".join(i.split(" - ")[0] for i in all_issues)
            summary = f"{len(all_issues)} issue(s) found: {short_issues}"
        else:
            summary = "HS matches and valuation is valid"

        logger.info(f"Declaration {request.declaration_id} complete. Summary: {summary}")
        return RAGBasedTariffValuationResponse(results=results, summary=summary)

    except Exception as e:
        logger.error(f"RAG verification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"error": f"Agent unavailable or timeout: {str(e)}"})

# RUN SERVER

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# To run the API, use the command:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000