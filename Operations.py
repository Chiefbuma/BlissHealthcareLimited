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
      
        @st.cache_resource
        def init_connection():
            url = "https://effdqrpabawzgqvugxup.supabase.co"
            key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmZmRxcnBhYmF3emdxdnVneHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA1MTQ1NDYsImV4cCI6MjAyNjA5MDU0Nn0.Dkxicm9oaLR5rm-SWlvGfV5OSZxFrim6x8-QNnc2Ua8"
            return create_client(url, key)

        supabase = init_connection()
        
        # Check if the connection is successful
        if init_connection():
            
            st.session_state.logged_in = True
            current_month = datetime.now().month 
            current_month_name = datetime.now().strftime("%B")
            
            # Query the MTD_Revenue table with the filter for location_name and Month
            response = supabase.from_('MTD_Revenue').select('*').eq('location_name', location).eq('Month', current_month_name).execute()
            performance_df = pd.DataFrame(response.data)
            
            Lastdateresponse = supabase.from_('Last_Update').select('*').execute()
            LastUpdate_df = pd.DataFrame(Lastdateresponse.data)
            LastUpdate_df = LastUpdate_df[['Last_Updated']]  
            Lastdate = LastUpdate_df.iloc[0]['Last_Updated']
          
            # Define the function to calculate the fraction of days passed in a month
            def fraction_of_days_in_month(date):
                total_days_in_month = (date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                fraction_passed = (date.day) / total_days_in_month.day
                return fraction_passed
           
            fraction_passed = fraction_of_days_in_month(datetime.strptime(Lastdate, "%Y-%m-%d").date())
            
            
            
            #iframe code with expanded width and centered alignment
            iframe_code = """
            <div style="display: flex; justify-content: center;">
                <iframe title="DASHBOARD - MTD | Summary" 
                        width="1100" 
                        height="700" 
                        src="https://app.powerbi.com/reportEmbed?reportId=16f6496e-6f9e-4b0c-8417-9291ff93938c&autoAuth=true&ctid=e2fcf853-8bfc-47b9-812f-359fb0a13c63&pageName=ReportSection8b673c123d2245457844&navContentPaneEnabled=false&filterPaneEnabled=false&bookmarkPaneEnabled=false&navigation=false" 
                        frameborder="0" 
                        allowFullScreen="true">
                </iframe>
            </div>
            """
            # Display the iframe in Streamlit
            st.markdown(iframe_code, unsafe_allow_html=True)

            with st.expander("YDT"):   
               
                iframe_code = """
                <div style="display: flex; justify-content: center;">
                    <iframe title="DASHBOARD - YTD | Summary" 
                            width="1100" 
                            height="700" 
                            src="https://app.powerbi.com/reportEmbed?reportId=16f6496e-6f9e-4b0c-8417-9291ff93938c&autoAuth=true&ctid=e2fcf853-8bfc-47b9-812f-359fb0a13c63&pageName=ReportSection0e8045cd64049172b21e&navContentPaneEnabled=false&filterPaneEnabled=false&bookmarkPaneEnabled=false&navigation=false" 
                            frameborder="0" 
                            allowFullScreen="true">
                    </iframe>
                </div>
                """
                # Display the iframe in Streamlit
                st.markdown(iframe_code, unsafe_allow_html=True)
        

    else:
        st.write("You are not logged in. Click **[Account]** on the side menu to Login or Signup to proceed")
