import requests
import streamlit as st
from styles import load_css

API_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(
    page_title="Root Cause Analysis Agent",
    page_icon="🤖",
    layout="wide"
)
load_css()

st.title("🤖 Root Cause Analysis (RCA) Agent")
st.markdown("Analyze customer transactions using an Agentic AI workflow.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    customer_id = st.text_input(
        "Customer ID",
        placeholder="CUST050"
    )

with col2:
    transaction_id = st.text_input(
        "Transaction ID",
        placeholder="TXN1050"
    )

if st.button("Analyze Transaction", use_container_width=True):

    if not customer_id or not transaction_id:
        st.warning("Please enter both Customer ID and Transaction ID.")

    else:

        payload = {
            "customer_id": customer_id,
            "transaction_id": transaction_id
        }

        with st.spinner("Running Agentic AI Workflow..."):

            try:

                response = requests.post(
                    API_URL,
                    json=payload,
                    timeout=120
                )

                if response.status_code == 200:

                    result = response.json()

                    st.success("Analysis Completed Successfully")

                    st.divider()

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Customer ID",
                            result["customerId"]
                        )

                    with col2:
                        st.metric(
                            "Transaction ID",
                            result["transactionId"]
                        )

                    st.subheader("🚨 Root Cause")

                    st.error(result["rootCause"])

                    st.subheader("🔄 Failure Flow")

                    for step in result["failureFlow"]:
                        st.write(f"• {step}")

                    st.subheader("📄 Evidence")

                    for item in result["evidence"]:
                        st.info(item)

                    st.subheader("💡 Recommendation")

                    for item in result["recommendation"]:
                        st.success(item)

                    st.divider()

                    with st.expander("Raw JSON Response"):

                        st.json(result)

                else:

                    st.error(response.text)

            except Exception as e:

                st.error(str(e))