# 🚀 Root Cause Analysis (RCA) Agent

An Agentic AI solution that automates transaction failure investigation by retrieving data from multiple sources, correlating transaction events, identifying failures, and generating a structured Root Cause Analysis (RCA) using Llama 4 Scout.

---

# 🚀 Getting Started

## Prerequisites

Before running the project, ensure the following software is installed:

- Python 3.11 or later
- Git
- SQLite
- Visual Studio Code (Recommended)

---

## Clone the Repository

```bash
git clone https://github.com/<your-username>/Sphere-Agentic-AI.git

cd Sphere-Agentic-AI
```

---

## Create a Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file in the project root.

```env
LLM_API_KEY=YOUR_API_KEY
LLM_BASE_URL=YOUR_LLM_BASE_URL
LLM_MODEL=YOUR_MODEL_NAME
MOCK_API_URL=http://127.0.0.1:8001
```

---

## Initialize the Database

```bash
python database/init_db.py
```

Expected Output

```text
Customers Loaded    : 100
Transactions Loaded : 100
Database Created    : database/db.sqlite
```

---

## Generate Application Logs

```bash
python logs/generate_logs.py
```

Expected Output

```text
500 Logs Created Successfully
```

---

## Generate Mock API Data

```bash
python mock_api/generate_mock_data.py
```

Expected Output

```text
Generated 100 API records.
```

---

## Start the Mock Payment Gateway API

```bash
uvicorn mock_api.mock_server:app --reload --port 8001
```

Verify by opening:

http://127.0.0.1:8001

Expected Response

```json
{
    "message": "Mock Payment Gateway API is running."
}
```

---

## Start the FastAPI Backend

```bash
uvicorn main:app --reload
```

Swagger Documentation

http://127.0.0.1:8000/docs

---

## Start the Streamlit Dashboard

Open another terminal and run:

```bash
streamlit run ui/streamlit_app.py
```

Streamlit Dashboard

http://localhost:8501

---

# 🧪 API Testing

### Endpoint

`POST /analyze`

### Sample Request

```json
{
    "customer_id": "CUST050",
    "transaction_id": "TXN1050"
}
```

---

# 📷 Application Screenshots

## Streamlit Dashboard

<img width="1891" height="1005" alt="image" src="https://github.com/user-attachments/assets/4ce2c977-f0bc-4336-8b8d-c5a126a29585" />

---

## Root Cause Analysis Result

<img width="945" height="539" alt="image" src="https://github.com/user-attachments/assets/4964335e-3c23-46a5-995b-576265452bd1" />

---

## Postman API Testing

<img width="620" height="439" alt="image" src="https://github.com/user-attachments/assets/e10c39ae-bead-465a-8a3e-2e387b1a9842" />

---

# 📄 Sample Response

```json
{
    "customerId": "CUST050",
    "transactionId": "TXN1050",
    "rootCause": "Gateway Timeout",
    "failureFlow": [
        "Customer request received by CustomerService",
        "Order validation completed by OrderService",
        "Payment processing started by PaymentService",
        "PaymentGateway returned HTTP 504 Gateway Timeout",
        "Transaction marked as FAILED by PaymentService"
    ],
    "evidence": [
        "Gateway returned HTTP 504 status code",
        "Gateway error code: GW_TIMEOUT_504",
        "Gateway error message: Gateway Timeout",
        "High latency of 6748ms",
        "3 retries attempted by PaymentGateway"
    ],
    "recommendation": [
        "Implement retry mechanism with exponential backoff for PaymentGateway",
        "Monitor PaymentGateway latency and timeouts",
        "Consider implementing circuit breaker pattern for PaymentGateway",
        "Review and optimize PaymentGateway configuration"
    ]
}
```







