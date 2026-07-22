import json
from pathlib import Path
from llm_client import client
from config import LLM_MODEL
from state import RCAState


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = BASE_DIR / "prompts" / "analysis_prompt.txt"


def analysis_agent(state: RCAState) -> RCAState:


    print("===== ANALYSIS AGENT INPUT =====")
    print(state)
    print("==========================")
    with open(PROMPT_FILE, "r", encoding="utf-8") as file:
        system_prompt = file.read()

    correlated_json = json.dumps(
        state["correlated_data"],
        indent=4
    )

    user_prompt = f"""
Analyze the following transaction.

Transaction Data:

{correlated_json}
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

    print("====== LLM OUTPUT ======")
    print(content)
    print("=========================")

    try:
        start = content.find("{")
        end = content.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("No JSON object found in LLM response.")

        json_content = content[start:end]
        analysis = json.loads(json_content)

    except Exception as e:
        print("JSON Parsing Error:", e)

        analysis = {
            "rootCause": "",
            "failureFlow": [],
            "evidence": [],
            "recommendation": [],
            "raw_response": content
        }

    state["analysis"] = analysis
    print("===== ANALYSIS AGENT OUTPUT =====")
    print(state)
    print("=================================")

    return state

    # content = response.choices[0].message.content

    # print("====== LLM OUTPUT ======")
    # print(content)
    # print("=========================")

    # try:
    #     # Extract JSON if model adds explanation
    #     start = content.find("{")
    #     end = content.rfind("}") + 1

    #     json_content = content[start:end]

    #     analysis = json.loads(json_content)

    # except Exception as e:
    #     print("JSON Parsing Error:", e)

    #     analysis = {
    #         "rootCause": "",
    #         "failureFlow": [],
    #         "evidence": [],
    #         "recommendation": [],
    #         "raw_response": content
    #     }

    # state["analysis"] = analysis

    # return state