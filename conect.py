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
import main
import region
import medical
import nyumbani
import Radiology
import Repair
import Finance
import Operations
import Optical
import TAT
# Set the page configuration
st.set_page_config(page_title="Bliss Healthcare limited", layout="wide")


class MultiApp:

    def __init__(self):
        self.apps = []

    def run():
        # app = st.sidebar(
        with st.sidebar:
            app = option_menu.option_menu(key="main_key",
                                          menu_title='DEPARTMENTS',
                                          options=[
                                              'Account', 'Medical centre', 'Region', 'Dawa Nyumbani',
                                              'Maintenance', 'Optical', 'Finance', 'Operations', 'TAT Report'
                                          ],
                                          icons=[
                                              'house-fill', 'receipt', 'receipt', 'receipt', 'receipt',
                                              'receipt', 'receipt', 'receipt', 'person-circle', 'receipt'
                                          ],
                                          menu_icon='house-fill',
                                          default_index=0,
                                          styles={
                                              "container": {"padding": "15", "background-color": {"grey": "black", "font-size": "10px"}},
                                              "nav-link": {"color": "Blck", "font-size": "13px", "text-align": "left"},
                                              "nav-link-selected": {"background-color": "Black"}
                                          }
                                          )

        if app == "Medical centre":
            medical.app()
        if app == "Region":
            region.app()
        if app == "Dawa Nyumbani":
            nyumbani.app()
        if app == "Maintenance":
            Repair.app()
        if app == "Optical":
            Optical.app()
        if app == "Account":
            main.app()
        if app == "Finance":
            Finance.app()
        if app == "Operations":
            Operations.app()
        if app == "TAT Report":
            TAT.app()

    run()
