import mysql.connector
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from IPython.display import display
import calendar
import numpy as np
import plotly.express as px
from IPython.display import HTML
import streamlit as st
import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.lists.list import List
import pandas as pd
from datetime import datetime
import streamlit_option_menu as option_menu
import plotly.graph_objects as go
import os
from sqlalchemy import create_engine


# Set the page configuration
st.set_page_config(page_title="My Streamlit App", layout="wide")

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

        # Get all available columns dynamically
        columns = target_list.fields.get()
        ctx.load(columns)
        ctx.execute_query()

        # Extract column names
        column_names = [column.properties["StaticName"] for column in columns]

        # Convert all columns to a DataFrame
        data = []
        for item in items:
            item_data = {key: item.properties[key] for key in column_names}
            data.append(item_data)
        return pd.DataFrame(data)

    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def home():
    
    
    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up", "Log Out"]
        choice = st.sidebar.selectbox("", menu)

        form_container = st.empty()
        with form_container :
            sharepoint_url = "https://blissgvske.sharepoint.com/sites/BlissHealthcareReports"
            list_name_facilities = "Facility"
            list_name_credential = "Db_credential"

            # Hardcoded email and password
            email_user = "biosafety@blisshealthcare.co.ke"
            password_user = "NaSi#2024"

            #connection to SharePoint
            location_df  = load_data(email_user, password_user, sharepoint_url, list_name_facilities)
            
            st.write(location_df)