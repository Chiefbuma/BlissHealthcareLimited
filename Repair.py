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
            
            # get clients sharepoint list
            st.cache_data(ttl=80, max_entries=2000, show_spinner=False, persist=False, experimental_allow_widgets=False)
            def load_new():
                columns = [
                    "Date of report",
                    "Name of Staff",
                    "Department",
                    "Month",
                    "Date Number ",
                    "Clinic",
                    "Departmental report",
                    "Details",
                    "Report",
                    "MainLink flow",
                    "ATTACHED",
                    "MainLINK",
                    "MainItem",
                    "Labor",
                    "Amount on the Quotation",
                    "RIT Approval",
                    "RIT Comment",
                    "RIT labour",
                    "Facility Approval",
                    "Facility comments",
                    "Facility Labor",
                    "Time Line",
                    "Projects Approval",
                    "Project Comments",
                    "Project Labor",
                    "Admin Approval",
                    "Admin Comments",
                    "Admin labor",
                    "Approved amount",
                    "Finance Amount",
                    "STATUS",
                    "Approver",
                    "TYPE",
                    "Days",
                    "Disbursement",
                    "MainStatus",
                    "Modified",
                    "Modified By",
                    "Created By",
                    "ID",
                    "Email",
                    "MAINTYPE",
                    "Attachments",
                    "LinkEdit",
                    "UpdateLink",
                    "PHOTOS",
                    "QUOTES",
                    "Title",
                    "MonthName",
                    "Centre Manager Approval",
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
                except APIError as e:
                    st.error("Connection not available, check connection")
                    st.stop()
                    
            Main_df = load_new()
            
           
    

            def get_month_options():
                current_year = datetime.now().year
                current_month = datetime.now().month
                month_names = [
                    datetime(current_year, month, 3).strftime('%B')
                    for month in range(3, current_month + 1)
                ]
                month_names.insert(0, "Select Month")
                return month_names

            month_options = get_month_options()
            cols = st.columns(2)
            with cols[0]:
                ui.card(
                        content="Bliss Healthcare Maintenance Dashboard",
                        key="MCcard3"
                    ).render()
            
            with card_container(key="gallery1"):

                        
                        st.markdown('<div style="height: 0px; overflow-y: scroll;">', unsafe_allow_html=True)
                        @st.cache_data(ttl=600, max_entries=100, show_spinner=False, persist=False, experimental_allow_widgets=False)
                        def load_new():
                                New = SharePoint().connect_to_list(ls_name='Maintenance Report')
                                return pd.DataFrame(  New )
                            
                        df_main=load_new()
                        
                        data_df= df_main[['ID','Date of report','Clinic','Department','Amount on the Quotation','MainStatus','Approver','MonthName','LinkEdit']]
                        
                        # Convert 'bill_date' to datetime type
                        data_df['Date of report'] = pd.to_datetime(data_df['Date of report']).dt.date
                                            
                        # Extract just the month name
                        data_df['MonthName'] = data_df['MonthName'].str.split(';#').str[1]
                    
                        data_df = data_df.rename(columns={
                            'ID': 'Tkt',
                            'Date of report':'Date',
                            'Clinic': 'Facility',
                            'Department':'Dep',
                            'Amount on the Quotation': 'Amount',
                            'MainStatus': 'Status',
                            'MonthName':'Month',
                            'Approver': 'Approver',
                            'LinkEdit': 'Link'
                        })
                        # Fill NaN/NA values with an empty string
                        
                       # Get unique month values from the 'Month' column
                        month_options = data_df['Month'].unique().tolist()

                        # Get the current month
                        current_month = datetime.now().strftime("%B")

                        # Ensure the current month is in the options to avoid errors
                        if current_month in month_options:
                            default_selection = [current_month]  # `default` expects a list for multi-selection
                        else:
                            default_selection = []  # No default if current month isn't in options


                        from datetime import datetime
                        import streamlit as st

                        # Assuming data_df is already defined and includes the 'Month' column
                        data_df.fillna('', inplace=True)

                        # Get unique month values from the 'Month' column, if present
                        month_options = data_df['Month'].unique().tolist() if 'Month' in data_df.columns else []

                        # Get the current month
                        current_month = datetime.now().strftime("%B")

                        # Ensure the current month is in the options to avoid errors
                        default_selection = [current_month] if current_month in month_options else []

                        # Create a multi-select box with the default value set to the current month
                        selected_months = st.multiselect("Select Month", options=month_options, default=default_selection)

                        # Define the columns to filter
                        filter_columns = ["Tkt", "Approver", "Facility", "Issue", "Month"]

                        # Create filter options only for existing columns
                        filter_options = {col: data_df[col].unique().tolist() for col in filter_columns if col in data_df.columns}

                        # Initialize filter dictionary only for columns that exist in data_df
                        filters = {col: [] for col in filter_columns if col in data_df.columns}

                        # Create columns to arrange widgets horizontally
                        col1, col2, col3, col4, col5 = st.columns(5)

                        # Create dropdowns or multiselects for each filter column
                        if "Tkt" in filters:
                            with col1:
                                filters["Tkt"] = st.multiselect("Filter Tkt", options=filter_options["Tkt"])

                        if "Approver" in filters:
                            with col2:
                                filters["Approver"] = st.multiselect("Filter Approver", options=filter_options["Approver"])

                        if "Facility" in filters:
                            with col3:
                                filters["Facility"] = st.multiselect("Filter Facility", options=filter_options["Facility"])

                        if "Issue" in filters:
                            with col4:
                                filters["Issue"] = st.multiselect("Filter Issue", options=filter_options["Issue"])

                        if "Month" in filters:
                            with col5:
                                # Use the selected months from the previous multiselect as a filter for the 'Month' column
                                filters["Month"] = selected_months

                        # Apply filters to the DataFrame
                        filtered_df = data_df
                        for column, filter_values in filters.items():
                            if filter_values:  # Only filter if there are selected values
                                filtered_df = filtered_df[filtered_df[column].isin(filter_values)]

                        st.write(filtered_df)


                        # Display the filtered DataFrame using st.data_editor
                        with card_container(key="gallery4"):
                            st.data_editor(
                                filtered_df,
                                column_config={
                                    "Link": st.column_config.LinkColumn(
                                        "Link",
                                        display_text="View"
                                    )
                                },
                                hide_index=True
                            , use_container_width=True)
                                            
                                                       
                    
                  
        else:
            st.write("You  are  not  logged  in. Click   **[Account]**  on the  side  menu to Login  or  Signup  to proceed")
    
    
    except APIError as e:
            st.error("Cannot connect, Kindly refresh")
            st.stop() 
