from fastapi import FastAPI, HTTPException, requests
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, List, Dict
from config import MODEL_NAME, OLLAMA_URL
from declaration_status import ai_verify_and_decide
from src.memory.agentstate import RiskProfile
from agent_automation import run_orchestrator
app = FastAPI(title="CDM Orchestrator API")

# Pydantic Models for API
class RiskProfileRequest(BaseModel):
    risk_id: str
    risk_type: str
    risk_description: str
    risk_confidence_score: str
    risk_recommended_action: str

class RunCDMRequest(BaseModel):
    declaration_id: str
    risk_profiles: List[RiskProfileRequest]

# API Route
@app.post("/cdm_agent")
def run_cdm_api(request: RunCDMRequest):
    try:
        # Convert RiskProfileRequest → RiskProfile
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

        # Run orchestrator
        output = run_orchestrator(
            declaration_id=request.declaration_id,
            risk_profiles=risk_profiles
        )

        return {"status": "success", "result": output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Declaration status endpoint
class DeclarationStatusPayload(BaseModel):
    status: str
    result: Dict[str, Any]


@app.post("/declaration_status")
def declaration_status(payload: DeclarationStatusPayload):
    try:
        final_decision = ai_verify_and_decide(payload.dict())

        # Return ONLY the AI output
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(final_decision)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agentic AI decision failed: {str(e)}"
        )

# # To run the API, use the command:
# # uvicorn main:app --reload --host 0.0.0.0 --port 8000


