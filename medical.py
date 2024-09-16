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
from postgrest import APIError
from dateutil.relativedelta import relativedelta


def app():
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False 
        st.write(f"""<span style="color:red;">
                    You are not Logged in,click account to  Log in/Sign up to proceed.
                </span>""", unsafe_allow_html=True)
        
        # Initialize session state if it doesn't exist
                 
    if st.session_state.is_authenticated:
        location=st.session_state.Region
        region=st.session_state.Location
        location=st.session_state.Region
      
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
        
        
            #Get the previous month as a date
            previous_month_date = datetime.now() - relativedelta(months=1)

            
            current_month = datetime.now().month 
            current_month_name = datetime.now().strftime("%B")
            
            #current_month = datetime.now() - relativedelta(months=1)
            #current_month_name = (datetime.now() - relativedelta(months=1)).strftime("%B")
            

            # Query the MTD_Revenue table with the filter for location_name and Month
            response = supabase.from_('MTD_Revenue').select('*').eq('location_name', location).eq('Month', current_month_name ).execute()
            performance_df = pd.DataFrame(response.data)
            
            # Query the MTD_Revenue table with the filter for location_name and Month
            Allresponse = supabase.from_('MTD_Revenue').select('*').eq('location_name', location).execute()
            Allperformance_df = pd.DataFrame(Allresponse.data)
            
            
            Lastdateresponse = supabase.from_('Last_Update').select('*').execute()
            LastUpdate_df = pd.DataFrame(Lastdateresponse.data)
            LastUpdate_df = LastUpdate_df[['Last_Updated']]  # Assuming 'Last_Updated' is the column you want
            Lastdate = LastUpdate_df.iloc[0]['Last_Updated']
            
            Lastdate = LastUpdate_df.iloc[0]['Last_Updated']
            Lastdate_date = datetime.strptime(Lastdate, "%Y-%m-%d").date()
            
            
            # Convert Lastdate to a datetime.date object
            dateword = datetime.strptime(Lastdate, "%Y-%m-%d").date()

            # Format the date as "Friday 24th 2024"
            formatted_date = dateword.strftime("%A %dth %Y")


            with card_container(key="MTDclinic"):
                cols = st.columns(4)
                with cols[3]:
                   st.write(f"Last updated on {formatted_date}")

                # User inputs for location and month
                month=current_month_name

                # Construct the filtered Metabase URL
                metabase_url = f"http://localhost:3000/public/dashboard/628833d3-9b9e-411a-8d1c-6c6aea544e9b?region={region}&location={location}&month={month}"


                # Embed in Streamlit using iframe
                st.markdown(f"""
                    <iframe
                        src="{metabase_url}"
                        frameborder="0"
                        width="1300"
                        height="1000"
                        allowtransparency
                    ></iframe>
                """, unsafe_allow_html=True)
                                # Create a container for the iframe
                


               
    else:
       st.write("You  are  not  logged  in. Click   **[Account]**  on the  side  menu to Login  or  Signup  to proceed")



