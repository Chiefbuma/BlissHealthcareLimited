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
import streamlit_option_menu as option_menu
import plotly.graph_objects as go
import supabase
import streamlit_shadcn_ui as ui
from local_components import card_container
from streamlit_shadcn_ui import slider, input, textarea, radio_group, switch

# Set the page configuration
st.set_page_config(page_title="My Streamlit App", layout="wide")

def home():
        
    if "logged_in" not in st.session_state:
       st.session_state.logged_in= False
       st.session_state.is_authenticated = False 
        # Initialize session state if it doesn't exist
    
   
    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up", "Log Out"]
        choice = st.sidebar.selectbox("", menu)

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

            def view_all_users():
                response = supabase.from_('users').select('*').execute()
                data = response.data
                return data
 
            
            # log in app
            
            if choice == "Log Out":
                st.subheader("Log Out")

            elif choice == "Login":
                # Check if the user is logged in
                

                with st.form("Login Form"):
                    st.write("Login Form")
                    staffnumber = st.text_input("Staffnumber")
                    password = st.text_input("Password", type='password')
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
        @st.cache_resource
        def init_connection():
            url = "https://effdqrpabawzgqvugxup.supabase.co"
            key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmZmRxcnBhYmF3emdxdnVneHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA1MTQ1NDYsImV4cCI6MjAyNjA5MDU0Nn0.Dkxicm9oaLR5rm-SWlvGfV5OSZxFrim6x8-QNnc2Ua8"
            return create_client(url, key)

        supabase = init_connection()
        
        # Check if the connection is successful
        if init_connection():

            st.session_state.logged_in= True
            # Dropdown for selecting the year
            current_year = datetime.now().year
            
            current_month = "March"
            #current_month =datetime.now().strftime('%B')

            # Query the MTD_Revenue table with the filter for location_name and Month
            response = supabase.from_('MTD_Revenue').select('*').eq('location_name', location).eq('Month', current_month).execute()

            performance_df = pd.DataFrame(response.data)
            
            
           
            # Create a new figure
            fig3 = go.Figure()
            
            # # Define the metrics
            
            Total_budget = performance_df['Total_Revenue_Budget'].sum()
            formatted_Rev_budget = "{:,.0f}".format(Total_budget)
            
            
            #Total_budget_FF = performance_df['Budget_Footfall'].sum()
            #formatted_FF_budget = "{:,.0f}".format(Total_budget_FF)
            
            
            fig3.add_trace(
            go.Indicator(
                title={'text': "MTD BUDGET",'font': {'size': 15,'color': 'green'}},
                value= int(Total_budget)
            )
        )
            # For example, let's say you want to add a trace for the "Projection" metric
            fig3.update_layout(
                template="plotly_white",
                height=80,
                font_family="TimesNew Roman",
                width=100,
                paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                uniformtext=dict(minsize=40, mode='hide'),
                margin=dict(l=20, r=20, t=50, b=5)
                )
            
                        # Create a new figure
            fig2 = go.Figure()
            
            # # Define the Reveneu metrics
            Total_Revenue = performance_df['MTD_Actual_Revenue'].sum()
            formatted_total_revenue = "{:,.0f}".format(Total_Revenue)
            
            Arch_Rev = (performance_df['MTD_Actual_Revenue'].sum() / performance_df['MTD_Budget_Revenue'].sum()) * 100
            formatted_arch_rev = "{:.2f}%".format(Arch_Rev)
            
            
            # # Define Footfalls  metrics
            #Total_footfalls = performance_df['Footfall'].sum()
            #formatted_total_footfalls = "{:,.0f}".format(Total_footfalls)
            #Arch_FF = performance_df['%Arch_FF'].mean() * 100
            #formatted_arch_ff = "{:.0f}%".format( Arch_FF)
            
            
            fig2.add_trace(
            go.Indicator(
                title={'text': "MTD REVENUE",'font': {'size': 15,'color': 'green'}},
                value= int(Total_Revenue)
            )
        )
            # For example, let's say you want to add a trace for the "Projection" metric
            fig2.update_layout(
                template="plotly_white",
                height=80,
                font_family="TimesNew Roman",
                width=100,
                paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                uniformtext=dict(minsize=40, mode='hide'),
                margin=dict(l=20, r=20, t=50, b=5)
                )
            
            
            # Create a new figure
            fig5 = go.Figure()
            fig5.add_trace(
            go.Indicator(
                title={'text': "MTD BUDGET",'font': {'size': 15,'color': 'green'}},
                value= int(Total_budget)
            )
        )
            # For example, let's say you want to add a trace for the "Projection" metric
            fig3.update_layout(
                template="plotly_white",
                height=80,
                font_family="TimesNew Roman",
                width=100,
                paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                uniformtext=dict(minsize=40, mode='hide'),
                margin=dict(l=20, r=20, t=50, b=5)
                )
            
            # Create a new figure
             #fig6 = go.Figure()
             #fig6.add_trace(
             #go.Indicator(
                 #title={'text': "MTD FOOTFALL",'font': {'size': 15,'color': 'green'}},
                 #value= int(Total_budget)
            # For example, let's say you want to add a trace for the "Projection" metric
            #fig6.update_layout(
                #template="plotly_white",
                #height=80,
                #font_family="TimesNew Roman",
               # width=100,
                #paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                #plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                #uniformtext=dict(minsize=40, mode='hide'),
                #margin=dict(l=20, r=20, t=50, b=5)
                
            performance_df["MTD_Budget_Revenue"] = performance_df["MTD_Budget_Revenue"].apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Actual_Revenue"] = performance_df["MTD_Actual_Revenue"].apply(lambda x: '{:,}'.format(x))
            performance_df["%Arch_REV"] = performance_df["%Arch_REV"].apply(lambda x: '{:.1f}%'.format(x ))
            performance_df["Total_Revenue_Budget"] = performance_df["Total_Revenue_Budget"].apply(lambda x: '{:,}'.format(x))
            performance_df["Projected_Revenue"] = performance_df["Projected_Revenue"].apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Actual_Footfall"] = performance_df["MTD_Actual_Footfall"].apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Budget_Footfall"] = performance_df["MTD_Budget_Footfall"].apply(lambda x: '{:,}'.format(x))
            performance_df["%Arch_FF"] = performance_df["%Arch_FF"].apply(lambda x: '{:.1f}%'.format(x/100 ))
            performance_df["Total_Footfall_Budget"] = performance_df["Total_Footfall_Budget"].apply(lambda x: '{:,}'.format(x))
            performance_df["Projected_Footfalls"] = performance_df["Projected_Footfalls"].apply(lambda x: '{:,}'.format(x))

            
            fig_request_by_type_Rev = go.Figure(data=[go.Table(
                header=dict(values=['Scheme','Revenue<br>Budget','Revenue<br>Actual','%Arch<br>REV','Total<br>Budget','Projected<br>Revenue',
                                    'Footfall<br>Budget','Footfall<br>Actual','%Arch<br>FF','Total<br>Budget','Projected<br>Footfalls'],
                            fill_color='rgba(0, 84, 0, 1)',
                            align='left',
                            font=dict(family='Georgia', color='White', size=14),
                            line_color='darkslategray',  # Border color
                            line=dict(width=1)),
                            columnwidth=[40, 30, 30,30, 30, 30, 30, 30, 30, 30,40],# Border width
                cells=dict(values=[performance_df["Scheme"],
                                   performance_df["MTD_Budget_Revenue"],
                                   performance_df["MTD_Actual_Revenue"],
                                   performance_df["%Arch_REV"],
                                    performance_df["Total_Revenue_Budget"],
                                    performance_df["Projected_Revenue"],
                                     performance_df["MTD_Budget_Footfall"],
                                    performance_df["MTD_Actual_Footfall"],
                                    performance_df["%Arch_FF"],
                                    performance_df["Total_Footfall_Budget"],
                                    performance_df["Projected_Footfalls"]]
,
                        fill_color=[
                                ['rgba(0, 0, 82, 1)'],  # Blue for "Report" column
                                ['white'] * len(performance_df)  # White for "Count" column
                            ],
                        font_color=[
                                ['white'],  # Blue for "Report" column
                                ['black'] * len(performance_df)  # White for "Count" column
                            ],
                        align='left',
                        font=dict(color='black', size=14),
                        line_color='darkslategray',
                        height=25,# Border color
                        line=dict(width=0.3))),
                       
            ])
            fig_request_by_type_Rev.update_layout(
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=200,
                    width=1000,# Set all margins to 0
                    paper_bgcolor='rgba(0, 0, 0, 0)', 
                    # Set paper background color to transparent
                )
            
            
            
            def generate_sales_data():
                np.random.seed(0)  # For reproducible results
                months = ['Jan', 'Feb', 'Mar']
                sales = np.random.randint(1000, 5000, size=len(months))
                return pd.DataFrame({'Month': months, 'Sales': sales})
            
            with card_container(key="MTDREVENUE"):
                card_style3 = "border: 2px solid #000000; border-radius: 5px; padding: 10px; background-color:#ffffff; color:#000000; text-align: center; font-size: 15px;font-weight: bold; width: 100%; height: 30;"
                ui.card(
                    content=location,
                    key="MCcard3"
                ).render()

                cols = st.columns(4)
                with cols[0]:
                    ui.card(title="MTD Revenue", content=formatted_total_revenue, key="Revcard1").render()
                with cols[1]:
                    ui.card(title="MTD Budget", content=formatted_Rev_budget, key="Revcard2").render()
                with cols[2]:
                    ui.card(title="MTD Archievement", content=formatted_arch_rev, key="Revcard3").render()
                with cols[3]:
                    ui.card(title="Last Updated:", content="31/03/2024", key="Revcard4").render()  
                st.plotly_chart(fig_request_by_type_Rev, use_container_width=True)
                with st.expander("DEPARTMENTAL MTD REVENUE (CASH & FSS)"):
                    st.vega_lite_chart(generate_sales_data(), {
                    'mark': {'type': 'bar', 'tooltip': True, 'fill': 'rgb(173, 250, 29)', 'cornerRadiusEnd': 4 },
                    'encoding': {
                        'x': {'field': 'Month', 'type': 'ordinal'},
                        'y': {'field': 'Sales', 'type': 'quantitative', 'axis': {'grid': False}},
                    },}, use_container_width=True)
        
        
        # Use the expander widget
        #with st.expander("MONTHWISE REVENUE SUMMARY TABLE"):
            # Set the height of the expander
            #st.write(RR_pivot_Actual, use_container_width=True)
            #st.write(FF_pivot_Actual, use_container_width=True)
        form_container.empty()

            
            
