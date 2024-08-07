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
import main
from streamlit_dynamic_filters import DynamicFilters
from urllib.error import HTTPError




# Path to your service account credentials file
SERVICE_ACCOUNT_FILE = 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Streamlit/blisshealtchare-fa7b1fd01b22.json'

# Scopes for Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def app():
    try:
        if 'is_authenticated' not in st.session_state:
            st.session_state.is_authenticated = False 
            st.write(
                """<span style="color: red;">
                You are not Logged in, click account to Log in/Sign up to proceed.
                </span>""", unsafe_allow_html=True
            )
        
        if st.session_state.is_authenticated:
            # Display Title and Description
            st.title("New Optical Order form")
            st.markdown("Enter the details of the new Order.")

            # Establishing a Google Sheets connection
            credentials = Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            conn = GSheetsConnection(credentials=credentials,connection_name="gsheets_conn",)

            # Fetch existing vendors data
            spreadsheet_id = '1Gq9-Uhq-JeBNWBunkmen2-YclAxNL8gp'  # Replace with your actual spreadsheet ID
            worksheet_name = 'Esslor'  # Replace with your actual worksheet name

            try:
                existing_data = conn.read(spreadsheet=spreadsheet_id, worksheet=worksheet_name, usecols=list(range(29)), ttl=5)
                existing_data = existing_data.dropna(how="all")
                st.dataframe(existing_data)
            except ValueError as ve:
                st.error(f"Value error: {ve}")
            except HTTPError as he:
                st.error(f"HTTP error occurred: {he.reason}")
            except Exception as e:
                st.error(f"An error occurred while reading the spreadsheet: {str(e)}")

        else:
            st.write("You are not logged in. Click **[Account]** on the side menu to Login or Signup to proceed")
    
    except APIError as e:
        st.error("Cannot connect, Kindly refresh")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.stop()

if __name__ == "__main__":
    app()
