from dotenv import load_dotenv
import os

load_dotenv()

# Tariff DB
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Ollama / LLM
OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
API_KEY = os.getenv("API_KEY")
# Tariff API
TARIFF_URL = os.getenv("TARIFF_URL")
TARIFF_TOKEN = os.getenv("TARIFF_TOKEN")

# Valuation API
VALUATION_URL = os.getenv("VALUATION_URL")
VALUATION_TOKEN = os.getenv("VALUATION_TOKEN")

# Declaration GraphQL API
GRAPHQL_URL = os.getenv("GRAPHQL_URL")

