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
    
    try:
    
        if 'is_authenticated' not in st.session_state:
            st.session_state.is_authenticated = False 
            
        if 'Location' not in st.session_state:
            st.session_state.Location = ''
        if 'Region' not in st.session_state:
            st.session_state.Region = ''
                    # Initialize session state if it doesn't exist
        
        def init_connection():
            try:
                url = "https://effdqrpabawzgqvugxup.supabase.co"
                key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmZmRxcnBhYmF3emdxdnVneHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA1MTQ1NDYsImV4cCI6MjAyNjA5MDU0Nn0.Dkxicm9oaLR5rm-SWlvGfV5OSZxFrim6x8-QNnc2Ua8"
                return create_client(url, key)
            
            except APIError as e:
                st.error("No connection, check connection")
                st.stop() 

        supabase = init_connection()
        
        response = supabase.table('facilities').select("*").execute()

        location_df = pd.DataFrame(response.data)

        def get_facilities(staffnumber):
            response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
            login_df = pd.DataFrame(response.data)
            return login_df

        def add_userdata(staffnumber, password, location, region):
            data = {
                'staffnumber': staffnumber,
                'password': password,
                'location': location,
                'region': region
            }

            _, count = supabase.table('users').insert(data).execute()
            return count

        location_names = location_df['Location'].unique().tolist()

        def login_user(staffnumber,password):
            
            try:
                response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
                user_data = response.data
                facilities_df = get_facilities(staffnumber)
                if not facilities_df.empty:
                    location = facilities_df['location'].iloc[0]
                    region = facilities_df['region'].iloc[0]
                    st.session_state.Location = location
                    st.session_state.Region =region

                    
                    if password == facilities_df['password'].iloc[0]:
                        return True, region, location
                    return False, None, None
                
            except APIError as e:
                st.error("Invalid credentials. Please log in again.")
                st.stop() 

        def view_all_users():
            response = supabase.from_('users').select('*').execute()
            data = response.data
            return data
        
        if not st.session_state.is_authenticated:
        
            col1, col2 = st.columns([2,1])
                
            with col1:
                menu = ["Login", "Sign up"]
                
                choice = st.sidebar.selectbox("", menu,key="choice_medical")
                
                if 'choice' not in st.session_state:
                    st.session_state.choice = False 
                    # Initialize session state if it doesn't exist
                    
                if 'container' not in st.session_state:
                    st.session_state.container = False 
                    # Initialize session state if it doesn't exist

                if choice == "Login":
                    st.session_state.choice = True
                    form_container = st.empty()
                    with form_container:
                        with st.form("Login Form"):
                            st.write("Login Form")
                            staffnumber = st.text_input("Staffnumber")
                            password = st.text_input("Password", type='password')
                            LogIn = st.form_submit_button("Login")
                            
                            if "logged_in" not in st.session_state:
                                st.session_state.logged_in= False
                            
                            if LogIn:
                                st.session_state.logged_in= True
                                result, location, region = login_user(staffnumber, password)
                                if result:
                                    st.success("Logged In successfully")
                                    st.write(f"Location: {location}, Region: {region}")
                                    st.session_state.logged_in= True
                                    st.session_state.is_authenticated=True
                                    st.session_state.staffnumber = staffnumber
                                    st.session_state.password = password
                                    st.session_state.Location = location
                                    st.session_state.Region =region

                                    form_container.empty()

                                else:
                                    st.warning("Invalid credentials. Please try again.")
                                
                elif choice == "Sign up":
                    st.session_state.signUp= True
                    form_container = st.empty()
                    with form_container:
                        with st.form("Sign-up Form"): 
                            staffnumber = st.text_input('Staff Number')
                            location = st.selectbox("Select Location", location_names)
                            selected_location_row = location_df[location_df['Location'] == location]
                            region = selected_location_row['Region'].iloc[0] if not selected_location_row.empty else None
                            password = st.text_input('Password',type='password')
                            signup_btn = st.form_submit_button('Sign Up')
                            
                            if "Sign_up" not in st.session_state:
                                st.session_state.Sign_up= False 
                            
                            if signup_btn:
                                st.session_state.Sign_up= True
                                add_userdata(staffnumber, password, location, region)
                                st.success("You have created a new account")
                                st.session_state.is_authenticated=True
                                st.session_state.Location = location
                                st.session_state.Region =region
                                form_container.empty()
                            else:
                                st.warning("Invalid credentials. Please try again.")
                                
    
        if st.session_state.is_authenticated:
            st.write(f"""<span style="color: green;">
                            Successfully logged in !!<br>
                            Location: <strong>{st.session_state.Region}</strong><br>
                            Region: <strong>{st.session_state.Location}</strong>.<br>\
                            <br>
                            Naviagte to your  dashboard from the menu on the sidebar.
                        </span>""", unsafe_allow_html=True)

    except APIError as e:
            st.error("Cannot connect, Kindly refresh")
            st.stop() 

           
