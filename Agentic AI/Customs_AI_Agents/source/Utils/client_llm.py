from config import OLLAMA_URL, MODEL_NAME, API_KEY
import requests


# def llm(prompt: str) -> str:
#     response = requests.post(
#         OLLAMA_URL,
#         json={
#             "model": MODEL_NAME,
#             "prompt": prompt,
#             "stream": False
#         },
#         timeout=120
#     )
#     response.raise_for_status()
#     return response.json().get("response", "")




def llm(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        },
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a rule-based decision engine. "
                        "You MUST return ONLY raw JSON. "
                        "No function calls. No tools. No explanations. "
                        "If output is not JSON, it is invalid."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0,
            "max_tokens": 300
        },
        timeout=120
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
    