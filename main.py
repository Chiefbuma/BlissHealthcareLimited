import streamlit as st
import streamlit_option_menu as option_menu
import Home, main, Regional, Maintenance, Departments, account
import mysql.connector
import pandas as pd

class MultipageApp:
    def __init__(self):
        self.apps = []
        self.selected_app = None

    def add_application(self, title, function):
        self.apps.append({
            "title": title,
            "function": function
        })

    def run(self):
        with st.sidebar:
            #st.image("Dashboard/logo.png", caption="Bliss Healthcare")
            app_name = option_menu.option_menu(
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
            st.session_state['app_name'] = app_name

        if st.session_state.get('app_name'):
            app_name = st.session_state['app_name']
            if app_name == "Maintenance Dashboard":
                Maintenance.app()
            elif app_name == "Medical centre Dashboard":
                Home.app()
            else:
                for app in self.apps:
                    if app_name == app["title"]:
                        app["function"]()

# Create an instance of the MultipageApp class
app = MultipageApp()

# Add applications to the MultipageApp
app.add_application("Medical centre Dashboard", Home.app)
app.add_application("Account", account.app)
app.add_application("Maintenance Dashboard", Maintenance.app)
app.add_application("Departments", Departments.app)

# Run the MultipageApp
app.run()
