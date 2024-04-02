import streamlit as st
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import calendar
import numpy as np
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
import streamlit_option_menu as option_menu
import plotly.graph_objects as go
import supabase
import streamlit_shadcn_ui as ui
from local_components import card_container
from streamlit_shadcn_ui import slider, input, textarea, radio_group, switch

def login_user(supabase, staffnumber, password):
    # Perform a Supabase query to fetch user data based on staff number
    response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
    user_data = response.data
    facilities_df = get_facilities(staffnumber)
    if not facilities_df.empty:
        location = facilities_df['location'].iloc[0]
        region = facilities_df['region'].iloc[0]

        # Check if the credentials match
        if password == facilities_df['password'].iloc[0]:
            return True, location, region
    return False, None, None

def sign_up_user(supabase, staffnumber, password, location, region):
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
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.is_authenticated = False
        st.session_state.show_login = True
        # Initialize session state if it doesn't exist

    form_container = st.empty()
    with form_container:
        @st.cache_resource
        def init_connection():
            url = "https://effdqrpabawzgqvugxup.supabase.co"
            key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmZmRxcnBhYmF3emdxdnVneHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA1MTQ1NDYsImV4cCI6MjAyNjA5MDU0Nn0.Dkxicm9oaLR5rm-SWlvGfV5OSZxFrim6x8-QNnc2Ua8"
            return create_client(url, key)

        supabase = init_connection()

        response = supabase.table('facilities').select("*").execute()

        location_df = pd.DataFrame(response.data)

        location_names = location_df['Location'].unique().tolist()

        if st.session_state.show_login:
            form_title = "Login Form"
            button_text = "Sign Up"
            other_form_text = "Don't have an account? Sign up here."
        else:
            form_title = "Sign Up Form"
            button_text = "Log In"
            other_form_text = "Already have an account? Log in here."

        with st.form(form_title):
            st.write(form_title)
            staffnumber = st.text_input("Staffnumber")
            password = st.text_input("Password", type='password')
            submit_button = st.form_submit_button(button_text)

            if submit_button:
                if st.session_state.show_login:
                    result, location, region = login_user(supabase, staffnumber, password)
                    if result:
                        st.success("Logged In successfully")
                        st.write(f"Location: {location}, Region: {region}")
                        st.session_state.logged_in = True
                        st.session_state.is_authenticated = True
                    else:
                        st.warning("Invalid credentials. Please try again.")
                else:
                    location = st.selectbox("Select Location", location_names)
                    selected_location_row = location_df[location_df['Location'] == location]
                    region = selected_location_row['Region'].iloc[0] if not selected_location_row.empty else None
                    count = sign_up_user(supabase, staffnumber, password, location, region)
                    if count > 0:
                        st.success("You have created a new account")
                        st.session_state.is_authenticated = True
                        st.session_state.logged_in = True
                        st.session_state.show_login = True

            st.write(other_form_text)
            if st.button("Switch Form"):
                st.session_state.show_login = not st.session_state.show_login

    if st.session_state.is_authenticated:
        # Your authenticated content here
        pass
