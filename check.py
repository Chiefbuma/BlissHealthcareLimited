
import streamlit as st
from st_login_form import login_form
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
from IPython.display import display
import calendar
import numpy as np
import plotly.express as px
from IPython.display import HTML
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
import streamlit_option_menu as option_menu
import plotly.graph_objects as go
# Set the page configuration



st.set_page_config(page_title="My Streamlit App", layout="wide")

def home():
    st.session_state.is_authenticated = False 
    
    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up", "Log Out"]
        choice = st.sidebar.selectbox("", menu)

        form_container = st.empty()
        with form_container :
            # Initialize connection.
            # Uses st.cache_resource to only run once.
            @st.cache_resource
            def init_connection():
                url = "https://effdqrpabawzgqvugxup.supabase.co"
                key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmZmRxcnBhYmF3emdxdnVneHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA1MTQ1NDYsImV4cCI6MjAyNjA5MDU0Nn0.Dkxicm9oaLR5rm-SWlvGfV5OSZxFrim6x8-QNnc2Ua8"
                return create_client(url, key)

            supabase = init_connection()
            
            response = supabase.from_('facilities').select('*').execute()
            location_df = pd.DataFrame(response.data)

            # Perform query.
            # Uses st.cache_data to only rerun when the query changes or after 10 min.
            @st.cache_resource(ttl=600)
            def create_usertable():
                try:
                    # Assuming `supabase` is your Supabase client
                    query = """
                    CREATE TABLE IF NOT EXISTS users (
                        staffnumber INTEGER NOT NULL,
                        password TEXT NOT NULL,
                        location TEXT NOT NULL,
                        region TEXT NOT NULL
                    );
                    """
                    supabase.query(query)
                    return True

                except Exception as e:
                    print(f"Error creating usertable: {e}")
                    return False
        
                            
            def add_userdata(staffnumber, password, location, region,supabase):
                try:
                    # Insert a new record into the 'users' table
                    supabase.table('users').insert({
                        'staffnumber': staffnumber,
                        'password': password,
                        'location': location,
                        'region': region
                    }).execute()
                    return True
                except Exception as e:
                    print(f"Error adding userdata: {e}")
                    return False
            
            def get_facilities(staffnumber):
                # Perform a Supabase query to fetch data from the 'users' table
                response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
                login_df = response.data
                return login_df
           
            def login_user(staffnumber, password):
                try:
                    # Query the 'users' table using Supabase client
                    query = f"SELECT * FROM users WHERE staffnumber = {staffnumber} AND password = '{password}'"
                    st.write("Query:", query)  # Print the query for debugging
                    result = supabase.query(query).execute()
                    

                    # Fetch location and region based on staffnumber
                    facilities_df = get_facilities(staffnumber)
                    print("Facilities DF:", facilities_df)  # Print the facilities dataframe for debugging

                    if facilities_df:
                        location = facilities_df[0]['location']
                        region = facilities_df[0]['region']

                        # Return the result, location, and region
                        return result, location, region
                    else:
                        # No facilities found for the staffnumber
                        return None, None, None
                except Exception as e:
                    # Log the error and return None for all values
                    print(f"Error logging in user: {e}")
                    return None, None, None
                
                
            response = supabase.from_('facilities').select('*').execute()
            location_df = pd.DataFrame(response.data)
            location_names = location_df["Location"]
            
            
            
             # log in app
             
            if choice == "Log Out":
                st.subheader("Log Out")

            elif choice == "Login":
                with st.form("Login Form"):
                    st.write("Login Form")
                    staffnumber = st.text_input("Staffnumber")
                    password = st.text_input("Password", type='password')
                    load = st.form_submit_button("Login")
                    facilities_df = get_facilities(staffnumber)
                    
                    location = facilities_df['location'].iloc[0]
                    region = facilities_df['region'].iloc[0]

                    if "logged_in" not in st.session_state:
                        st.session_state.logged_in= False

                    if load or st.session_state.logged_in:
                        st.session_state.logged_in = False
                        result, location, region = login_user(staffnumber, password)
                        if result:
                            st.success("Logged In successfully")
                            st.write(f"Location: {location}, Region: {region}")
                            st.session_state.is_authenticated = True
                            st.session_state["logged_in"] = True
                            form_container.empty()
                        else:
                            st.warning("Invalid credentials. Please try again.")

            elif choice == "Sign up":
                with st.form("Sign-up Form"):
                    st.write("Sign-up Form")
                    staffnumber = st.text_input("Staffnumber")
                    password = st.text_input("Password", type='password')
                    location = st.selectbox("Select Location", location_names)
                    selected_location_row = location_df[location_df['Location'] == location]
                    # Filter location_df based on selected_location
                    region_options = selected_location_row['Region'].tolist() if not selected_location_row.empty else []
                    region = st.selectbox("Select Region", region_options)
                    if st.form_submit_button("Sign up"):
                        if add_userdata(staffnumber, password, location, region,supabase):
                            st.success("You have created a new account")
                            st.session_state["logged_in"] = True
                            st.session_state.is_authenticated = True
                            form_container.empty()
                        else:
                            st.warning("Failed to create a new account. Please try again.")

    if st.session_state.is_authenticated:
            form_container.empty()
            def fraction_of_days_in_month(given_date):

                # Convert the input date string to a datetime object
                given_date = pd.to_datetime(given_date, format='%Y-%m-%d')
                
                # Extract the month and year from the given date
                month = given_date.month
                year = given_date.year
                
                # Find the number of days in the month
                days_in_month = calendar.monthrange(year, month)[1]
                
                # Calculate the fraction of days passed with two decimal places
                fraction_passed = round(given_date.day / days_in_month, 2)
                
                return fraction_passed

with st.sidebar:
    #st.image("Dashboard/logo.png", caption="Bliss Healthcare")
    selected_page = option_menu.option_menu(
        menu_title='DASHBOARDS',
        options=['Medical centre Dashboard', 'Region Dashboard', 'Departments Dashboard', "Maintenance Dashboard", 'Summary Dashboard', 'Account'],
        icons=['house-fill', 'receipt', 'receipt', 'receipt', 'receipt', 'person-circle'],
        menu_icon='house-fill',
        default_index=0,
        styles={
            "container": {"padding": "15", "background-color": {"grey": "black", "font-size": "10px"}},
            "nav-link": {"color": "Blck", "font-size": "13px", "text-align": "left"},
            "nav-link-selected": {"background-color": "Black"}
        }
    )

if st.session_state.get('selected_page'):
    selected_page = st.session_state['selected_page']
if selected_page == "Medical centre Dashboard":
    home()
else:
    pass
