import pandas as pd 
import pymongo
import seaborn as sns 
import matplotlib.pyplot as plt 
import plotly.express as px 
import streamlit as st
import plotly.graph_objects as go
from streamlit_option_menu import option_menu


def data():
    clm = {'name': [], 'country': [], 'property_type': [], 'price': [], 'room_type': [],
           'bedrooms': [], 'beds': [],'accommodates':[],'cancellation_policy': [],'number_of_reviews': [],
           'minimum_nights': [], 'extra_people':[],'maximum_nights': [],'guests_include': [],'review_scores_cleanliness': [],
           'last_scraped': [], 'host_name':[], 'host_listings_count':[],'calendar_last_scraped': [], 
           'availability_365': [],'latitude': [], 'longitude': []}

    for i in col.find():
        # connection to mongodb
        client = pymongo.MongoClient("mongodb+srv://lavanya:Lavan123@guvilavan.5pjwpvl.mongodb.net/?retryWrites=true&w=majority")
        db = client['sample_airbnb']
        col = db['listingsAndReviews']
        name = i.get('name')
        country = i['address'].get('country')
        property_type = i.get('property_type')
        price = i.get('price')
        room_type = i.get('room_type')

        accommodates = i.get('accommodates')
        minimum_nights = i.get('minimum_nights')
        maximum_nights = i.get('maximum_nights')
        cancellation_policy = i.get('cancellation_policy')
        number_of_reviews = i.get('number_of_reviews')

        bedrooms = i.get('bedrooms')
        beds = i.get('beds')
        guests_include = i.get('guests_included')
        extra_people = i.get('extra_people')
        review_scores_cleanliness = i['review_scores'].get('review_scores_cleanliness')
        last_scraped = i.get('last_scraped')
        
        host_name = i['host'].get('host_name')
        host_total_listings = i['host'].get('host_total_listings_count')
        calendar_last_scraped = i.get('calendar_last_scraped')
        availability_365 = i['availability'].get('availability_365')
        latitude = i['address']['location'].get('coordinates')[0]
        longitude = i['address']['location'].get('coordinates')[1]

        clm['name'].append(name)
        clm['country'].append(country)
        clm['property_type'].append(property_type)
        clm['price'].append(price)
        clm['room_type'].append(room_type)

        clm['accommodates'].append(accommodates)
        clm['minimum_nights'].append(minimum_nights)
        clm['maximum_nights'].append(maximum_nights)
        clm['number_of_reviews'].append(number_of_reviews)
        clm['cancellation_policy'].append(cancellation_policy)

        clm['bedrooms'].append(bedrooms)
        clm['beds'].append(beds)
        clm['guests_include'].append(guests_include)
        clm['extra_people'].append(extra_people)
        clm['review_scores_cleanliness'].append(review_scores_cleanliness)
        clm['last_scraped'].append(last_scraped)
        
        clm['host_name'].append(host_name)
        clm['host_listings_count'].append(host_total_listings)
        clm['availability_365'].append(availability_365)
        clm['calendar_last_scraped'].append(calendar_last_scraped)
        clm['latitude'].append(latitude)
        clm['longitude'].append(longitude)

    df = pd.DataFrame(clm)
    #data cleaning
    df['review_scores_cleanliness'] = df['review_scores_cleanliness'].fillna(0)
    df['beds'] = df['beds'].fillna(1)
    df['bedrooms'] = df['bedrooms'].fillna(1)
    df['last_scraped'] = df['last_scraped'].dt.date
    df['calendar_last_scraped'] = df['calendar_last_scraped'].dt.date
    df.dropna(inplace=True)
    return df


#dataframe
df = pd.read_csv(r'C:\Users\DELL\Desktop\Projects\Project4-Airbnb\Airbnb_Analysis.csv')
df.drop('Unnamed: 0', axis=1, inplace=True)
df.dropna(inplace=True)
#Streamlit page
st.set_page_config(layout= "wide")


