import numpy as np
import pandas as pd
import streamlit as st
import pickle
from joblib import load

# Load the dataset
df = pd.read_csv(r'C:\Users\DELL\Desktop\Project6-Singapore\singapore_encoded.csv')

st.set_page_config(layout="wide")
st.title(' :blue[Singapore Housing Resale Value Estimator]')


# Load the encoder from the pickle file
with open(r"C:\Users\DELL\Desktop\Project6-Singapore\town1_encoder.pkl", "rb") as town_pickle_file:
    town_encoder = pickle.load(town_pickle_file)
with open(r"C:\Users\DELL\Desktop\Project6-Singapore\block1_encoder.pkl", "rb") as block_pickle_file:
    block_encoder = pickle.load(block_pickle_file)
with open(r"C:\Users\DELL\Desktop\Project6-Singapore\flat_type1_encoder.pkl", "rb") as flattype_pickle_file:
    flattype_encoder = pickle.load(flattype_pickle_file)    
with open(r"C:\Users\DELL\Desktop\Project6-Singapore\flat_model1_encoder.pkl", "rb") as flatmodel_pickle_file:
    flatmodel_encoder = pickle.load(flatmodel_pickle_file)
with open(r"C:\Users\DELL\Desktop\Project6-Singapore\storey_range1_encoder.pkl", "rb") as storeyrange_pickle_file:
    storeyrange_encoder = pickle.load(storeyrange_pickle_file)
with open(r"C:\Users\DELL\Desktop\Project6-Singapore\street_name1_encoder.pkl", "rb") as streetName_pickle_file:
    streetName_encoder = pickle.load(streetName_pickle_file)
    

# Decode the encoded town names
encoded_block = df['block'].unique()  # Get the encoded town values from the DataFrame
encoded_towns = df['town'].unique()
encoded_flattype= df['flat_type'].unique()
encoded_flatmodel= df['flat_model'].unique()
encoded_storeyrange= df['storey_range'].unique()
encoded_streetName= df['street_name'].unique()


# Get the encoded town values from the DataFrame
decoded_towns = town_encoder.inverse_transform(encoded_towns)
decoded_block = block_encoder.inverse_transform(encoded_block)  # Decode the town names
decoded_flattype = flattype_encoder.inverse_transform(encoded_flattype)
decoded_flatmodel = flatmodel_encoder.inverse_transform(encoded_flatmodel)
decoded_storeyrange = storeyrange_encoder.inverse_transform(encoded_storeyrange)
decoded_streetName = streetName_encoder.inverse_transform(encoded_streetName)


# Get unique town names for the selectbox options
unique_decoded_towns = np.unique(decoded_towns)
unique_decoded_block = np.unique(decoded_block)
unique_decoded_flattype = np.unique(decoded_flattype)
unique_decoded_flatmodel = np.unique(decoded_flatmodel)
unique_decoded_storeyrange = np.unique(decoded_storeyrange)
unique_decoded_streetName = np.unique(decoded_streetName)


st.write(' :white[Fill the below details to find Predict Resale Price]')

# Get input from users
with st.form('Regression'):
    col1, col2, col3 = st.columns([0.5, 0.1, 0.5])

    with col1:
        # Create a selectbox with decoded town names
        selected_town = st.selectbox("Select a Town:", unique_decoded_towns)
        selected_block = st.selectbox("Select Block:", unique_decoded_block)
        selected_model = st.selectbox("Select a Flat Model:", unique_decoded_flatmodel)
        month = st.number_input(label='Month', min_value=1 , max_value=12)
        floor_area_sqm = st.number_input(label='Select floor area sqm', min_value=28.0 , max_value=307.0)
        
    with col3:
        selected_type = st.selectbox("Select Flat Type:", unique_decoded_flattype)
        selected_storey = st.selectbox("Select Storey Range:", unique_decoded_storeyrange)
        selected_street = st.selectbox("Select Street Name:", unique_decoded_streetName)
        lease_commence_date = st.number_input(label='lease commence year', min_value=1966, max_value=2022)
        year = st.number_input(label='year', min_value=1990, max_value=2024)
        st.write('')
        button = st.form_submit_button(label='SUBMIT')

    col1, col2 = st.columns([0.65, 0.35])
    with col2:
        st.caption(body='*Min and Max values are reference only')
        
        
#Process user input and make predictions
if button:
    # Encode the selected values
    encoded_selected_town = town_encoder.transform([selected_town])[0]
    encoded_selected_block = block_encoder.transform([selected_block])[0]
    encoded_selected_model = flatmodel_encoder.transform([selected_model])[0]
    encoded_selected_type = flattype_encoder.transform([selected_type])[0]
    encoded_selected_storey = storeyrange_encoder.transform([selected_storey])[0]
    encoded_selected_street = streetName_encoder.transform([selected_street])[0]
    
    # Make predictions 
    input_array = np.array([[month, encoded_selected_town, encoded_selected_type, encoded_selected_block, 
                             encoded_selected_street, encoded_selected_storey, floor_area_sqm, 
                             encoded_selected_model, lease_commence_date, year]])
    

     # Load the saved model
    file_path = r'C:\Users\DELL\Desktop\Project6-Singapore\singapore_regression_model.pkl'  # Adjust the file path as per your saved model
    loaded_model = load(file_path)
    
    # Make predictions
    y_pred = loaded_model.predict(input_array)
    predicted_resale = y_pred[0]
    
    # Display the prediction
    st.header(f'Predicted Resale Price is: {predicted_resale}')       
        
    
        
        
        
        
        