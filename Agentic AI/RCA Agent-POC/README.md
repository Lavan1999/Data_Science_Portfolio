🚀 Getting Started
Prerequisites

Before running the project, ensure the following software is installed:

Python 3.11 or above
Git
SQLite
Visual Studio Code (Recommended)
Clone the Repository

Clone the repository and navigate to the project directory.

git clone https://github.com/<your-github-username>/Sphere-Agentic-AI.git

cd Sphere-Agentic-AI

Create a Virtual Environment

Windows

python -m venv venv

venv\Scripts\activate

Linux / macOS

python3 -m venv venv

source venv/bin/activate

Install Dependencies

pip install -r requirements.txt

Configure Environment Variables

Create a .env file in the project root and add the following values:

LLM_API_KEY=YOUR_API_KEY

LLM_BASE_URL=YOUR_LLM_BASE_URL

LLM_MODEL=YOUR_MODEL_NAME

Example:

LLM_API_KEY=abc123

LLM_BASE_URL=http://localhost:8000/v1

LLM_MODEL=llama-4-scout

Initialize the Database

Run the database initialization script.

python database/init_db.py

Expected Output

Customers Loaded : 100
Transactions Loaded : 100
Database Created : database/db.sqlite
Generate Application Logs

Run the log generation script.

python logs/generate_logs.py

Expected Output

500 Logs Created Successfully
Generate Mock API Data

Run the mock API data generation script.

python mock_api/generate_mock_data.py

Expected Output

Generated 100 API records.
Start the Mock Payment Gateway API

Run the mock API server.

uvicorn mock_api.mock_server:app --reload --port 8001

Verify the API by opening:

http://127.0.0.1:8001

Expected Response

{
"message": "Mock Payment Gateway API is running."
}

Start the FastAPI Backend

Run the FastAPI application.

uvicorn main:app --reload

Swagger API Documentation will be available at:

http://127.0.0.1:8000/docs

Start the Streamlit Application

Open a new terminal and run:

streamlit run ui/streamlit_app.py

The Streamlit dashboard will be available at:

http://localhost:8501

API Testing

Endpoint

POST /analyze

Request Body

{
"customer_id": "CUST050",
"transaction_id": "TXN1050"
}

<img width="1891" height="1005" alt="image" src="https://github.com/user-attachments/assets/4ce2c977-f0bc-4336-8b8d-c5a126a29585" />

<img width="945" height="539" alt="image" src="https://github.com/user-attachments/assets/4964335e-3c23-46a5-995b-576265452bd1" />


<img width="620" height="439" alt="image" src="https://github.com/user-attachments/assets/e10c39ae-bead-465a-8a3e-2e387b1a9842" />
