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

def app():
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False

    else:
        st.session_state.is_authenticated = False

    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False


    if not st.session_state.is_authenticated :
            form_container = st.empty()
            col1, col2 = st.columns([2,1])
            with col1:
               menu = ["Login", "Sign up"]
            choice = st.sidebar.selectbox("", menu,key="choice_medical")
            with form_container:
                @st.cache_resource
                def init_connection():
                    url = "https://effdqrpabawzgqvugxup.supabase.co"
                    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmZmRxcnBhYmF3emdxdnVneHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA1MTQ1NDYsImV4cCI6MjAyNjA5MDU0Nn0.Dkxicm9oaLR5rm-SWlvGfV5OSZxFrim6x8-QNnc2Ua8"
                    return create_client(url, key)

                supabase = init_connection()

                response = supabase.table('facilities').select("*").execute()

                location_df = pd.DataFrame(response.data)
                # st.write(location_df)

                def get_facilities(staffnumber):
                    response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
                    login_df = pd.DataFrame(response.data)
                    return login_df

                def add_userdata(staffnumber, password, location, region):
                    data = {
                        'staffnumber': staffnumber,
                        'password': password,
                        'location': location,
                        'region': region
                    }

                    _, count = supabase.table('users').insert(data).execute()
                    return count

                location_names = location_df['Location'].unique().tolist()

                def login_user(staffnumber,password):
                    try:
                        response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
                        user_data = response.data
                        facilities_df = get_facilities(staffnumber)
                        if not facilities_df.empty:
                            location = facilities_df['location'].iloc[0]
                            region = facilities_df['region'].iloc[0]

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
                    with st.form("Login Form"):
                        st.write("Login Form")
                        staffnumber = st.text_input("Staffnumber",key="staff_medical")
                        password = st.text_input("Password", type='password',key="pass_medical")
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
                           

    
    else:
         form_container.empty()
         
    if st.session_state.is_authenticated:
        form_container.empty()
        # get clients sharepoint list
       
        clients = SharePoint().connect_to_list(ls_name='Maintenance Report')

        # create DataFrame from clients list
        Main_df = pd.DataFrame(clients)

        st.write(Main_df)

        Total_requests = Main_df["ID"].nunique()
       
        pending_requests_calc =  Main_df [Main_df ["MainStatus"] == "Pending"]
        pending_request = int(pending_requests_calc.shape[0])

        closed_requests_calc =  Main_df [ Main_df ["MainStatus"] == "Closed"]
        closed_request = int(closed_requests_calc.shape[0])

        numeric_days_pending = Main_df["Days"].apply(pd.to_numeric, errors="coerce")
        Main_df["Days"] = numeric_days_pending
        Main_df.dropna(subset=["Days"], inplace=True)

        

        if st.session_state.is_authenticated or st.session_state.tab_clicked:
            st.session_state.tab_clicked=True
            st.session_state.is_authenticated=False
            with card_container(key="Main1"):
                st.session_state.tab_clicked=True
                ui.tabs(options=['PyGWalker', 'Graphic Walker', 'GWalkR', 'RATH'], default_value='PyGWalker', key="kanaries")
                if Main_df is not None:
                    cols = st.columns(4)
                    with cols[0]:
                        ui.card(title="Total Request", content=Total_requests, key="Revcard10").render()
                    with cols[1]:
                        ui.card(title="Closed Request", content=closed_request , key="Revcard11").render()
                    with cols[2]:
                        ui.card(title="Pending Request", content=pending_request , key="Revcard12").render()
                    with cols[3]:
                        ui.card(title="Average TAT:", content=pending_request, key="Revcard13").render()

                with st.expander("View Table"):
                    st.dataframe(Main_df, use_container_width=True)

                    metrics = [
                        {"label": "Total", "value": Total_requests},
                        {"label": "Closed", "value": closed_request},
                        {"label": "Pending", "value": pending_request},
                        {"label": "TAT(days)", "value": Average_Days_pending}
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
