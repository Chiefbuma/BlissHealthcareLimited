import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
from local_components import card_container
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

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
import streamlit as st

def app():
    
    # Check if user is authenticated
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
        st.write("""<span style="color:red;">
                    You are not Logged in, click account to Log in/Sign up to proceed.
                </span>""", unsafe_allow_html=True)
        
    if st.session_state.is_authenticated:

       
            st.header('Dispatch Packages🔖')

            # Upload CSV file
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

            if uploaded_file is not None:
                # Define the columns to import and parse as datetime
                columns_to_import = [
                    'UHID', 'PatientName', 'Department', 'FacilityName',
                    'ConsultationBillingTime', 'Pharmacy_Billing_Time',
                ]

                try:
                    # Load the CSV file into a DataFrame with specified encoding and columns
                    TAT_df = pd.read_csv(uploaded_file, encoding='utf-8', usecols=columns_to_import, parse_dates=columns_to_import)
                except (UnicodeDecodeError, ValueError):
                    # Handle encoding issues or missing columns gracefully
                    st.error("Error reading the CSV file. Please check the file format and content.")
                    return

                # Filter rows where UHID is not blank and FacilityName is not "Bliss Medical Centre HomeCare"
                filtered_TAT_df = TAT_df.dropna(subset=['UHID'])
                filtered_TAT_df = filtered_TAT_df[filtered_TAT_df['FacilityName'] != "Bliss Medical Centre HomeCare"]

                # Create separate DataFrames based on the Department column
                Consultation_df = filtered_TAT_df[filtered_TAT_df['Department'] == 'GENERAL OPD'].drop(columns=['Pharmacy_Billing_Time'])
                Pharmacy_df = filtered_TAT_df[filtered_TAT_df['Department'] == 'Pharmacy'].drop(columns=['ConsultationBillingTime'])

                # Add a new 'date' column by extracting the date from the billing time columns
                Consultation_df['date'] = Consultation_df['ConsultationBillingTime'].dt.date
                Pharmacy_df['date'] = Pharmacy_df['Pharmacy_Billing_Time'].dt.date

                # Group by date, UHID, and FacilityName, and get the earliest Pharmacy_Billing_Time
                TAT_pharmacy_df = Pharmacy_df.groupby(['date', 'UHID', 'PatientName', 'FacilityName']).agg({
                    'Pharmacy_Billing_Time': 'min',
                    'Department': 'first'
                }).reset_index()

                # Group by date, UHID, and FacilityName, and get the earliest ConsultationBillingTime
                TAT_consultation_df = Consultation_df.groupby(['date', 'UHID', 'PatientName', 'FacilityName']).agg({
                    'ConsultationBillingTime': 'min',
                    'Department': 'first'
                }).reset_index()

                # Create a new 'Unique' column by concatenating UHID, PatientName, FacilityName, and date
                TAT_pharmacy_df['Unique'] = TAT_pharmacy_df['UHID'].astype(str) + "_" + \
                                            TAT_pharmacy_df['PatientName'].astype(str) + "_" + \
                                            TAT_pharmacy_df['FacilityName'].astype(str) + "_" + \
                                            TAT_pharmacy_df['date'].astype(str)

                TAT_consultation_df['Unique'] = TAT_consultation_df['UHID'].astype(str) + "_" + \
                                                TAT_consultation_df['PatientName'].astype(str) + "_" + \
                                                TAT_consultation_df['FacilityName'].astype(str) + "_" + \
                                                TAT_consultation_df['date'].astype(str)

                # Merge TAT_Pharmacy_df onto TAT_Consultation_df on 'Unique' column
                merged_df = TAT_consultation_df.merge(
                    TAT_pharmacy_df[['Unique', 'Pharmacy_Billing_Time']],
                    on='Unique',
                    how='left'
                )

                # Filter the merged DataFrame where Pharmacy_Billing_Time is not NaT or null
                filtered_merged_df = merged_df[merged_df['Pharmacy_Billing_Time'].notna()]

                # Calculate the time difference in minutes and create the TAT column
                filtered_merged_df['TAT'] = (filtered_merged_df['Pharmacy_Billing_Time'] - filtered_merged_df['ConsultationBillingTime']).dt.total_seconds() / 60

                # Classify shifts based on Pharmacy_Billing_Time
                def classify_shift(pharmacy_billing_time):
                    if pharmacy_billing_time.hour >= 20 or pharmacy_billing_time.hour < 7:
                        return 'Night Shift'
                    elif 7 <= pharmacy_billing_time.hour < 10:
                        return 'Morning'
                    elif 10 <= pharmacy_billing_time.hour < 13:
                        return 'Mid Morning'
                    elif 13 <= pharmacy_billing_time.hour < 16:
                        return 'Afternoon'
                    elif 16 <= pharmacy_billing_time.hour < 19:
                        return 'Evening'

                # Create a new column 'time' to extract only the time part
                filtered_merged_df['time'] = filtered_merged_df['Pharmacy_Billing_Time'].dt.time

                # Create a new column 'Shift' by applying the classify_shift function
                filtered_merged_df['Shift'] = filtered_merged_df['Pharmacy_Billing_Time'].apply(classify_shift)

                

                # Group by 'date', 'FacilityName', and 'Shift'
                grouped_df = filtered_merged_df.groupby(['date', 'FacilityName']).agg(
                    Unique_UHID_Count=('UHID', 'nunique'),  # Count of unique UHID
                    Average_TAT=('TAT', 'mean')  # Average TAT
                ).reset_index()
                
                
                # Add 20 minutes to Average TAT
                grouped_df['Average_TAT'] += 20
                
                st.write(grouped_df)
                
                # Pivot the DataFrame with FacilityName and date as index, and Shift as columns
                pivoted_df = grouped_df.pivot_table(
                    index=['FacilityName', 'date'],  # Rows as medical centers and date
                    columns='Shift',                 # Columns as shifts
                    values='Average_TAT',            # Values as Average TAT
                    aggfunc='mean'                   # Average in case of multiple entries
                )

                # Calculate the daily average (across shift columns) and add it as a new column
                pivoted_df['Day Avg'] = pivoted_df.mean(axis=1)

                # Convert TAT from minutes to "X hr Y min" format for each column, including 'Day Avg'
                pivoted_df = pivoted_df.applymap(lambda x: f"{int(x // 60)} hr {int(x % 60)} min" if pd.notnull(x) else "")

                # Reset index to make 'FacilityName' and 'date' columns
                pivoted_df = pivoted_df.reset_index()

                # Optional: Remove MultiIndex column names
                pivoted_df.columns.name = None

                # Reorder columns based on preferred shift order, including 'Day Avg'
                preferred_order = ["FacilityName", "date", "Morning", "Mid Morning", "Afternoon", "Evening", "Night Shift", "Day Avg"]
                existing_columns = [col for col in preferred_order if col in pivoted_df.columns]  # Retain only existing columns
                pivoted_df = pivoted_df[existing_columns]


                st.write(pivoted_df)
                
                


                

        
        
        
                
            
                

    else:
        st.write("Please upload a CSV file to proceed.")

if __name__ == "__main__":
    app()