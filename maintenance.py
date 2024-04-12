import streamlit as st
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
from office365.sharepoint.client_context import UserCredential
import streamlit_option_menu as option_menu
import plotly.graph_objects as go
import supabase
import streamlit_shadcn_ui as ui
from local_components import card_container
from streamlit_shadcn_ui import slider, input, textarea, radio_group, switch

import main
from postgrest import APIError


def app():
        
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False 
        # Initialize session state if it doesn't exist

   
    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up"]
        choice = st.sidebar.selectbox("", menu,key="choice_medical")

        form_container = st.empty()
        with form_container :
            @st.cache_resource
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
                        
                        
                        # Check if the credentials match
                        if password == facilities_df['password'].iloc[0]:
                            return True, location, region
                        return False, None, None
                    
                except APIError as e:
                    st.error("Invalid credentials. Please log in again.")
                    st.stop() 

            def view_all_users():
                response = supabase.from_('users').select('*').execute()
                data = response.data
                return data
 

            if choice == "Login":
                # Check if the user is logged in
                
                with st.form("Login Form"):
                    st.write("Login Form")
                    staffnumber = st.text_input("Staffnumber",key="staff_medical")
                    password = st.text_input("Password", type='password',key="pass_medical")
                    # Fetch location and region based on staffnumber
                    load=st.form_submit_button("Login")
                    
                    
                    if "logged_in" not in st.session_state:
                        st.session_state.logged_in= False
                        
                        
                    if load or st.session_state.logged_in:
                        st.session_state.logged_in= True
  
                        result, location, region = login_user(staffnumber, password)
                        if result:
                            st.success("Logged In successfully")
                            st.write(f"Location: {location}, Region: {region}")

                            st.session_state.logged_in= True
                            st.session_state.is_authenticated=True
                            st.session_state.staffnumber = staffnumber
                            st.session_state.password = password
                            
   
                        else:
                            st.warning("Invalid credentials. Please try again.")

            elif choice == "Sign up":
                with st.form("Sign-up Form"):  
                    st.write("Sign-up Form")
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
                        
                        
                        
    if st.session_state.is_authenticated:        
        form_container.empty()  
        
        @st.cache_resource()
        def load_data(username, password, sharepoint_url, list_name):
            try:
                user_credentials = UserCredential(username, password)
                ctx = ClientContext(sharepoint_url).with_credentials(user_credentials)
                web = ctx.web
                ctx.load(web)
                ctx.execute_query()
                target_list = ctx.web.lists.get_by_title(list_name)
                items = target_list.get_items()
                ctx.load(items)
                ctx.execute_query()

                selected_columns= [
                        "ID",
                        "Title",
                        "AuthorId",
                        "Dateofreport",
                        "DateNumber",
                        "Typeofmaintenance",
                        "Details",
                        "Month",
                        "FacilitycoordinatorComments",
                        "Approvedammount",
                        "Receivedstatus",
                        "ReceivedAmmount",
                        "Maintenancestatus",
                        "ProjectsApproval",
                        "ProjectComments",
                        "AdminApproval",
                        "AdminComments",
                        "FinanceApproval",
                        "FinanceComment",
                        "FacilityApproval",
                        "Approver",
                        "LinkEdit",
                        "AmmountontheQuotation",
                        "Clinic2",
                        "Region2",
                        "CentreManager2",
                        "Department",
                        "RITApproval",
                        "RITComment",
                        "BiomedicalHeadApproval",
                        "BiomedicalHeadComments",
                        "MarketingManagerApproval",
                        "MarketingManagerComments",
                        "Phone",
                        "Days_x0020_Pending",
                        "Report",
                        "Qty",
                        "FacilityQty",
                        "ProjectsQty",
                        "AdminQty",
                        "Laborcost",
                        "MainItem",
                        "TimeLine",
                        "RITlabour",
                        "FacilityLabor",
                        "ProjectLabor",
                        "Adminlabor",
                        "Disbursement"
                    ]



                data = []
                for item in items:
                    item_data = {key: item.properties[key] for key in selected_columns}
                    data.append(item_data)
                return pd.DataFrame(data)

            except Exception as e:
                st.error("Failed to load data from SharePoint. Please check your credentials and try again.")
                st.error(f"Error details: {e}")
                return None

        sharepoint_url = "https://blissgvske.sharepoint.com/sites/BlissHealthcareReports"
        list_name = "Maintenance Report"
        username = "biosafety@blisshealthcare.co.ke"
        password = "NaSi#2024"
       
        with card_container(key="Main1"):
                        
            Main_df = load_data(username, password, sharepoint_url, list_name)
            
            if 'is_authenticated' not in st.session_state:
                st.session_state.is_authenticated = True
                st.session_state.logged_in= True
                # Initialize session state if it doesn't exist
            
            if ui.tabs or st.session_state.is_authenticated:
                st.session_state.is_authenticated=True
                ui.tabs(options=['PyGWalker', 'Graphic Walker', 'GWalkR', 'RATH'], default_value='PyGWalker', key="kanaries")
                    
                #Region = st.selectbox("Region:", options=[""] + list(Main_df["Region2"].unique()))
                #Location = st.selectbox("Medical Centre:", options=[""] + list(Main_df["Clinic2"].unique()))
                #Status = st.selectbox("Request Status:", options=[""] + list(Main_df["Maintenancestatus"].unique()))
                #if Region == "" and Location == "" and Status == "":
                    #df_mainselected = Main_df
                #else:
                    #df_mainselected = Main_df.query("Clinic2 == @Location or Region2 == @Region or Maintenancestatus == @Status")

                Total_requests = int(Main_df.shape[0])  # Count all rows in the filtered DataFrame

                # Filter the DataFrame to include only rows where "Maintenancestatus" is "Pending"
                pending_requests_calc =  Main_df [Main_df ["Maintenancestatus"] == "Pending"]

                # Count the number of rows in the filtered DataFrame
                pending_request = int(pending_requests_calc.shape[0])

                # Filter the DataFrame to include only rows where "Maintenancestatus" is "Closed"
                closed_requests_calc =  Main_df [ Main_df ["Maintenancestatus"] == "Closed"]

                # Count the number of rows in the filtered DataFrame
                closed_request = int(closed_requests_calc.shape[0])

                # Filter out rows with non-numeric values in "Days_x0020_Pending" column
                numeric_days_pending = Main_df["Days_x0020_Pending"].apply(pd.to_numeric, errors="coerce")
                Main_df["Days_x0020_Pending"] = numeric_days_pending
                Main_df.dropna(subset=["Days_x0020_Pending"], inplace=True)

                # Calculate average days pending
                Average_Days_pending = int(Main_df["Days_x0020_Pending"].mean())
                
                

                if Main_df is not None:
                    cols = st.columns(4)
                    with cols[0]:
                        ui.card(title="Total Request", content=Total_requests, key="Revcard10", style={"height": "150px"}).render()
                    with cols[1]:
                        ui.card(title="Closed Request", content=closed_request , key="Revcard11").render()
                    with cols[2]:
                        ui.card(title="Pending Request", content=pending_request , key="Revcard12").render()
                    with cols[3]:
                        ui.card(title="Average TAT:", content=Average_Days_pending, key="Revcard13").render()  
                    
                # Display Table
                with st.expander("View Table"):
                    st.dataframe(Main_df, use_container_width=True)
                    
            # Define the metrics
                metrics = [
                    {"label": "Total", "value": Total_requests},
                    {"label": "Closed", "value": closed_request},
                    {"label": "Pending", "value": pending_request},
                    {"label": "TAT(days)", "value": Average_Days_pending}
                ]

                # Create the data cards
                fig_data_cards = go.Figure()

                for i, metric in enumerate(metrics):
                    fig_data_cards.add_trace(go.Indicator(
                        mode="number",
                        value=metric["value"],
                        number={'font': {'size': 25, 'color': 'white'}},
                        domain={'row': i, 'column': 0},  # Set the row and column to stack vertically
                        title={'text': metric["label"],'font': {'size': 20,'color': 'white'}},
                        align="center"
                    ))

                # Update layout
                fig_data_cards.update_layout(
                    grid={'rows': len(metrics), 'columns': 1, 'pattern': "independent"},
                    template="plotly_white",
                    height=100*len(metrics),  # Adjust the height based on the number of metrics
                    paper_bgcolor='rgba(0, 131, 184, 1)',  # Set background color to transparent
                    plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                    uniformtext=dict(minsize=40, mode='hide'),
                    margin=dict(l=20, r=20, t=50, b=5)
                    
                    )

                st.markdown(
                    """
                    <style>
                    .st-cd {
                        border: 1px solid #e6e9ef;
                        border-radius: 5px;
                        padding: 10px;
                        margin-bottom: 10px;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
    )
            


