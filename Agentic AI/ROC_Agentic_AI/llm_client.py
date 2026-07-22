from openai import OpenAI
from config import LLM_API_KEY,LLM_BASE_URL

client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL
)

print("LLM BASE URL:", LLM_BASE_URL)
print("LLM API KEY:", LLM_API_KEY[:5] if LLM_API_KEY else None)