@st.cache_resource()
def load_data(email_user, password_user, sharepoint_url, list_name):
    try:
        auth = AuthenticationContext(sharepoint_url)
        auth.acquire_token_for_user(email_user, password_user)
        ctx = ClientContext(sharepoint_url, auth)
        web = ctx.web
        ctx.load(web)
        ctx.execute_query()
        # Main form for updating or creating items
        target_list = ctx.web.lists.get_by_title(list_name)

        # Get items from SharePoint list
        items = target_list.get_items()
        ctx.load(items)
        ctx.execute_query()

        # Specify column names to import
        selected_columns = ["Dateofreport",
                            "Month",
                            "Clinic2",
                            "Region2",
                            "Typeofmaintenance",
                            "Department",
                            "Report",
                            "Details",
                            "FacilityCoordinatorApproval",
                            "FacilitycoordinatorComments",
                            "ProjectsApproval",
                            "ProjectComments",
                            "AdminApproval",
                            "AdminComments",
                            "Approvedammount",
                            "Maintenancestatus",
                            "FinanceApproval",
                            "FinanceComment",
                            "Approver",
                            "Days_x0020_Pending",
                            "Created"
                            ]

        # Convert selected columns to a DataFrame
        data = []
        for item in items:
            item_data = {key: item.properties[key] for key in selected_columns}
            data.append(item_data)
        return pd.DataFrame(data)

    except Exception as e:
        st.error("Failed to load data from SharePoint. Please check your credentials and try again.")
        st.error(f"Error details: {e}")
        return None


