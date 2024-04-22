import streamlit as st
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import plotly.graph_objects as go
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import UserCredential
import streamlit_option_menu as option_menu
import streamlit_shadcn_ui as ui
from local_components import card_container
from streamlit_shadcn_ui import slider, input, textarea, radio_group, switch
from sharepoint import SharePoint
from postgrest import APIError
from IPython.display import HTML
from streamlit_dynamic_filters import DynamicFilters

def app():
    
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False 
        
    if 'Location' not in st.session_state:
        st.session_state.Location = ''
    if 'Region' not in st.session_state:
        st.session_state.Region = ''
                # Initialize session state if it doesn't exist
     
    def init_connection():
        url = "https://effdqrpabawzgqvugxup.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmZmRxcnBhYmF3emdxdnVneHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA1MTQ1NDYsImV4cCI6MjAyNjA5MDU0Nn0.Dkxicm9oaLR5rm-SWlvGfV5OSZxFrim6x8-QNnc2Ua8"
        return create_client(url, key)

    supabase = init_connection()
    
    response = supabase.table('facilities').select("*").execute()

    location_df = pd.DataFrame(response.data)
    #st.write(location_df)


    def get_facilities(staffnumber):
        # Perform a Supabase query to fetch data from the 'users' table
        response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
        login_df = pd.DataFrame(response.data)
        return login_df

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

        # Return the count of rows affected by the insert operation
        return count

    location_names = location_df['Location'].unique().tolist()
        # Create a dictionary mapping each location to its region

    def login_user(staffnumber,password):
        
        try:
            # Perform a Supabase query to fetch user data based on staff number
            response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
            user_data = response.data
            facilities_df = get_facilities(staffnumber)
            if not facilities_df.empty:
                location = facilities_df['location'].iloc[0]
                region = facilities_df['region'].iloc[0]
                st.session_state.Location = location
                st.session_state.Region =region

                
                # Check if the credentials match
                if password == facilities_df['password'].iloc[0]:
                    return True, st.session_state.Location, st.session_state.Region
                return False, None, None
            
        except APIError as e:
            st.error("Invalid credentials. Please log in again.")
            st.stop() 

    def view_all_users():
        response = supabase.from_('users').select('*').execute()
        data = response.data
        return data
    
    
    form_container = st.empty()
    with form_container:
        with st.form("Login Form"):
            st.write("Login Form")
            staffnumber = st.text_input("Staffnumber",key="staff_medical")
            password = st.text_input("Password", type='password',key="pass_medical")
            
            # Fetch location and region based on staffnumber
            cols = st.columns(4)
            with cols[0]:
                LogIn=st.form_submit_button("Login")
            with cols[3]:
                signUp=st.form_submit_button("Login")
            
            if "logged_in" not in st.session_state:
                st.session_state.logged_in= False
                
            if "Sign_up" not in st.session_state:
                st.session_state.Sign_up= False  
             
            if LogIn:
                st.session_state.logged_in= True
                result, location, region = login_user(staffnumber, password)
                if result:
                    st.success("Logged In successfully")
                    st.write(f"Location: {location}, Region: {region}")
                    st.session_state.logged_in= True
                    st.session_state.staffnumber = staffnumber
                    st.session_state.password = password
                    form_container.empty()

                else:
                    st.warning("Invalid credentials. Please try again.")
                
            elif signUp:
                st.session_state.signUp= True
                with st.form("Sign-up Form"): 
                    staffnumber = st.text_input('Staff Number', key='signup_staff_number')
                    location = st.selectbox("Select Location", location_names)
                    selected_location_row = location_df[location_df['Location'] == location]
                    region = selected_location_row['Region'].iloc[0] if not selected_location_row.empty else None
                    password = st.text_input('Password', key='signup_password')
                    signup_btn = st.form_submit_button('Sign Up')
                    if signup_btn:
                        add_userdata(staffnumber, password, location, region)
                        st.success("You have created a new account")
                        st.session_state.is_authenticated=True
                        st.session_state.logged_in= True
                        form_container.empty()
                    else:
                        st.warning("Invalid credentials. Please try again.")

