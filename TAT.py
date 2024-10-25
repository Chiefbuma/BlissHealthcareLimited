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
import time
import os
from supabase import create_client, Client
from datetime import datetime



def app():
    
    # Check if user is authenticated
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
        st.write("""<span style="color:red;">
                    You are not Logged in, click account to Log in/Sign up to proceed.
                </span>""", unsafe_allow_html=True)
        
    if st.session_state.is_authenticated:
        location = st.session_state.Region
        staffnumber = st.session_state.staffnumber
        department = st.session_state.Department

        # Supabase credentials
        url = "https://effdqrpabawzgqvugxup.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmZmRxcnBhYmF3emdxdnVneHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA1MTQ1NDYsImV4cCI6MjAyNjA5MDU0Nn0.Dkxicm9oaLR5rm-SWlvGfV5OSZxFrim6x8-QNnc2Ua8"
        supabase: Client = create_client(url, key)

        with card_container("Upload"):
            st.header('Dispatch Packages🔖')
             # Upload Excel file
             # Upload CSV file
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

            if uploaded_file is not None:
                # Load CSV file into DataFrame
                df = pd.read_csv(uploaded_file)

                # Define the file path
                file_path =uploaded_file

                # Define the columns to import and parse as datetime
                columns_to_import = [
                'UHID','PatientName','Department','FacilityName',
                'ConsultationBillingTime',  'Pharmacy_Billing_Time',
                    
                ]

                # Try loading the dataset with different encodings, only importing specific columns
                try:
                    TAT_df = pd.read_csv(file_path, encoding='utf-8', usecols=columns_to_import, parse_dates=columns_to_import)
                except UnicodeDecodeError:
                    TAT_df = pd.read_csv(file_path, encoding='latin1', usecols=columns_to_import, parse_dates=columns_to_import)  # or 'ISO-8859-1', 'cp1252'

                
                # Filter rows where UHID is not blank and FacilityName is not "Bliss Medical Centre Homecare"
                filtered_TAT_df = TAT_df.dropna(subset=['UHID'])
                filtered_TAT_df = filtered_TAT_df[filtered_TAT_df['FacilityName'] != "Bliss Medical Centre HomeCare"]

                # Create separate DataFrames based on Department column
                Consultation_df = filtered_TAT_df[filtered_TAT_df['Department'] == 'GENERAL OPD'].drop(columns=['Pharmacy_Billing_Time'])
                Pharmacy_df = filtered_TAT_df[filtered_TAT_df['Department'] == 'Pharmacy'].drop(columns=['ConsultationBillingTime'])


                # Add a new 'date' column by extracting the date from the billing time columns
                Consultation_df['date'] = Consultation_df['ConsultationBillingTime'].dt.date
                Pharmacy_df['date'] = Pharmacy_df['Pharmacy_Billing_Time'].dt.date

            else:
                st.write("Please upload an Excel file to proceed.")
                

if __name__ == "__main__":
    app()