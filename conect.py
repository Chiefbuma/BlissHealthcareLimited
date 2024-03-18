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
import supabase


st.set_page_config(page_title="My Streamlit App", layout="wide")


@st.cache_resource
def init_connection():
    url = "https://effdqrpabawzgqvugxup.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmZmRxcnBhYmF3emdxdnVneHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA1MTQ1NDYsImV4cCI6MjAyNjA5MDU0Nn0.Dkxicm9oaLR5rm-SWlvGfV5OSZxFrim6x8-QNnc2Ua8"
    return create_client(url, key)

supabase = init_connection()

def get_facilities(staffnumber):
    # Perform a Supabase query to fetch data from the 'users' table
    response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
    login_df = pd.DataFrame(response.data)
    return login_df


def login(staffnumber,password, location, region):
    # Perform a Supabase query to fetch user data based on staff number
    response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
    user_data = response.data

    # Check if a user with the given staff number exists
    if len(user_data) == 1:
        user = user_data[0]
        # Check if the location and region match
        if user['location'] == location and user['region'] == region  and user['password'] == password:
            st.session_state.is_authenticated = True
            st.success("🎉 Login successful!")
            return True
    # If no user found or credentials don't match, show a warning message
    st.warning("Login failed. Please check your credentials.")
    return False

def add_userdata(staffnumber, password, location, region):
    # Define the data to insert
    data = {
        'staffnumber': staffnumber,
        'password': password,
        'location': location,
        'region': region
    }

    # Insert the data into the 'userdata' table using Supabase
    _, count = supabase.table('users').insert(data).execute()

    # Return the count of rows affected by the insert operation
    return count

def home():
    st.session_state.is_authenticated = False 
    
    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up", "Log Out"]
        choice = st.sidebar.selectbox("", menu)

        form_container = st.empty()
        with form_container :
            if choice == "Log Out":
                st.subheader("Log Out")

            elif choice == "Login":        
                with st.form("Login Form"):
                    st.write("Login Form")
                    staffnumber = st.text_input('Staff Number', key='login_staff_number')
                    password = st.text_input('Password', key='login_password')
                    location = st.text_input('Location', key='login_location')
                    region = st.text_input('Region', key='login_region')
                    login_btn = st.form_submit_button('Login')
                    if login_btn:
                        login_success = login(staffnumber,password, location, region)
                        if login_success:
                            # Redirect or navigate to another page upon successful login
                            st.session_state.is_authenticated = True
                       
            elif choice == "Sign up":
                with st.form("Sign-up Form"):  
                    st.write("Sign-up Form")
                    staffnumber = st.text_input('Staff Number', key='signup_staff_number')
                    location = st.text_input('Location', key='signup_location')
                    region = st.text_input('Region', key='signup_region')
                    password = st.text_input('Password', key='signup_password')
                    signup_btn = st.form_submit_button('Sign Up')
                    if signup_btn:
                        add_userdata(staffnumber, password, location, region)

    if st.session_state.is_authenticated:
        form_container.empty()
        
        @st.cache_resource
        def init_connection():
            url = "https://effdqrpabawzgqvugxup.supabase.co"
            key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmZmRxcnBhYmF3emdxdnVneHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA1MTQ1NDYsImV4cCI6MjAyNjA5MDU0Nn0.Dkxicm9oaLR5rm-SWlvGfV5OSZxFrim6x8-QNnc2Ua8"
            return create_client(url, key)

        supabase = init_connection()
        
        response = supabase.from_('Allmerged_sales').select('*').execute()
        Allsales_df = pd.DataFrame(response.data)
        st.write(Allsales_df)
        

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
