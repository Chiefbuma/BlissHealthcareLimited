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
import main, region,medical,support,maintenance,Repair,Optical
# Set the page configuration
st.set_page_config(page_title="Bliss Healthcare limited", layout="wide")


class MultiApp:

    def __init__(self):
        self.apps = []

    def run():
        # app = st.sidebar(
        with st.sidebar: 
            app = option_menu.option_menu(key="main_key",
            menu_title='DASHBOARDS',
            options=['Account','Medical centre Dashboard', 'Region Dashboard','Summary Dashboard','Maintenance Dashboard','Optical orders' ],
            icons=['house-fill', 'receipt', 'receipt', 'receipt', 'receipt', 'person-circle'],
            menu_icon='house-fill',
            default_index=0,
            styles={
                "container": {"padding": "15", "background-color": {"grey": "black", "font-size": "10px"}},
                "nav-link": {"color": "Blck", "font-size": "13px", "text-align": "left"},
                "nav-link-selected": {"background-color": "Black"}
            }
        )       
            

        if app == "Medical centre Dashboard":
            medical.app()
        if app == "Region Dashboard":
            region.app()  
        if app == "Summary Dashboard":
            support.app()  
        if app == "Maintenance Dashboard":
           Repair.app()
        if app == "Account":
            main.app()    
        if app == "Optical orders":
            Optical.app()    
    

    run()            
        