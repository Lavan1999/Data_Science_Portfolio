from fastapi import FastAPI
from pydantic import BaseModel

from graph import workflow


app = FastAPI(
    title="Root Cause Analysis Agent",
    version="1.0.0"
)


class RCARequest(BaseModel):
    customer_id: str
    transaction_id: str


@app.get("/")
def home():
    return {
        "message": "Root Cause Analysis Agent is running."
    }


@app.post("/analyze")
def analyze(request: RCARequest):

    try:
        initial_state = {
            "customer_id": request.customer_id,
            "transaction_id": request.transaction_id,
            "db_result": None,
            "api_result": None,
            "log_result": None,
            "trace_id": None,
            "correlated_data": None,
            "analysis": None,
            "response": None
        }

        result = workflow.invoke(initial_state)

        return result["response"]

    except Exception as e:
        print("ERROR:", repr(e))
        raise e

# @app.post("/analyze")
# def analyze(request: RCARequest):

#     initial_state = {
#         "customer_id": request.customer_id,
#         "transaction_id": request.transaction_id,
#         "db_result": None,
#         "api_result": None,
#         "log_result": None,
#         "trace_id": None,
#         "correlated_data": None,
#         "analysis": None,
#         "response": None
#     }

#     result = workflow.invoke(initial_state)

#     return result["response"]