def maintenance():
    st.session_state.is_authenticated = False 
    
    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up", "Log Out"]
        choice = st.sidebar.selectbox("", menu)

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

            def view_all_users():
                response = supabase.from_('users').select('*').execute()
                data = response.data
                return data

            
            # log in app
            
            if choice == "Log Out":
                st.subheader("Log Out")

            elif choice == "Login":
                # Check if the user is logged in
                

                with st.form("Login Form"):
                    st.write("Login Form")
                    staffnumber = st.text_input("Staffnumber")
                    password = st.text_input("Password", type='password')
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
                            st.session_state.is_authenticated=True
                            st.session_state["logged_in"] == "True"
                            form_container.empty()

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
                        form_container.empty()
                        
    if st.session_state.is_authenticated:
        form_container.empty()                   
    
        sharepoint_url = "https://blissgvske.sharepoint.com/sites/BlissHealthcareReports"
        list_name_maintenance_report = "Maintenance Report"
        list_name_maintenance_tracker = "Maintenance Tracker"

        
        # Hardcoded email and password
        email_user = "biosafety@blisshealthcare.co.ke"
        password_user = "NaSi#2024"

        # Authentication and connection to SharePoint
        Main_df = load_data(email_user, password_user, sharepoint_url, list_name_maintenance_report)
        Maintenance_tracker_df = load_data(email_user, password_user, sharepoint_url, list_name_maintenance_tracker)
        if Main_df is not None and Maintenance_tracker_df is not None:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                Region = st.selectbox("Region:", options=[""] + list(Main_df["Region2"].unique()))
                st.markdown("<style>div[data-baseweb='card'] {background-color: blue !important;}</style>", unsafe_allow_html=True)
            with col2:
                Location = st.selectbox("Medical Centre:", options=[""] + list(Main_df["Clinic2"].unique()))
            with col3:
                Status = st.selectbox("Request Status:", options=[""] + list(Main_df["Maintenancestatus"].unique()))

            if Region == "" and Location == "" and Status == "":
                df_mainselected = Main_df
            else:
                df_mainselected = Main_df.query("Clinic2 == @Location or Region2 == @Region or Maintenancestatus == @Status")

            Total_requests = int(df_mainselected.shape[0])  # Count all rows in the filtered DataFrame

            # Filter the DataFrame to include only rows where "Maintenancestatus" is "Pending"
            pending_requests_calc = df_mainselected[df_mainselected["Maintenancestatus"] == "Pending"]

            # Count the number of rows in the filtered DataFrame
            pending_request = int(pending_requests_calc.shape[0])

            # Filter the DataFrame to include only rows where "Maintenancestatus" is "Closed"
            closed_requests_calc = df_mainselected[df_mainselected["Maintenancestatus"] == "Closed"]

            # Count the number of rows in the filtered DataFrame
            closed_request = int(closed_requests_calc.shape[0])

            # Filter out rows with non-numeric values in "Days_x0020_Pending" column
            numeric_days_pending = df_mainselected["Days_x0020_Pending"].apply(pd.to_numeric, errors="coerce")
            df_mainselected["Days_x0020_Pending"] = numeric_days_pending
            df_mainselected.dropna(subset=["Days_x0020_Pending"], inplace=True)

            # Calculate average days pending
            Average_Days_pending = int(df_mainselected["Days_x0020_Pending"].mean())
            
            # Display Table
            with st.expander("View Table"):
                st.dataframe(df_mainselected, use_container_width=True)
                
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
            with st.container():
                c1, c2, c3 = st.columns([0.5, 3, 1.5])
                # Add content to the columns
                with c1:
                    # Display the figure
                    st.plotly_chart(fig_data_cards, use_container_width=True) 
                with c2:
                    graph(df_mainselected)  # Call the graph function with df_mainselecte
                with c3:
                    graphy(df_mainselected)  # Call the graph function with df_mainselected
                    st.markdown("""<div class='.st-cd'>•</div>""", unsafe_allow_html=True)


              
