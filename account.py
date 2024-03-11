import mysql.connector
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from IPython.display import display
import calendar
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from IPython.display import HTML
import streamlit as st
import Home, main, Regional, Maintenance, Departments

def app():
    
    st.session_state.is_authenticated=False
    
    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up", "Log Out"]
        choice = st.sidebar.selectbox("", menu)

        form_container = st.empty()
        with form_container :
            host = '127.0.0.1'
            port = 3306
            database = 'blisshealthcare'
            user = 'root'
            password = 'buluma'

            # Connect to the MySQL server
            connection = mysql.connector.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                allow_local_infile=True
            )
            # Query to select all columns from the facilities table
            query = "SELECT * FROM facilities"

            # Load data into a DataFrame
            location_df = pd.read_sql(query, con=connection)

            cursor = connection.cursor()

            def create_usertable():
                cursor.execute('CREATE TABLE IF NOT EXISTS usertable (staff_id INT PRIMARY KEY AUTO_INCREMENT, staffnumber INT, password TEXT, location TEXT, region TEXT)')

            def add_userdata(staffnumber, password, location, region):
                cursor.execute('INSERT INTO usertable (staffnumber, password, location, region) VALUES (%s, %s, %s, %s)', (staffnumber, password, location, region))
                connection.commit()

            def get_facilities(staffnumber):
                query = "SELECT * FROM usertable WHERE staffnumber = %s"
                params = (staffnumber,)
                Login_df = pd.read_sql(query, params=params, con=connection)
                return Login_df

            def login_user(staffnumber, password):
                # Fetch location and region based on staffnumber
                facilities_df = get_facilities(staffnumber)

                if not facilities_df.empty:
                    location = facilities_df['location'].iloc[0]
                    region = facilities_df['region'].iloc[0]

                    # Check if the credentials match
                    cursor.execute('SELECT * FROM usertable WHERE staffnumber = %s AND password = %s', (staffnumber, password))
                    data = cursor.fetchall()
                    return data, location, region
                else:
                    return None, None, None

            def view_all_users():
                cursor.execute('SELECT * FROM usertable')
                data = cursor.fetchall()
                return data

            # Fetch locations from the database
            cursor.execute("SELECT Location FROM facilities")
            locations = cursor.fetchall()
            location_names = [location[0] for location in locations]

            # log in app
            if choice == "Log Out":
                st.subheader("Log Out")

            elif choice == "Login":
                with st.form("Login Form"):
                    st.write("Login Form")
                    staffnumber = st.text_input("Staffnumber")
                    password = st.text_input("Password", type='password')
                    # Fetch location and region based on staffnumber
                    facilities_df = get_facilities(staffnumber)
                    if not facilities_df.empty:
                        location = facilities_df['location'].iloc[0]
                        region = facilities_df['region'].iloc[0]
                    if st.form_submit_button("Login"):
                        create_usertable() 

                        result, location, region = login_user(staffnumber, password)
                        if result:
                            st.success("Logged In successfully")
                            st.write(f"Location: {location}, Region: {region}")
                            st.session_state.is_authenticated=True
                            form_container.empty()

                        else:
                            st.warning("Invalid credentials. Please try again.")

            elif choice == "Sign up":
                with st.form("Sign-up Form"):
                    st.write("Sign-up Form")
                    new_user = st.text_input("Staffnumber")
                    new_password = st.text_input("Password", type='password')
                    location = st.selectbox("Select Location", location_names)
                    selected_location_row = location_df[location_df['Location'] == location]
                    region = selected_location_row['Region'].iloc[0] if not selected_location_row.empty else None

                    if st.form_submit_button("Sign up"):
                        create_usertable()
                        add_userdata(new_user, new_password, location, region)
                        st.success("You have created a new account")
                        st.session_state.is_authenticated=True
                        form_container.empty()