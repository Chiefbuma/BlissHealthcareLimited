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

        with card_container("Upload"):

           
            st.write("Username:10443")
            st.write("Password:123")
            st.header('Turn Around Time(TAT)🔖')
            # Upload CSV file
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

            st.write(
            "[Click here to Download TAT Dump ](https://app.blissmedicalcentre.com/dashboard/DashBoard.aspx?name=ConsolidatedTATReportNew)")

            if uploaded_file is not None:
                # Define the columns to import and parse as datetime
                columns_to_import = [
                    'UHID', 'PatientName', 'Department', 'FacilityName',
                    'ConsultationBillingTime', 'Pharmacy_Billing_Time',
                ]

                try:
                    # Load the CSV file into a DataFrame with specified encoding and columns
                    TAT_df = pd.read_csv(
                        uploaded_file, encoding='utf-8', usecols=columns_to_import, parse_dates=columns_to_import)
                except (UnicodeDecodeError, ValueError):
                    # Handle encoding issues or missing columns gracefully
                    st.error(
                        "Error reading the CSV file. Please check the file format and content.")
                    return

                # Filter rows where UHID is not blank and FacilityName is not "Bliss Medical Centre HomeCare"
                filtered_TAT_df = TAT_df.dropna(subset=['UHID'])
                filtered_TAT_df = filtered_TAT_df[filtered_TAT_df['FacilityName']
                                                  != "Bliss Medical Centre HomeCare"]

                # Create separate DataFrames based on the Department column
                Consultation_df = filtered_TAT_df[filtered_TAT_df['Department'] == 'GENERAL OPD'].drop(
                    columns=['Pharmacy_Billing_Time'])
                Pharmacy_df = filtered_TAT_df[filtered_TAT_df['Department'] == 'Pharmacy'].drop(
                    columns=['ConsultationBillingTime'])

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
                filtered_merged_df = merged_df[merged_df['Pharmacy_Billing_Time'].notna(
                )]

                # Calculate the time difference in minutes and create the TAT column
                filtered_merged_df['TAT'] = (filtered_merged_df['Pharmacy_Billing_Time'] -
                                             filtered_merged_df['ConsultationBillingTime']).dt.total_seconds() / 60

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
                filtered_merged_df['Shift'] = filtered_merged_df['Pharmacy_Billing_Time'].apply(
                    classify_shift)

                # Group by 'date', 'FacilityName', and 'Shift'
                grouped_df = filtered_merged_df.groupby(['date', 'FacilityName', 'Shift']).agg(
                    # Count of unique UHID
                    Unique_UHID_Count=('UHID', 'nunique'),
                    Average_TAT=('TAT', 'mean')  # Average TAT
                ).reset_index()

                # Group by 'date', 'FacilityName', and 'Shift'
                patient_df = filtered_merged_df.groupby(['date', 'PatientName', 'FacilityName', 'ConsultationBillingTime', 'Pharmacy_Billing_Time']).agg(
                    # Count of unique UHID
                    Average_TAT=('TAT', 'mean')  # Average TAT
                ).reset_index()

                # Add 20 minutes to Average TAT
                patient_df['Average_TAT'] += 20

                cols = st.columns([2, 1])
                with cols[0]:
                    # Select box for TAT filter
                    tat_filter = st.selectbox("Select TAT Filter", [
                                              "All", "TAT above 1 hour (60)"])

                    # Apply filter based on the selected option
                    if tat_filter == "TAT above 1 hour (60)":
                        filtered_df = patient_df[patient_df['Average_TAT'] > 59]
                    else:
                        filtered_df = patient_df

                    # Group by 'date', 'FacilityName', and 'Shift'
                    grouped_All = filtered_merged_df.groupby(['date', 'FacilityName']).agg(
                        Average_TAT=('TAT', 'mean')  # Average TAT
                    ).reset_index()

                    # Add 20 minutes to Average TAT
                    grouped_All['Average_TAT'] += 20

                    # Pivot the DataFrame with FacilityName and date as index, and Shift as columns
                    pivoted_df = grouped_df.pivot_table(
                        # Rows as medical centers and date
                        index=['FacilityName', 'date'],
                        columns='Shift',                 # Columns as shifts
                        values='Average_TAT',            # Values as Average TAT
                        aggfunc='mean'                   # Average in case of multiple entries
                    )

                    # Calculate the daily average (across shift columns) and add it as a new column
                    pivoted_df['Day Avg'] = pivoted_df.mean(axis=1)

                    # Convert TAT from minutes to "X hr Y min" format for each column, including 'Day Avg'
                    pivoted_df = pivoted_df.applymap(
                        lambda x: f"{int(x // 60)} hr {int(x % 60)} min" if pd.notnull(x) else "")

                    # Reset index to make 'FacilityName' and 'date' columns
                    pivoted_df = pivoted_df.reset_index()

                    # Optional: Remove MultiIndex column names
                    pivoted_df.columns.name = None

                    # Reorder columns based on preferred shift order, including 'Day Avg'
                    preferred_order = ["FacilityName", "date", "Morning",
                                       "Mid Morning", "Afternoon", "Evening", "Night Shift", "Day Avg"]
                    # Retain only existing columns
                    existing_columns = [
                        col for col in preferred_order if col in pivoted_df.columns]
                    pivoted_df = pivoted_df[existing_columns]

                    st.write(filtered_df)

                with cols[1]:
                    tat_filter_2 = st.selectbox(
                        "Select", ["All", "TAT above 1 hour (60)"])
                    st.write(grouped_All)

                # Assuming 'filtered_merged_df' is already defined and contains the 'TAT' and 'Pharmacy_Billing_Time' columns

                # Extract just the time component
                filtered_merged_df['time'] = filtered_merged_df['Pharmacy_Billing_Time'].dt.time

                # Filter for times between 07:00:00 and 20:00:00
                start_time = pd.to_datetime("07:00:00").time()
                end_time = pd.to_datetime("20:00:00").time()
                filtered_period_df = filtered_merged_df[(
                    filtered_merged_df['time'] >= start_time) &
                    (filtered_merged_df['time'] <= end_time)
                ]

                # Convert time to hours for the x-axis
                time_in_hours = (
                    filtered_period_df['Pharmacy_Billing_Time'].dt.hour +
                    filtered_period_df['Pharmacy_Billing_Time'].dt.minute / 60
                )

                # Optional: Use a subset of data if the dataset is too large
                # Adjust sample size as needed
                sample_size = min(2000, len(filtered_period_df))
                sampled_data = filtered_period_df.sample(
                    n=sample_size, random_state=42)
                time_sampled = time_in_hours.loc[sampled_data.index]
                tat_sampled = sampled_data['TAT']
                index_sampled = sampled_data.index

                # Calculate density for color mapping
                xy = np.vstack([time_sampled, index_sampled])
                density = gaussian_kde(xy)(xy)

                # Create scatter plot with density-based coloring and TAT-based point sizing
                plt.figure(figsize=(6, 3))
                scatter = plt.scatter(
                    time_sampled,
                    index_sampled,
                    s=tat_sampled,       # Size points by TAT values
                    c=density,           # Color points by density
                    cmap='viridis',
                    alpha=0.7
                )

                # Customize the plot with 3-hour intervals
                plt.title('Distribution of Patients Visits')
                plt.xlabel("Time of Day")
                plt.ylabel("Patients")
                # Set x-ticks to 3-hour intervals from 07:00 to 19:00
                plt.xticks(np.arange(7, 20, 3))
                plt.colorbar(scatter)  # Add a color bar to show density levels

                # Display the plot in Streamlit
                st.pyplot(plt)