def graph(df_mainselected):
    
    request_by_report = df_mainselected.groupby(by=["Typeofmaintenance"]).size().reset_index(name='Count').sort_values(by="Count", ascending=True)
    
    fig_request_by_report = px.bar(request_by_report, x="Count", y="Typeofmaintenance",
                                orientation="h", title="<b> Category of Works </b>",
                                color_discrete_sequence=["#0083b8"]*len(request_by_report), template="plotly_white")

    fig_request_by_report.update_layout(plot_bgcolor="rgba(0,255,0,0)", xaxis=dict(showgrid=True))
    
    st.plotly_chart(fig_request_by_report, use_container_width=True)
    
def graphy(df_mainselected):
    request_by_type = df_mainselected.groupby(by=["Report"]).size().reset_index(name='Count').sort_values(by="Count", ascending=False)
    
    fig_request_by_type = go.Figure(data=[go.Table(
        header=dict(values=["ITEM", "NO."],
                    fill_color='rgba(0, 131, 184, 1)',
                    align='left',
                    font=dict(color='White', size=11),
                    line_color='darkslategray',  # Border color
                    line=dict(width=1)),  # Border width
        cells=dict(values=[request_by_type["Report"], request_by_type["Count"]],
                   fill_color=[
                        ['rgba(0, 131, 184, 1)'],  # Blue for "Report" column
                        ['white'] * len(request_by_type)  # White for "Count" column
                    ],
                   font_color=[
                        ['white'],  # Blue for "Report" column
                        ['black'] * len(request_by_type)  # White for "Count" column
                    ],
                   align='left',
                   font=dict(color='black', size=11),
                   line_color='darkslategray',  # Border color
                   line=dict(width=1)))  # Border width
    ])

    fig_request_by_type.update_layout(title="<b> Type of items </b>", template="plotly_white")
    
    st.plotly_chart(fig_request_by_type, use_container_width=True)
 
 
 
       
