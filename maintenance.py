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
import main
from postgrest import APIError
from IPython.display import HTML
from streamlit_dynamic_filters import DynamicFilters

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
        
        # get clients sharepoint list
        def load_data():
                clients = SharePoint().connect_to_list(ls_name='Maintenance Report')
                return pd.DataFrame(clients)

        @st.cache_data
        def get_main_df():
            return load_data()
        
        # Load the main DataFrame
        Main_df = get_main_df()
        

        # Add a button to update the data
        if st.button('Update Data'):
            Main_df = load_data()
            form_container.empty()
            
        # Filter the Main_df DataFrame to get the "departmental report" column
        departmental_report_df =  Main_df["Departmental report"]

        # Assuming departmental_report_df is your DataFrame
        category_counts =  departmental_report_df.value_counts().reset_index()
        
            # Rename the columns to "Category" and "No."
        category_counts.columns = ["Category", "No."]
        
        # Convert "No." column to integers
        category_counts["No."] = category_counts["No."].astype(int)

        # Display the new DataFrame
        #st.write(category_counts) 
        
                # Filter the Main_df DataFrame where 'Director approval' is equal to 'Approved'
        approved_main_df = Main_df[Main_df['Admin Approval'] == 'Approved']

        # Get unique items in the "Report" column
        unique_reports = approved_main_df["Report"].unique()

        # Create an empty dictionary to store the sum of approved amounts for each unique report
        report_sum = {}

        # Iterate over each unique report and calculate the sum of approved amounts
        for report in unique_reports:
            sum_approved_amount = approved_main_df[approved_main_df["Report"] == report]["Approved amount"].sum()
            report_sum[report] = sum_approved_amount

        # Convert the dictionary to a DataFrame for easier visualization
        report_sum_df = pd.DataFrame(list(report_sum.items()), columns=["Item", "Cost"])

        # Display the DataFrame
        #st.write(report_sum_df)

                    
                
        Director_Approved=  Main_df [Main_df ["Admin Approval"]=="Approved"]
        Dir_Approved_value = '{:,.0f}'.format(Director_Approved["Approved amount"].sum())
        Dir_Approved_request=  Director_Approved["ID"].nunique()
        Director_pending = Main_df[(Main_df["Approver"]=="DIRECTOR") & (Main_df["Projects Approval"] == "Approved")]
        Dir_pending_request=  Director_pending["ID"].nunique()
        Director_Rejected=  Main_df [Main_df ["Admin Approval"]=="Rejected"]
        Dir_rejecetd_request= Director_Rejected["ID"].nunique()
        
        
        Ops_Approved=  Main_df [Main_df ["RIT Approval"]=="Approved"]
        Ops_Approved_value= '{:,.0f}'.format(Ops_Approved["Approved amount"].sum())
        Ops_Approved_request= Ops_Approved["ID"].nunique()
        Ops_pending = Main_df[(Main_df["Approver"] == "OPERATIONS") & (Main_df["RIT Approval"].isnull())]
        Ops_pending_request=  Ops_pending["ID"].nunique()
        Ops_rejected=  Main_df [Main_df ["RIT Approval"]=="Rejected"]
        Ops_rejecetd_request= Ops_rejected["ID"].nunique()
        
        
        Fac_Approved=  Main_df [Main_df ["Facility Approval"]=="Approved"]
        Fac_Approved_value = '{:,.0f}'.format(Fac_Approved["Approved amount"].sum())
        Fac_Approved_request= Fac_Approved["ID"].nunique()
        Fac_pending = Main_df[(Main_df["Approver"]=="FACILITY") & (Main_df["RIT Approval"] == "Approved")]
        Fac_pending_request=  Fac_pending["ID"].nunique()
        Fac_rejected=  Main_df [Main_df ["Facility Approval"]=="Rejected"]
        Fac_rejected_request=  Fac_rejected["ID"].nunique()
        
        
        Pro_Approved=  Main_df [Main_df ["Projects Approval"]=="Approved"]
        Pro_Approved_value = '{:,.0f}'.format(Pro_Approved["Approved amount"].sum())
        Pro_Approved_request= Pro_Approved["ID"].nunique()
        Pro_pending = Main_df[(Main_df["Approver"]=="PROJECTS") & (Main_df["Facility Approval"] == "Approved")]
        Pro_pending_request=  Pro_pending["ID"].nunique()
        Pro_rejected=  Main_df [Main_df ["Projects Approval"]=="Rejected"]
        Pro_rejected_request=  Pro_rejected["ID"].nunique()
        
        
        #st.write(Dir_Approved_value)
        #st.write(Main_df.columns)
        

        #ALL SUMMARY
        Total_requests = Main_df["ID"].nunique()
        
        Total_Value = Main_df.groupby('ID')["Amount on the Quotation"].sum().sum()

        pending_requests_calc =  Main_df [Main_df ["MainStatus"] == "Pending"]
        pending_request = int(pending_requests_calc.shape[0])
        
        
        pending_value=pending_requests_calc.groupby('ID')["Amount on the Quotation"].sum().sum()

        closed_requests_calc =  Main_df [ Main_df ["MainStatus"] == "Closed"]
        closed_request = int(closed_requests_calc.shape[0])

        numeric_days_pending = Main_df["Days"].apply(pd.to_numeric, errors="coerce")
        Main_df["Days"] = numeric_days_pending
        Main_df.dropna(subset=["Days"], inplace=True)

        data = [
            {"Approver": "Director", "Approved.":Dir_Approved_request, "Value":Dir_Approved_value, "Pending": Dir_pending_request,"Rejected": Dir_rejecetd_request },
                {"Approver": "Projects", "Approved.":Pro_Approved_request, "Value":Pro_Approved_value , "Pending":Pro_pending_request,"Rejected": Pro_rejected_request },
                {"Approver": "Cordinator", "Approved.":Fac_Approved_request, "Value":Fac_Approved_value, "Pending":Fac_pending_request,"Rejected": Fac_rejected_request },
                {"Approver": "Operations", "Approved.":Ops_Approved_request, "Value":Ops_Approved_value, "Pending":Ops_pending_request ,"Rejected": Ops_rejecetd_request}
            # Add more records as needed
        ]
        New_df=pd.DataFrame(data)
        
        #st.write(New_df)
        
        # Creating a DataFrame
        Approval_df = pd.DataFrame(data)


        with card_container(key="Main1"):
            st.session_state.tab_clicked=True
            if Main_df is not None:
                cols = st.columns(4)
                with cols[0]:
                    ui.card(title="Total Request", content=Total_requests, key="Revcard10").render()
                with cols[1]:
                    ui.card(title="Closed Request", content=closed_request , key="Revcard11").render()
                with cols[2]:
                    ui.card(title="Pending Request", content=pending_request, key="Revcard12").render()
                with cols[3]:
                    ui.card(title="Approved Value:", content=Dir_Approved_value, key="Revcard13").render()                   
                with card_container(key="table2"):
                    cols = st.columns(2)
                    with cols[0]:
                        def get_month_options():
                            current_year = datetime.now().year
                            current_month = datetime.now().month
                            month_names = [
                                datetime(current_year, month, 1).strftime('%B')
                                for month in range(1, current_month + 1)
                            ]
                            month_names.insert(0, "Select Month")
                            return month_names
            
                        month_options = get_month_options()
                        
                        choice = ui.select(options=month_options)
                        
                        if "Choice" not in st.session_state:
                            st.session_state.choice=False
                            
                        if choice:
                            st.session_state.choice=True
                            with card_container(key="table1"):
                                def generate_sales_data():
                                    np.random.seed(0)  # For reproducible results
                                    Item = report_sum_df["Item"].apply(lambda x: x.split()[0]).tolist()
                                    Cost = report_sum_df["Cost"].tolist()
                                    return pd.DataFrame({'Item': Item, 'Cost': Cost})
                                with card_container(key="chart1"):
                                    st.vega_lite_chart(generate_sales_data(), {
                                        'title': 'Cost of Repairs -(Based on Approved Amount)',
                                        'mark': {'type': 'bar', 'tooltip': True, 'fill': 'black', 'cornerRadiusEnd': 4 },
                                        'encoding': {
                                            'x': {'field': 'Item', 'type': 'ordinal'},
                                            'y': {'field': 'Cost', 'type': 'quantitative', 'sort': '-x', 'axis': {'grid': False}},
                                        },
                                    }, use_container_width=True)
                            with card_container(key="table1"):
                                    ui.table(data=Approval_df, maxHeight=300)
                                
                            
            # Initialize the session state
            if 'toggle_value' not in st.session_state:
                st.session_state.toggle_value = False

            # Create a checkbox to toggle the value
            toggle_value = ui.switch(default_checked=st.session_state.toggle_value, label="Show Table", key="switch1")   

            # Store the value of the toggle in the session state
            st.session_state.toggle_value = toggle_value
            
            if "load_state" not in st.session_state:
                    st.session_state.load_state=False
                
            if toggle_value or st.session_state.load_state:
                st.session_state.load_state=True
                
                        
                with card_container(key="gallery1"):
                    
                    st.markdown('<div style="height: 0px; overflow-y: scroll;">', unsafe_allow_html=True)
                    @st.cache_resource
                    def load_data():
                            New = SharePoint().connect_to_list(ls_name='Maintenance Report')
                            return pd.DataFrame(  New )
                        
                    df_mainselected=load_data()
                    
                    data_df= df_mainselected[['ID','Date of report','Clinic','Department','Report','Amount on the Quotation','Approved amount','MainStatus','Approver','MonthName','LinkEdit']]
                    
                    # Convert 'bill_date' to datetime type
                    data_df['Date of report'] = pd.to_datetime(data_df['Date of report']).dt.date
                                        
                    # Extract just the month name
                    data_df['MonthName'] = data_df['MonthName'].str.split(';#').str[1]
                
                    data_df = data_df.rename(columns={
                        'ID': 'Ticket',
                        'Date of report':'Date',
                        'Clinic': 'Facility',
                        'Department':'Department',
                        'Report': 'Issue',
                        'Amount on the Quotation': 'Quoted Amount',
                        'Approved amount': 'Final Approved',
                        'MainStatus': 'Status',
                        'MonthName':'Month',
                        'Approver': 'Approver',
                        'LinkEdit': 'Link'
                    })
                    # Fill NaN/NA values with an empty string
                    
                    data_df.fillna('', inplace=True)
                    
                    # Define the columns to filter
                    filter_columns = ["Ticket", "Approver", "Facility","Issue","Status","Month"]

                    # Create five columnss for arranging widgets horizontally
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    
                    
                    # Create a dictionary to store filter values
                    filters = {column: '' for column in filter_columns}
                    

                    # Create text input widgets for each filter column and arrange them horizontally
                    with col1:
                        filters[filter_columns[0]] = st.text_input(f"Filter {filter_columns[0]}", filters[filter_columns[0]])
                    with col2:
                        filters[filter_columns[1]] = st.text_input(f"Filter {filter_columns[1]}", filters[filter_columns[1]])
                    with col3:
                        filters[filter_columns[2]] = st.text_input(f"Filter {filter_columns[2]}", filters[filter_columns[2]])
                    with col4:
                        filters[filter_columns[3]] = st.text_input(f"Filter {filter_columns[3]}", filters[filter_columns[3]])
                    with col5:
                        filters[filter_columns[4]] = st.text_input(f"Filter {filter_columns[4]}", filters[filter_columns[4]])
                    with col6:
                        filters[filter_columns[5]] = st.text_input(f"Filter {filter_columns[5]}", filters[filter_columns[5]])
                    # Apply filters to the DataFrame
                    filtered_df = data_df
                    for column, filter_value in filters.items():
                        if filter_value:
                            filtered_df = filtered_df[filtered_df[column].str.contains(filter_value, case=False)]

                    # Display the filtered DataFrame using st.data_editor
                    st.data_editor(
                        filtered_df,
                        column_config={
                            "Link": st.column_config.LinkColumn(
                                "Link",
                                display_text="View"
                            )
                        },
                        hide_index=True
                    )   
            
                
                
                                    
            metrics = [
                {"label": "Total", "value": Total_requests},
                {"label": "Closed", "value": closed_request},
                {"label": "Pending", "value": pending_request},
                {"label": "Value", "value": Total_Value}
            ]

            fig_data_cards = go.Figure()

            for i, metric in enumerate(metrics):
                fig_data_cards.add_trace(go.Indicator(
                    mode="number",
                    value=metric["value"],
                    number={'font': {'size': 25, 'color': 'white'}},
                    domain={'row': i, 'column': 0},
                    title={'text': metric["label"],'font': {'size': 20,'color': 'white'}},
                    align="center"
                ))

            fig_data_cards.update_layout(
                grid={'rows': len(metrics), 'columns': 1, 'pattern': "independent"},
                template="plotly_white",
                height=100*len(metrics),
                paper_bgcolor='rgba(0, 131, 184, 1)',
                plot_bgcolor='rgba(0, 137, 184, 1)',
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