def home():
    st.markdown(f""" <style>.stApp {{
                    background: url('https://www.hotelnewsnow.com/Media/Default/Legacy/FeatureImages/20160209_STR_Airbnb_Feature_Headline1.jpg');   
                    background-size: cover}}
                 </style> """,unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: right; color: black;'>Airbnb Analysis</h1>", unsafe_allow_html=True)
    st.header(" ")
    col1, col2 = st.columns(2)
    with col2:
        st.image("C:/Users/DELL/Pictures/1.webp",width=600)


    
def data_visualization():
    
    # Using columns layout to display title and image in the same line
    col1, col2, col3 = st.columns([2, 8, 4])

    # In the first column, display the image
    with col1:
        st.image("C:\\Users\\DELL\\Pictures\\airbnb_logo.jpg", width=100)
        st.write(' ')
    # In the second column, display the title
    with col2:
        st.markdown("<h1 style='color: white;'>Airbnb Analysis for Booking Rooms</h1>", unsafe_allow_html=True)


    
    #sst.markdown("<h1 style='text-align: center; color: white;'>Airbnb Analysis</h1>", unsafe_allow_html=True)
    st.header(':blue[Top 10 Property Types by Number of Reviews]')
    #st.markdown("<h2 style='text-align: left; color: blue;'>Airbnb Property Type Visualization</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)
    col7, col8 = st.columns(2)
    col9, col10 = st.columns(2)

    with col1:
        # Choose a country
        selected_country = st.selectbox("Select Country", df['country'].unique())
        
        # Filter data based on selected country
        filtered_df = df[df['country'] == selected_country]

    with col3:
        
        # Group by property type and sum the number_of_reviews
        property_reviews = filtered_df.groupby('property_type')['number_of_reviews'].sum().reset_index()

        # Sort the values by number_of_reviews in descending order
        property_reviews = property_reviews.sort_values(by='number_of_reviews', ascending=False)

        # Get top 10 property types
        top_10_property_reviews = property_reviews.head(10)

        # Plot countplot using Plotly
        fig = px.bar(top_10_property_reviews, 
                    x='property_type', 
                    y='number_of_reviews', 
                    color='property_type')
        fig.update_layout(title='Top 10 Property Types in {} by Number of Reviews'.format(selected_country),
                        xaxis_title='Property Type', 
                        yaxis_title='Number of Reviews')
        st.plotly_chart(fig, use_container_width=True)

    with col5:
        st.header(':blue[Average price of property type]')
        df_avg_price = df.groupby('property_type')['price'].mean().reset_index()
        df_avg_price = df_avg_price.sort_values(by='price', ascending=False).head(15)

        # Create a Plotly bar plot using the top 15 property types by average price
        fig = px.bar(
            df_avg_price,
            x='property_type',
            y='price',
            color='price',
            color_continuous_scale='viridis',
            title='Average Price by Property Type (Top 15)',
            labels={'property_type': 'Property Type', 'price': 'Average Price'}
        )

        # Customize the layout of the Plotly figure
        fig.update_layout(
            xaxis_title='Property Type',
            yaxis_title='Average Price',
            xaxis_tickangle=-45,
            coloraxis_colorbar=dict(title='Price', tickprefix='$')
        )

        # Render the Plotly figure in Streamlit
        st.plotly_chart(fig, use_container_width=True)
        
    with col4:
        
        
        # Group by property type and calculate the mean review score for cleanliness
        property_cleanliness = filtered_df.groupby('property_type')['review_scores_cleanliness'].sum().reset_index()

        # Sort the values by mean review score in descending order
        property_cleanliness = property_cleanliness.sort_values(by='review_scores_cleanliness', ascending=False)

        # Get top 5 property types
        top_5_property_cleanliness = property_cleanliness.head(5)

        # Plot pie chart using Plotly
        fig = px.pie(top_5_property_cleanliness, 
                    values='review_scores_cleanliness', 
                    names='property_type',
                    title='Top 5 Property Types with Highest Review Scores for Cleanliness in {}'.format(selected_country))
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        st.header(':blue[Average Price by Country]')
        country_agg = df.groupby('country').agg({'price': 'mean'}).reset_index()
        fig = px.choropleth(country_agg, 
                    locations='country', 
                    locationmode='country names',
                    color='price', 
                    hover_name='country',
                    hover_data={'country': True, 'price': True},  # Add country name to hover data
                    color_continuous_scale='Viridis',
                    title='Average Price by Country')
        st.plotly_chart(fig, use_container_width=True)
        
    with col7:
        st.header(":blue[Filter Options]")
        col1, col2 = st.columns(2)
        with col1:
            # Define the desired price range for the slider (0 to 3000)
            price_min = 0
            price_max = 3000

            # User input for price range
            st.markdown('<h2 style="color: white;">Select price range</h2>', unsafe_allow_html=True)
            price_range = st.slider(" ", price_min, price_max, (price_min, price_max))

            # Filter the DataFrame based on the selected price range
            filtered_df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]
        st.header(' ')
        
        # User input for the number of beds, bedrooms, and cancellation policy
        st.markdown('<h2 style="color: white;">Choose additional filters</h2>', unsafe_allow_html=True)
        col3, col4 ,col5= st.columns(3)
        with col3:
            selected_beds = st.selectbox("Number of beds", options=sorted(filtered_df['beds'].unique()))
        with col4:
            selected_bedrooms = st.selectbox("Number of bedrooms", options=sorted(filtered_df['bedrooms'].unique()))
        with col5:
            selected_cancellation_policy = st.selectbox("Cancellation policy", options=filtered_df['cancellation_policy'].unique())
            
    with col8:
        # Filter the DataFrame based on the user's selections
        st.header(':blue[Top 10 Apartment within Selected Filters]')
        filtered_df = filtered_df[
        (filtered_df['beds'] == selected_beds) &
        (filtered_df['bedrooms'] == selected_bedrooms) &
        (filtered_df['cancellation_policy'] == selected_cancellation_policy) &
        (filtered_df['country'] == selected_country)]

        #filtered_df = df[df['country'] == selected_country]
        # Find the top 10 apartment names based on the filtered DataFrame
        top_10_names = filtered_df['name'].value_counts().head(10).index

        # Filter the DataFrame to include only the top 10 names
        filtered_top_10_df = filtered_df[filtered_df['name'].isin(top_10_names)]

        # Truncate apartment names to a specified length (e.g., 15 characters)
        max_name_length = 15
        filtered_top_10_df['name_truncated'] = filtered_top_10_df['name'].apply(lambda x: x[:max_name_length] + '...' if len(x) > max_name_length else x)

        # Plot the bar plot of the top 10 apartment names within the selected filters using truncated names
        fig = px.bar(
            filtered_top_10_df,
            x='name_truncated',
            y='price',
            title=f'Top 10 Apartment Names within Selected Filters',
            labels={'name_truncated': 'Apartment Name', 'price': 'Price'},
            hover_data=['name','country','number_of_reviews', 'review_scores_cleanliness','guests_include','availability_365','extra_people']
        )

        # Customize layout and display the Plotly chart in Streamlit
        fig.update_layout(
            xaxis_title='Apartment Name',
            yaxis_title='Price'
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col9:
        st.header(' :blue[Apartment Details]')
        # Define custom table style
        custom_table_style = """
        <style>
        table { 
            background-color: #f2f2f2; /* Light gray background color for entire table */
            color: black; /* Text color for entire table */
            border-collapse: collapse; /* Collapse borders to ensure table lines */
        }
        th {
            color: black !important; /* Text color for header row */
            border: 1px solid black; /* Add border to header row */
        }
        td {
            color: black !important; /* Text color for data rows */
            border: 1px solid black; /* Add border to data rows */
        }
        </style>
        """

        # Apply the custom CSS style using st.markdown
        st.markdown(custom_table_style, unsafe_allow_html=True)

        option1 = st.radio("", [" :white[Show Min Price Apartment Details]", " :white[Details Apartment Name]"])

        if option1 == " :white[Show Min Price Apartment Details]":
            min_price_row = filtered_top_10_df[filtered_top_10_df['price'] == filtered_top_10_df['price'].min()]
            st.header(" :white[Minimum Price Apartment Details]")
            #st.table(min_price_row)
             # Transpose the DataFrame
            min_price_row_transposed = min_price_row.transpose()

            # Display vertical table
            st.table(min_price_row_transposed)

        if option1 == ' :white[Details Apartment Name]':
            selected_apartment_name = st.selectbox("Select Apartment Name", filtered_top_10_df['name'])
            selected_apartment_row = filtered_top_10_df[filtered_top_10_df['name'] == selected_apartment_name]
            
            if not selected_apartment_row.empty:
                st.header(f" :white[Details of {selected_apartment_name}]")
                #st.table(selected_apartment_row)
                # Transpose the DataFrame
                selected_apartment_row_trans = selected_apartment_row.transpose()

                # Display vertical table
                st.table(selected_apartment_row_trans)
            else:
                st.write("No details available for the selected apartment.")

                

def dashboard():

    st.markdown("<h1 style='text-align: center; color: white;'>Airbnb Analysis</h1>", unsafe_allow_html=True)
    #st.markdown("<h2 style='text-align: right; color: blue;'>Airbnb Property Type Visualization</h2>", unsafe_allow_html=True)
    #st.title(":blue[Airbnb Analysis]")
    st.header(':blue[Airbnb Analysis Dashboard]')
    st.header('')
    st.image("C:/Users/DELL/Downloads/Dashboard 2 (2).png", caption='Airbnb Analysis Dashboard')
    st.link_button("Go to Dashboard", "https://public.tableau.com/shared/W9C5ZQ2ZR?:display_count=n&:origin=viz_share_link")

def report():
    st.markdown("<h1 style='text-align: center; color: violet;'>Airbnb Analysis Report</h1>", unsafe_allow_html=True)
    st.header(':blue[Project Report: Airbnb Analysis Web Application]')
    st.write("""

### Introduction
The Airbnb Analysis Web Application aims to provide users with an interactive platform to explore Airbnb listings, visualize trends, and make informed decisions when selecting accommodations. By leveraging data from the Airbnb database, the application offers various features such as filtering listings, analyzing property types, and viewing detailed apartment information.

### Data Overview
Dataset: The dataset used for analysis consists of Airbnb listings and reviews obtained from the sample Airbnb database.
Variables: Key variables include property type, price, room type, number of reviews, cleanliness scores, and geographic coordinates.
Data Source: Data was sourced from the sample Airbnb database hosted on MongoDB and supplemented with additional data from a CSV file.
### Data Collection and Preprocessing
Data Collection: Utilized pymongo to connect to the MongoDB database and retrieve Airbnb listings and reviews data.
Data Cleaning: Conducted data cleaning tasks such as handling missing values, converting data types, and dropping unnecessary columns.
Feature Engineering: Created new features such as average price by property type and total number of reviews.
### Streamlit Web Application
Homepage: Designed a visually appealing homepage with background images and headers to welcome users and introduce the application.
Data Visualization: Implemented interactive visualizations using Plotly and Seaborn to showcase trends in property types, average prices, and review scores.
Filter Options: Incorporated filter options for users to refine their search based on price range, number of beds, bedrooms, and cancellation policy.
Apartment Details: Provided detailed information about individual apartments, including pricing, cleanliness scores, and availability.
### Analysis and Insights
Top Property Types: Identified the top property types by the number of reviews, average prices, and cleanliness scores.
Average Price by Country: Analyzed average prices of Airbnb listings across different countries to highlight regional pricing trends.
Filter Options Impact: Explored the impact of filter options on search results and identified top apartments within selected filters.
User Interactions: Examined user interactions with the web application to understand preferences and usage patterns.
### Conclusion
The Airbnb Analysis Web Application offers users a comprehensive platform to explore and analyze Airbnb listings effectively. By providing interactive visualizations, filter options, and detailed apartment information, 
the application empowers users to make informed decisions when choosing accommodations for their travel needs.

### Future Enhancements
Advanced Analytics: Incorporate advanced analytics techniques such as sentiment analysis of reviews or predictive modeling for pricing trends.
User Authentication: Implement user authentication and user-specific recommendations based on past preferences and behavior.
Integration with External APIs: Integrate with external APIs such as Google Maps API for enhanced location-based features and visualization. """)
    
    
    
    
option = st.sidebar.radio(":blue[Choose your page]", ["Home", "Visually Room Booking", "Dashboard", "Airbnb Analysis Report"])
    
if option == "Home":
    home()
if option == 'Visually Room Booking':
    data_visualization()
if option == "Dashboard":
    dashboard()
if option == "Airbnb Analysis Report":
    report()   
