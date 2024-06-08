import numpy as np
import pandas as pd
import streamlit as st
from joblib import load

st.set_page_config(layout="wide")

st.title(" :red[Store Sales Forecasting Model]")
# Define dictionaries for mapping strings to integers
type_dict = {'A': 0, 'B': 1, 'C': 2}
isholiday_dict = {True: 1, False: 0}
# custom style for prediction result text - color and position
type_values = ['A','B','C']

store_values = [ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17,
       18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
       35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]

isholiday_values = [True,False]
st.write(' :white[Fill the below details to find Predict weekly sales]')
with st.form('Salesforecast'):

        col1,col2,col3 = st.columns([0.5,0.1,0.5])
        with col1:

            type = st.selectbox(label='Type of store(1-45)', options=type_values)
            store = st.selectbox(label='Store Number', options=store_values)
            department= st.number_input(label='Department (1-99)' ,min_value= 1, max_value= 99)
            temperature = st.number_input(label='Temperature (Example range: 1-100)', min_value=-7.29, max_value=101.95)
            year = st.number_input(label='Year', min_value=2000, max_value=2050)
            
        with col3:  
            cpi = st.number_input(label='CPI(Consumer Price Index)', min_value= 126.064 , max_value=228.976)
            isholiday = st.selectbox(label='IsHoliday', options=isholiday_values)
            unemployment = st.number_input(label='Unemployment rate', min_value=3.684, max_value=14.313)
            size = st.number_input(label='Size of store', min_value=34875.0	, max_value=219622.0)
            st.write('')
            st.write('')
            button = st.form_submit_button(label='SUBMIT')
            
col1,col2 = st.columns([0.65,0.35])
with col2:
    st.caption(body='*Min and Max values are reference only')
    
# Process user input and make predictions
# Adjusted form submission check
if button:
    
# Convert user inputs to the appropriate format
    type_int = type_dict.get(type)
    isholiday_int = isholiday_dict.get(isholiday)
    
    # Combine inputs into a NumPy array
    input_data = np.array([[store, temperature, cpi, unemployment, isholiday_int, department, type_int, size, year]])
    
    # Load the saved model
    file_path = 'resale_regression_model.pkl'  # Adjust the file path as per your saved model
    loaded_model = load(file_path)
    
    # Make predictions
    y_pred = loaded_model.predict(input_data)
    predicted_sales = y_pred[0]
    
    # Display the prediction
    st.header(f'Predicted Weekly Sales: {predicted_sales:.2f}')