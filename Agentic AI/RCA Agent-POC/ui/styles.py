import streamlit as st

def load_css():

    st.markdown(
        """
        <style>

        .main{
            padding-top:1rem;
        }

        .title{
            font-size:40px;
            font-weight:bold;
            color:#1565C0;
        }

        .section-title{
            font-size:24px;
            font-weight:600;
            margin-top:20px;
        }

        .metric-card{
            border-radius:12px;
            padding:20px;
            border:1px solid #ddd;
        }

        </style>
        """,
        unsafe_allow_html=True
    )