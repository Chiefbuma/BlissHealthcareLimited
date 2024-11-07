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



def app():
    
    try:

        if 'is_authenticated' not in st.session_state:
            st.session_state.is_authenticated = False 
            st.write(f"""<span style="color: red;">
                        You are not Logged in,click account to  Log in/Sign up to proceed.
                    </span>""", unsafe_allow_html=True)
        
            # Initialize session state if it doesn't exist
                    
        if st.session_state.is_authenticated:
            # Load the data once and store it in session state
            if 'data_df' not in st.session_state:
                st.cache_data(ttl=80, max_entries=2000, show_spinner=False, persist=False, experimental_allow_widgets=False)
                
                # Load data from SharePoint
                def load_data():
                    columns = [
                        "Date of report", "Name of Staff", "Department", "Month", "Date Number ", "Clinic",
                        "Departmental report", "Details", "Report", "MainLink flow", "ATTACHED", "MainLINK", 
                        "MainItem", "Labor", "Amount on the Quotation", "RIT Approval", "RIT Comment", 
                        "RIT labour", "Facility Approval", "Facility comments", "Facility Labor", "Time Line", 
                        "Projects Approval", "Project Comments", "Project Labor", "Admin Approval", 
                        "Admin Comments", "Admin labor", "Approved amount", "Finance Amount", "STATUS", 
                        "Approver", "TYPE", "Days", "Disbursement", "MainStatus", "Modified", "Modified By", 
                        "Created By", "ID", "Email", "MAINTYPE", "Attachments", "LinkEdit", "UpdateLink", 
                        "PHOTOS", "QUOTES", "Title", "MonthName", "Centre Manager Approval", 
                        "Biomedical Head Approval"
                    ]
                    
                    try:
                        clients = SharePoint().connect_to_list(ls_name='Maintenance Report', columns=columns)
                        df = pd.DataFrame(clients)
                        
                        # Ensure all specified columns are in the DataFrame, even if empty
                        for col in columns:
                            if col not in df.columns:
                                df[col] = None

                        return df
                    except APIError:
                        st.error("Connection not available, check connection")
                        st.stop()

                # Load the data and save it in session state
                df_main = load_data()
                st.session_state.data_df = df_main[['ID', 'Date of report', 'Clinic', 'Department', 
                                                    'Amount on the Quotation', 'Approver', 
                                                    'MonthName', 'LinkEdit']]

            # Rename and preprocess data for filtering
            data_df = st.session_state.data_df.copy()
            data_df['Date of report'] = pd.to_datetime(data_df['Date of report']).dt.date
            data_df['MonthName'] = data_df['MonthName'].str.split(';#').str[1]
            
            data_df = data_df.rename(columns={
                'ID': 'Tkt',
                'Date of report': 'Date',
                'Clinic': 'Facility',
                'Department': 'Dep',
                'Amount on the Quotation': 'Amount',
                'MonthName': 'Month',
                'Approver': 'Approver',
                'LinkEdit': 'Link'
            })
            
            data_df.fillna('', inplace=True)
            
            cols = st.columns([1,4])
            
            with cols[0]:
                
                with card_container(key="sum"):

                    # Get unique month values
                    month_options = data_df['Month'].unique().tolist()
                    current_month = datetime.now().strftime("%B")
                    default_selection = [current_month] if current_month in month_options else []

                    # Display filter selection widgets
                    selected_months = st.multiselect("Select Month", options=month_options, default=default_selection)

                    # Define columns to filter and create text input widgets
                    filter_columns = ["Tkt", "Approver", "Facility", "Issue"]
                    # Create five columnss for arranging widgets horizontally

                    filters = {column: st.text_input(f"Filter {column}", "") for column in filter_columns}
                    filters["Month"] = selected_months

            # Add a button to apply filters after selection
            if st.button("Apply Filters"):
                # Filter the data
                filtered_df = data_df[data_df['Month'].isin(filters["Month"])] if filters["Month"] else data_df
                
                for column, filter_value in filters.items():
                    if isinstance(filter_value, str) and filter_value:  # Handle text input filters
                        filtered_df = filtered_df[filtered_df[column].str.contains(filter_value, case=False, na=False)]
            else:
                filtered_df = data_df  
              
                    
            with cols [1]:
                # Display the filtered DataFrame
                st.data_editor(
                    filtered_df,
                    column_config={
                        "Link": st.column_config.LinkColumn(
                            "Link",
                            display_text="View"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )                       
                                                            
                            
                        
        else:
            st.write("You  are  not  logged  in. Click   **[Account]**  on the  side  menu to Login  or  Signup  to proceed")
    
    
    except APIError as e:
            st.error("Cannot connect, Kindly refresh")
            st.stop() 
