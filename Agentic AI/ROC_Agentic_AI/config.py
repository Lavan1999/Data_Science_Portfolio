import os

from dotenv import load_dotenv


load_dotenv()


LLM_API_KEY = os.getenv("API_KEY")

LLM_BASE_URL = os.getenv("OLLAMA_URL")

LLM_MODEL = os.getenv("MODEL_NAME")

MOCK_API_URL = os.getenv("MOCK_API_URL")