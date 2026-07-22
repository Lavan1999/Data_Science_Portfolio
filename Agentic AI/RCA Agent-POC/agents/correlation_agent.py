import json
from pathlib import Path

from llm_client import client
from config import LLM_MODEL
from state import RCAState

from tools.database_tool import database_tool
from tools.api_tool import api_tool
from tools.log_tool import log_tool


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = BASE_DIR / "prompts" / "rca_prompt.txt"


def correlation_agent(state: RCAState) -> RCAState:

    print("===== CORRELATION AGENT INPUT =====")
    print(state)
    print("===================================")

    # Execute Tools
    state = database_tool(state)
    state = api_tool(state)
    state = log_tool(state)

    db_result = state["db_result"]
    api_result = state["api_result"]
    log_result = state["log_result"]

    with open(PROMPT_FILE, "r", encoding="utf-8") as file:
        system_prompt = file.read()

    user_prompt = f"""
Correlate the following information.

Database Result:

{json.dumps(db_result, indent=4)}

API Result:

{json.dumps(api_result, indent=4)}

Application Logs:

{json.dumps(log_result, indent=4)}
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    content = response.choices[0].message.content

    print("===== CORRELATION LLM OUTPUT =====")
    print(content)
    print("==================================")

    try:

        start = content.find("{")
        end = content.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("No JSON object found.")

        json_content = content[start:end]

        correlated_data = json.loads(json_content)

    except Exception as e:

        print("JSON Parsing Error:", e)

        correlated_data = {
            "customer": db_result,
            "transaction": db_result,
            "gateway": api_result,
            "logs": log_result
        }

    state["correlated_data"] = correlated_data

    print("===== CORRELATION AGENT OUTPUT =====")
    print(state)
    print("====================================")

    return state
#-------
# from state import RCAState
# from tools.database_tool import database_tool
# from tools.api_tool import api_tool
# from tools.log_tool import log_tool

# def correlation_agent(state: RCAState) -> RCAState:

#     print("INITIAL STATE")
#     print(state)

#     state = database_tool(state)
#     print("\nAFTER DATABASE TOOL")
#     print(state)

#     state = api_tool(state)
#     print("\nAFTER API TOOL")
#     print(state)

#     state = log_tool(state)
#     print("\nAFTER LOG TOOL")
#     print(state)

#     db_result = state["db_result"]
#     api_result = state["api_result"]
#     log_result = state["log_result"]

#     correlated_data = {
#         "customer": {
#             "customerId": db_result["customerId"],
#             "customerName": db_result["customerName"],
#             "email": db_result["email"],
#             "phone": db_result["phone"]
#         },
#         "transaction": {
#             "transactionId": db_result["transactionId"],
#             "traceId": db_result["traceId"],
#             "amount": db_result["amount"],
#             "status": db_result["status"],
#             "failureScenario": db_result["failureScenario"],
#             "timestamp": db_result["timestamp"]
#         },
#         "gateway": api_result,
#         "logs": log_result
#     }

#     state["correlated_data"] = correlated_data

#     print("\nFINAL STATE")
#     print(state)

#     return state
#------------

# from pathlib import Path
# import json

# from llm_client import client
# from config import LLM_MODEL
# from state import RCAState
# print("CORRELATION AGENT FILE:", __file__)
# BASE_DIR = Path(__file__).resolve().parent.parent
# PROMPT_FILE = BASE_DIR / "prompts" / "rca_prompt.txt"


# def correlation_agent(state: RCAState):

#     with open(PROMPT_FILE, "r", encoding="utf-8") as f:
#         system_prompt = f.read()

#     user_prompt = f"""
# Database Result:
# {json.dumps(state["db_result"], indent=4)}

# API Result:
# {json.dumps(state["api_result"], indent=4)}

# Log Result:
# {json.dumps(state["log_result"], indent=4)}
# """

#     response = client.chat.completions.create(
#         model=LLM_MODEL,
#         temperature=0,
#         response_format={"type": "json_object"},
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt},
#         ]
#     )

#     state["correlated_data"] = json.loads(
#         response.choices[0].message.content
#     )
#     print("===== CORRELATION AGENT OUTPUT =====")
#     print(state)
#     print("=============================")

#     return state


# from state import RCAState
# from tools.database_tool import database_tool
# from tools.api_tool import api_tool
# from tools.log_tool import log_tool



# def correlation_agent(state: RCAState) -> RCAState:

#     state = database_tool(state)

#     state = api_tool(state)

#     state = log_tool(state)

#     db_result = state["db_result"]
#     api_result = state["api_result"]
#     log_result = state["log_result"]

#     if db_result["traceId"] != api_result["traceId"]:
#         raise ValueError("Trace ID mismatch between Database and API.")

#     correlated_data = {
#         "customer": {
#             "customerId": db_result["customerId"],
#             "customerName": db_result["customerName"],
#             "email": db_result["email"],
#             "phone": db_result["phone"]
#         },
#         "transaction": {
#             "transactionId": db_result["transactionId"],
#             "traceId": db_result["traceId"],
#             "amount": db_result["amount"],
#             "status": db_result["status"],
#             "failureScenario": db_result["failureScenario"],
#             "timestamp": db_result["timestamp"]
#         },
#         "paymentGateway": api_result,
#         "logs": log_result
#     }

#     state["correlated_data"] = correlated_data

#     return state

# # def correlation_agent(state: RCAState) -> RCAState:

# #     db_result = state["db_result"]
# #     api_result = state["api_result"]
# #     log_result = state["log_result"]

# #     if db_result["traceId"] != api_result["traceId"]:
# #         raise ValueError("Trace ID mismatch between Database and API.")

# #     correlated_data = {
# #         "customer": {
# #             "customerId": db_result["customerId"],
# #             "customerName": db_result["customerName"],
# #             "email": db_result["email"],
# #             "phone": db_result["phone"]
# #         },
# #         "transaction": {
# #             "transactionId": db_result["transactionId"],
# #             "traceId": db_result["traceId"],
# #             "amount": db_result["amount"],
# #             "status": db_result["status"],
# #             "failureScenario": db_result["failureScenario"],
# #             "timestamp": db_result["timestamp"]
# #         },
# #         "paymentGateway": api_result,
# #         "logs": log_result
# #     }

# #     state["correlated_data"] = correlated_data

# #     return state