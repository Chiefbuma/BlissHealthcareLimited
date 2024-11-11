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
            url = "https://jxdfovectoeugyeixnnf.supabase.co"
            key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp4ZGZvdmVjdG9ldWd5ZWl4bm5mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzEzMDc3MTUsImV4cCI6MjA0Njg4MzcxNX0.eanuttDhkje4q43yyicxEEJMUnDO5aGaIyJYtKFUu3Y"
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
          
            # Define the function to calculate the fraction of days passed in a month
            def fraction_of_days_in_month(date):
                # Calculate the total number of days in the month
                total_days_in_month = (date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                # Calculate the fraction of days passed
                fraction_passed = (date.day) / total_days_in_month.day
                
                return fraction_passed
           
            # Create a new figure
            fig3 = go.Figure()
            
            # # Define the metrics
                        # Calculate the previous day
            Lastdate = LastUpdate_df.iloc[0]['Last_Updated']
            Lastdate_date = datetime.strptime(Lastdate, "%Y-%m-%d").date()
            
            # Convert Lastdate to a datetime.date object
            dateword = datetime.strptime(Lastdate, "%Y-%m-%d").date()

            # Format the date as "Friday 24th 2024"
            formatted_date = dateword.strftime("%A %dth %Y")

            # Calculate fraction of days passed for the selected month
            fraction_passed = fraction_of_days_in_month(Lastdate_date)
            
            with card_container(key="MTDREVENUE"):
                ui.card(
                content="DEPARTMENTAL",
                key="MCcard3"
            ).render()
          

                # Power BI embed URL
                embed_url = "https://app.powerbi.com/reportEmbed?reportId=902d5299-7684-421e-a96d-03158eba6a33&autoAuth=true&ctid=e2fcf853-8bfc-47b9-812f-359fb0a13c63"

                # Set the height for the iframe, width is set to 100% to make it responsive
                iframe_width = "100%"
                iframe_height = 1250  # You can adjust this as needed

                # HTML code to embed the Power BI report
                iframe_code = f'''
                <iframe width="{iframe_width}" height="{iframe_height}" src="{embed_url}" frameborder="0" allowFullScreen="true"></iframe>
                '''

                # Display the iframe in Streamlit
                st.markdown(iframe_code, unsafe_allow_html=True)


    else:
       st.write("You  are  not  logged  in. Click   **[Account]**  on the  side  menu to Login  or  Signup  to proceed")