def region():
        
    if "logged_in" not in st.session_state:
       st.session_state.logged_in= False
       st.session_state.is_authenticated = False 
        # Initialize session state if it doesn't exist
    
   
    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up", "Log Out"]
        choice = st.sidebar.selectbox("", menu)

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

            def view_all_users():
                response = supabase.from_('users').select('*').execute()
                data = response.data
                return data
 
            
            # log in app
            
            if choice == "Log Out":
                st.subheader("Log Out")

            elif choice == "Login":
                # Check if the user is logged in
                

                with st.form("Login Form"):
                    st.write("Login Form")
                    staffnumber = st.text_input("Staffnumber")
                    password = st.text_input("Password", type='password')
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
        @st.cache_resource
        def init_connection():
            url = "https://effdqrpabawzgqvugxup.supabase.co"
            key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmZmRxcnBhYmF3emdxdnVneHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA1MTQ1NDYsImV4cCI6MjAyNjA5MDU0Nn0.Dkxicm9oaLR5rm-SWlvGfV5OSZxFrim6x8-QNnc2Ua8"
            return create_client(url, key)

        supabase = init_connection()
        
        # Check if the connection is successful
        if init_connection():

            st.session_state.logged_in= True
            # Dropdown for selecting the year
                      
            current_month = "March"
            #current_month =datetime.now().strftime('%B')

            # Query the MTD_Revenue table with the filter for location_name and Month
            response = supabase.from_('MTD_Region').select('*').eq('Region', region).eq('Month', current_month).execute()

            performance_df = pd.DataFrame(response.data)
            
            # Create a new figure
            fig3 = go.Figure()
            
            # # Define the metrics
            
            Total_budget = performance_df['Total_Revenue_Budget'].sum()
            formatted_Rev_budget = "{:,.0f}".format(Total_budget)
            
            
            #Total_budget_FF = performance_df['Budget_Footfall'].sum()
            #formatted_FF_budget = "{:,.0f}".format(Total_budget_FF)
            
            
            fig3.add_trace(
            go.Indicator(
                title={'text': "MTD BUDGET",'font': {'size': 15,'color': 'green'}},
                value= int(Total_budget)
            )
        )
            # For example, let's say you want to add a trace for the "Projection" metric
            fig3.update_layout(
                template="plotly_white",
                height=80,
                font_family="TimesNew Roman",
                width=100,
                paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                uniformtext=dict(minsize=40, mode='hide'),
                margin=dict(l=20, r=20, t=50, b=5)
                )
            
                        # Create a new figure
            fig2 = go.Figure()
            
            # # Define the Reveneu metrics
            Total_Revenue = performance_df['MTD_Actual_Revenue'].sum()
            formatted_total_revenue = "{:,.0f}".format(Total_Revenue)
            
            Arch_Rev = (performance_df['MTD_Actual_Revenue'].sum() / performance_df['MTD_Budget_Revenue'].sum()) * 100
            formatted_arch_rev = "{:.2f}%".format(Arch_Rev)
            
            
            # # Define Footfalls  metrics
            #Total_footfalls = performance_df['Footfall'].sum()
            #formatted_total_footfalls = "{:,.0f}".format(Total_footfalls)
            #Arch_FF = performance_df['%Arch_FF'].mean() * 100
            #formatted_arch_ff = "{:.0f}%".format( Arch_FF)
            
            
            fig2.add_trace(
            go.Indicator(
                title={'text': "MTD REVENUE",'font': {'size': 15,'color': 'green'}},
                value= int(Total_Revenue)
            )
        )
            # For example, let's say you want to add a trace for the "Projection" metric
            fig2.update_layout(
                template="plotly_white",
                height=80,
                font_family="TimesNew Roman",
                width=100,
                paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                uniformtext=dict(minsize=40, mode='hide'),
                margin=dict(l=20, r=20, t=50, b=5)
                )
            
            
            # Create a new figure
            fig5 = go.Figure()
            fig5.add_trace(
            go.Indicator(
                title={'text': "MTD BUDGET",'font': {'size': 15,'color': 'green'}},
                value= int(Total_budget)
            )
        )
            # For example, let's say you want to add a trace for the "Projection" metric
            fig3.update_layout(
                template="plotly_white",
                height=80,
                font_family="TimesNew Roman",
                width=100,
                paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                uniformtext=dict(minsize=40, mode='hide'),
                margin=dict(l=20, r=20, t=50, b=5)
                )
            
            # Create a new figure
             #fig6 = go.Figure()
             #fig6.add_trace(
             #go.Indicator(
                 #title={'text': "MTD FOOTFALL",'font': {'size': 15,'color': 'green'}},
                 #value= int(Total_budget)
            # For example, let's say you want to add a trace for the "Projection" metric
            #fig6.update_layout(
                #template="plotly_white",
                #height=80,
                #font_family="TimesNew Roman",
               # width=100,
                #paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                #plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                #uniformtext=dict(minsize=40, mode='hide'),
                #margin=dict(l=20, r=20, t=50, b=5)
                
            performance_df["MTD_Budget_Revenue"] = performance_df["MTD_Budget_Revenue"].apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Actual_Revenue"] = performance_df["MTD_Actual_Revenue"].apply(lambda x: '{:,}'.format(x))
            performance_df["%Arch_REV"] = performance_df["%Arch_REV"].apply(lambda x: '{:.1f}%'.format(x ))
            performance_df["Total_Revenue_Budget"] = performance_df["Total_Revenue_Budget"].apply(lambda x: '{:,}'.format(x))
            performance_df["Projected_Revenue"] = performance_df["Projected_Revenue"].apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Actual_Footfall"] = performance_df["MTD_Actual_Footfall"].apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Budget_Footfall"] = performance_df["MTD_Budget_Footfall"].apply(lambda x: '{:,}'.format(x))
            performance_df["%Arch_FF"] = performance_df["%Arch_FF"].apply(lambda x: '{:.1f}%'.format(x/100 ))
            performance_df["Total_Footfall_Budget"] = performance_df["Total_Footfall_Budget"].apply(lambda x: '{:,}'.format(x))
            performance_df["Projected_Footfalls"] = performance_df["Projected_Footfalls"].apply(lambda x: '{:,}'.format(x))

            
            fig_request_by_type_Rev = go.Figure(data=[go.Table(
                header=dict(values=['Scheme','Revenue<br>Budget','Revenue<br>Actual','%Arch<br>REV','Total<br>Budget','Projected<br>Revenue',
                                    'Footfall<br>Budget','Footfall<br>Actual','%Arch<br>FF','Total<br>Budget','Projected<br>Footfalls'],
                            fill_color='rgba(0, 84, 0, 1)',
                            align='left',
                            font=dict(family='Georgia', color='White', size=14),
                            line_color='darkslategray',  # Border color
                            line=dict(width=1)),
                            columnwidth=[40, 30, 30,30, 30, 30, 30, 30, 30, 30,40],# Border width
                cells=dict(values=[performance_df["Scheme"],
                                   performance_df["MTD_Budget_Revenue"],
                                   performance_df["MTD_Actual_Revenue"],
                                   performance_df["%Arch_REV"],
                                    performance_df["Total_Revenue_Budget"],
                                    performance_df["Projected_Revenue"],
                                     performance_df["MTD_Budget_Footfall"],
                                    performance_df["MTD_Actual_Footfall"],
                                    performance_df["%Arch_FF"],
                                    performance_df["Total_Footfall_Budget"],
                                    performance_df["Projected_Footfalls"]]
,
                        fill_color=[
                                ['rgba(0, 0, 82, 1)'],  # Blue for "Report" column
                                ['white'] * len(performance_df)  # White for "Count" column
                            ],
                        font_color=[
                                ['white'],  # Blue for "Report" column
                                ['black'] * len(performance_df)  # White for "Count" column
                            ],
                        align='left',
                        font=dict(color='black', size=14),
                        line_color='darkslategray',
                        height=25,# Border color
                        line=dict(width=0.3))),
                       
            ])
            fig_request_by_type_Rev.update_layout(
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=200,
                    width=1000,# Set all margins to 0
                    paper_bgcolor='rgba(0, 0, 0, 0)', 
                    # Set paper background color to transparent
                )
            
            
            
            def generate_sales_data():
                np.random.seed(0)  # For reproducible results
                months = ['Jan', 'Feb', 'Mar']
                sales = np.random.randint(1000, 5000, size=len(months))
                return pd.DataFrame({'Month': months, 'Sales': sales})
            
            with card_container(key="MTDREVENUE"):
                card_style3 = "border: 2px solid #000000; border-radius: 5px; padding: 10px; background-color:#ffffff; color:#000000; text-align: center; font-size: 15px;font-weight: bold; width: 100%; height: 30;"
                ui.card(
                    content="Region: " + region,
                    key="MCcard3"
                ).render()

                cols = st.columns(4)
                with cols[0]:
                    ui.card(title="MTD Revenue", content=formatted_total_revenue, key="Revcard1").render()
                with cols[1]:
                    ui.card(title="MTD Budget", content=formatted_Rev_budget, key="Revcard2").render()
                with cols[2]:
                    ui.card(title="MTD Archievement", content=formatted_arch_rev, key="Revcard3").render()
                with cols[3]:
                    ui.card(title="Last Updated:", content="31/03/2024", key="Revcard4").render()    
                st.plotly_chart(fig_request_by_type_Rev, use_container_width=True)
                with st.expander("DEPARTMENTAL MTD REVENUE (CASH & FSS)"):
                    st.vega_lite_chart(generate_sales_data(), {
                    'mark': {'type': 'bar', 'tooltip': True, 'fill': 'rgb(173, 250, 29)', 'cornerRadiusEnd': 4 },
                    'encoding': {
                        'x': {'field': 'Month', 'type': 'ordinal'},
                        'y': {'field': 'Sales', 'type': 'quantitative', 'axis': {'grid': False}},
                    },}, use_container_width=True)
        
        
        # Use the expander widget
        #with st.expander("MONTHWISE REVENUE SUMMARY TABLE"):
            # Set the height of the expander
            #st.write(RR_pivot_Actual, use_container_width=True)
            #st.write(FF_pivot_Actual, use_container_width=True)


        form_container.empty()
        
        
