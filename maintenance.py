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

    if st.session_state.is_authenticated or st.session_state.tab_clicked:
        st.session_state.is_authenticated = True
        st.session_state.tab_clicked = False
        ui.tabs(options=['PyGWalker', 'Graphic Walker', 'GWalkR', 'RATH'], default_value='PyGWalker', key="kanaries")
    else:
        st.session_state.is_authenticated = False  

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
        ui.badges(badge_list=[("shadcn", "default"), ("in", "secondary"), ("streamlit", "destructive")], class_name="flex gap-2", key="main_badges1")
        st.caption("A Streamlit component library for building beautiful apps easily. Bring the power of Shadcn UI to your Streamlit apps!")
        st.caption("Get started with pip install streamlit-shadcn-ui")


        with ui.element("div", className="flex gap-2", key="buttons_group1"):
            ui.element("button", text="Get Started", className="btn btn-primary", key="btn1")
            ui.element("link_button", text="Github", url="https://github.com/ObservedObserver/streamlit-shadcn-ui", variant="outline", key="btn2")

        st.subheader("Dashboard")

        ui.tabs(options=['Overview', 'Analytics', 'Reports', 'Notifications'], default_value='Overview', key="main_tabs")

        ui.date_picker(key="date_picker1")

        cols = st.columns(3)
        with cols[0]:
            # with ui.card():
            #     ui.element()
            ui.card(title="Total Revenue", content="$45,231.89", description="+20.1% from last month", key="card1").render()
        with cols[1]:
            ui.card(title="Subscriptions", content="+2350", description="+180.1% from last month", key="card2").render()
        with cols[2]:
            ui.card(title="Sales", content="+12,234", description="+19% from last month", key="card3").render()

        def generate_sales_data():
            np.random.seed(0)  # For reproducible results
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            sales = np.random.randint(1000, 5000, size=len(months))
            return pd.DataFrame({'Month': months, 'Sales': sales})

        with card_container(key="chart1"):
            st.vega_lite_chart(generate_sales_data(), {
                'mark': {'type': 'bar', 'tooltip': True, 'fill': 'rgb(173, 250, 29)', 'cornerRadiusEnd': 4 },
                'encoding': {
                    'x': {'field': 'Month', 'type': 'ordinal'},
                    'y': {'field': 'Sales', 'type': 'quantitative', 'axis': {'grid': False}},
                },
            }, use_container_width=True)

        # Sample data
        data = [
            {"invoice": "INV001", "paymentStatus": "Paid", "totalAmount": 500, "paymentMethod": "Credit Card"},
            {"invoice": "INV002", "paymentStatus": "Unpaid", "totalAmount": 200, "paymentMethod": "Cash"},
            {"invoice": "INV003", "paymentStatus": "Paid", "totalAmount": 150, "paymentMethod": "Debit Card"},
            {"invoice": "INV004", "paymentStatus": "Unpaid", "totalAmount": 350, "paymentMethod": "Credit Card"},
            {"invoice": "INV005", "paymentStatus": "Paid", "totalAmount": 400, "paymentMethod": "PayPal"},
            # Add more records as needed
        ]

        # Creating a DataFrame
        invoice_df = pd.DataFrame(data)

        with card_container(key="table1"):
            ui.table(data=invoice_df, maxHeight=300)


        ui_result = ui.button("Button", key="btn")
        st.write("UI Button Clicked:", ui_result)


        # Slider Component
        slider_value = slider(default_value=[20], min_value=0, max_value=100, step=2, label="Select a Range", key="slider1")
        st.write("Slider Value:", slider_value)

        # Input Component
        input_value = input(default_value="Hello, Streamlit!", type='text', placeholder="Enter text here", key="input1")
        st.write("Input Value:", input_value)

        # Textarea Component
        textarea_value = textarea(default_value="Type your message here...", placeholder="Enter longer text", key="textarea1")
        st.write("Textarea Value:", textarea_value)

        # Radio Group Component
        radio_options = [
            {"label": "Option A", "value": "A", "id": "r1"},
            {"label": "Option B", "value": "B", "id": "r2"},
            {"label": "Option C", "value": "C", "id": "r3"}
        ]
        radio_value = radio_group(options=radio_options, default_value="B", key="radio1")
        st.write("Selected Radio Option:", radio_value)

        # Switch Component
        switch_value = switch(default_checked=True, label="Toggle Switch", key="switch1")
        st.write("Switch is On:", switch_value)

        st.subheader("Alert Dialog")
        trigger_btn = ui.button(text="Trigger Button", key="trigger_btn")
        ui.alert_dialog(show=trigger_btn, title="Alert Dialog", description="This is an alert dialog", confirm_label="OK", cancel_label="Cancel", key="alert_dialog1")