def department():
        
    st.session_state.regionlogged_in= False
    st.session_state.is_regionauthenticated = False 
    # Initialize session state if it doesn't exist
    
   
    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up", "Log Out"]
        choice = st.sidebar.selectbox("", menu)

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

            def view_all_users():
                response = supabase.from_('users').select('*').execute()
                data = response.data
                return data
 
            
            # log in app
            
            if choice == "Log Out":
                st.subheader("Log Out")

            elif choice == "Login":
                # Check if the user is logged in
                

                with st.form("Login Form"):
                    st.write("Login Form")
                    staffnumber = st.text_input("Staffnumber")
                    password = st.text_input("Password", type='password')
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
                            st.session_state.regionlogged_in= True
                            st.session_state.is_regionauthenticated=True
                            
   
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
                        st.session_state.is_regionauthenticated=True
                        st.session_state.regionlogged_in= True
                        form_container.empty()
                        
                       
                        
    if st.session_state.is_regionauthenticated:
        st.session_state.is_authenticated=False
        @st.cache_resource
        def init_connection():
            url = "https://effdqrpabawzgqvugxup.supabase.co"
            key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmZmRxcnBhYmF3emdxdnVneHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA1MTQ1NDYsImV4cCI6MjAyNjA5MDU0Nn0.Dkxicm9oaLR5rm-SWlvGfV5OSZxFrim6x8-QNnc2Ua8"
            return create_client(url, key)

        supabase = init_connection()
        
        # Check if the connection is successful
        if init_connection():

            st.session_state.regionlogged_in= True
            # Dropdown for selecting the year
                      
            current_month = "March"
            #current_month =datetime.now().strftime('%B')

            # Query the MTD_Revenue table with the filter for location_name and Month
            response = supabase.from_('MTD_Region').select('*').eq('Region', region).eq('Month', current_month).execute()

            performance_df = pd.DataFrame(response.data)
            
            # Create a new figure
            fig3 = go.Figure()
            
            # # Define the metrics
            
            Total_budget = performance_df['Total_Revenue_Budget'].sum()
            formatted_Rev_budget = "{:,.0f}".format(Total_budget)
            
            
            #Total_budget_FF = performance_df['Budget_Footfall'].sum()
            #formatted_FF_budget = "{:,.0f}".format(Total_budget_FF)
            
            
            fig3.add_trace(
            go.Indicator(
                title={'text': "MTD BUDGET",'font': {'size': 15,'color': 'green'}},
                value= int(Total_budget)
            )
        )
            # For example, let's say you want to add a trace for the "Projection" metric
            fig3.update_layout(
                template="plotly_white",
                height=80,
                font_family="TimesNew Roman",
                width=100,
                paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                uniformtext=dict(minsize=40, mode='hide'),
                margin=dict(l=20, r=20, t=50, b=5)
                )
            
                        # Create a new figure
            fig2 = go.Figure()
            
            # # Define the Reveneu metrics
            Total_Revenue = performance_df['MTD_Actual_Revenue'].sum()
            formatted_total_revenue = "{:,.0f}".format(Total_Revenue)
            
            Arch_Rev = (performance_df['MTD_Actual_Revenue'].sum() / performance_df['MTD_Budget_Revenue'].sum()) * 100
            formatted_arch_rev = "{:.2f}%".format(Arch_Rev)
            
            
            # # Define Footfalls  metrics
            #Total_footfalls = performance_df['Footfall'].sum()
            #formatted_total_footfalls = "{:,.0f}".format(Total_footfalls)
            #Arch_FF = performance_df['%Arch_FF'].mean() * 100
            #formatted_arch_ff = "{:.0f}%".format( Arch_FF)
            
            
            fig2.add_trace(
            go.Indicator(
                title={'text': "MTD REVENUE",'font': {'size': 15,'color': 'green'}},
                value= int(Total_Revenue)
            )
        )
            # For example, let's say you want to add a trace for the "Projection" metric
            fig2.update_layout(
                template="plotly_white",
                height=80,
                font_family="TimesNew Roman",
                width=100,
                paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                uniformtext=dict(minsize=40, mode='hide'),
                margin=dict(l=20, r=20, t=50, b=5)
                )
            
            
            # Create a new figure
            fig5 = go.Figure()
            fig5.add_trace(
            go.Indicator(
                title={'text': "MTD BUDGET",'font': {'size': 15,'color': 'green'}},
                value= int(Total_budget)
            )
        )
            # For example, let's say you want to add a trace for the "Projection" metric
            fig3.update_layout(
                template="plotly_white",
                height=80,
                font_family="TimesNew Roman",
                width=100,
                paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                uniformtext=dict(minsize=40, mode='hide'),
                margin=dict(l=20, r=20, t=50, b=5)
                )
            
            # Create a new figure
             #fig6 = go.Figure()
             #fig6.add_trace(
             #go.Indicator(
                 #title={'text': "MTD FOOTFALL",'font': {'size': 15,'color': 'green'}},
                 #value= int(Total_budget)
            # For example, let's say you want to add a trace for the "Projection" metric
            #fig6.update_layout(
                #template="plotly_white",
                #height=80,
                #font_family="TimesNew Roman",
               # width=100,
                #paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                #plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                #uniformtext=dict(minsize=40, mode='hide'),
                #margin=dict(l=20, r=20, t=50, b=5)
                
            performance_df["MTD_Budget_Revenue"] = performance_df["MTD_Budget_Revenue"].apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Actual_Revenue"] = performance_df["MTD_Actual_Revenue"].apply(lambda x: '{:,}'.format(x))
            performance_df["%Arch_REV"] = performance_df["%Arch_REV"].apply(lambda x: '{:.1f}%'.format(x ))
            performance_df["Total_Revenue_Budget"] = performance_df["Total_Revenue_Budget"].apply(lambda x: '{:,}'.format(x))
            performance_df["Projected_Revenue"] = performance_df["Projected_Revenue"].apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Actual_Footfall"] = performance_df["MTD_Actual_Footfall"].apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Budget_Footfall"] = performance_df["MTD_Budget_Footfall"].apply(lambda x: '{:,}'.format(x))
            performance_df["%Arch_FF"] = performance_df["%Arch_FF"].apply(lambda x: '{:.1f}%'.format(x/100 ))
            performance_df["Total_Footfall_Budget"] = performance_df["Total_Footfall_Budget"].apply(lambda x: '{:,}'.format(x))
            performance_df["Projected_Footfalls"] = performance_df["Projected_Footfalls"].apply(lambda x: '{:,}'.format(x))

            
            fig_request_by_type_Rev = go.Figure(data=[go.Table(
                header=dict(values=['Scheme','Revenue<br>Budget','Revenue<br>Actual','%Arch<br>REV','Total<br>Budget','Projected<br>Revenue',
                                    'Footfall<br>Budget','Footfall<br>Actual','%Arch<br>FF','Total<br>Budget','Projected<br>Footfalls'],
                            fill_color='rgba(0, 84, 0, 1)',
                            align='left',
                            font=dict(family='Georgia', color='White', size=14),
                            line_color='darkslategray',  # Border color
                            line=dict(width=1)),
                            columnwidth=[40, 30, 30,30, 30, 30, 30, 30, 30, 30,40],# Border width
                cells=dict(values=[performance_df["Scheme"],
                                   performance_df["MTD_Budget_Revenue"],
                                   performance_df["MTD_Actual_Revenue"],
                                   performance_df["%Arch_REV"],
                                    performance_df["Total_Revenue_Budget"],
                                    performance_df["Projected_Revenue"],
                                     performance_df["MTD_Budget_Footfall"],
                                    performance_df["MTD_Actual_Footfall"],
                                    performance_df["%Arch_FF"],
                                    performance_df["Total_Footfall_Budget"],
                                    performance_df["Projected_Footfalls"]]
,
                        fill_color=[
                                ['rgba(0, 0, 82, 1)'],  # Blue for "Report" column
                                ['white'] * len(performance_df)  # White for "Count" column
                            ],
                        font_color=[
                                ['white'],  # Blue for "Report" column
                                ['black'] * len(performance_df)  # White for "Count" column
                            ],
                        align='left',
                        font=dict(color='black', size=14),
                        line_color='darkslategray',
                        height=25,# Border color
                        line=dict(width=0.3))),
                       
            ])
            fig_request_by_type_Rev.update_layout(
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=200,
                    width=1000,# Set all margins to 0
                    paper_bgcolor='rgba(0, 0, 0, 0)', 
                    # Set paper background color to transparent
                )
            
            
            
            def generate_sales_data():
                np.random.seed(0)  # For reproducible results
                months = ['Jan', 'Feb', 'Mar']
                sales = np.random.randint(1000, 5000, size=len(months))
                return pd.DataFrame({'Month': months, 'Sales': sales})
            
            with card_container(key="MTDREVENUE"):
                card_style3 = "border: 2px solid #000000; border-radius: 5px; padding: 10px; background-color:#ffffff; color:#000000; text-align: center; font-size: 15px;font-weight: bold; width: 100%; height: 30;"
                ui.card(
                    content="Region: " + region,
                    key="MCcard3"
                ).render()

                cols = st.columns(4)
                with cols[0]:
                    ui.card(title="MTD Revenue", content=formatted_total_revenue, key="Revcard1").render()
                with cols[1]:
                    ui.card(title="MTD Budget", content=formatted_Rev_budget, key="Revcard2").render()
                with cols[2]:
                    ui.card(title="MTD Archievement", content=formatted_arch_rev, key="Revcard3").render()
                with cols[3]:
                    ui.card(title="Last Updated:", content="31/03/2024", key="Revcard4").render()    
                st.plotly_chart(fig_request_by_type_Rev, use_container_width=True)
                with st.expander("DEPARTMENTAL MTD REVENUE (CASH & FSS)"):
                    st.vega_lite_chart(generate_sales_data(), {
                    'mark': {'type': 'bar', 'tooltip': True, 'fill': 'rgb(173, 250, 29)', 'cornerRadiusEnd': 4 },
                    'encoding': {
                        'x': {'field': 'Month', 'type': 'ordinal'},
                        'y': {'field': 'Sales', 'type': 'quantitative', 'axis': {'grid': False}},
                    },}, use_container_width=True)
        
        
        # Use the expander widget
        #with st.expander("MONTHWISE REVENUE SUMMARY TABLE"):
            # Set the height of the expander
            #st.write(RR_pivot_Actual, use_container_width=True)
            #st.write(FF_pivot_Actual, use_container_width=True)


        form_container.empty()       

with st.sidebar:
    #st.image("Dashboard/logo.png", caption="Bliss Healthcare")
        selected_page = option_menu.option_menu(
        menu_title='DASHBOARDS',
        options=['Medical centre Dashboard', 'Region Dashboard', 'Departments Dashboard', "Maintenance Dashboard", 'Summary Dashboard', 'Account'],
        icons=['house-fill', 'receipt', 'receipt', 'receipt', 'receipt', 'person-circle'],
        menu_icon='house-fill',
        default_index=0,
        styles={
            "container": {"padding": "15", "background-color": {"grey": "black", "font-size": "10px"}},
            "nav-link": {"color": "Blck", "font-size": "13px", "text-align": "left"},
            "nav-link-selected": {"background-color": "Black"}
        }
    )

if st.session_state.get('selected_page'):
    selected_page = st.session_state['selected_page']
if selected_page == "Medical centre Dashboard":
    home()
elif selected_page == "Region Dashboard":
    region()
elif selected_page == "Departments Dashboard":
   department()
elif selected_page == "Maintenance Dashboard":
   maintenance()
else:
    pass