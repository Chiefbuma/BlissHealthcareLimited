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
# The above code is using multi-line comments in Python, which are denoted by three consecutive pound
# signs (
            
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
            
            
            
            
            #Total_budget_FF = performance_df['Budget_Footfall'].sum()
            #formatted_FF_budget = "{:,.0f}".format(Total_budget_FF)
                        
            import pandas as pd
            import numpy as np
            
            

            # Assuming you have a DataFrame named 'sales_data' with 'patient_code' and 'bill_date' columns
            sales_data = pd.DataFrame({
                'patient_code': ['P001', 'P002', 'P003', 'P004'],
                'bill_date': pd.to_datetime(['2024-09-10', '2024-09-15', '2024-09-20', '2024-09-25'])
            })

            # Function to calculate week of the month
            def week_of_month(bill_date):
                # Start of the month
                start_month = bill_date - pd.offsets.MonthBegin()
                # Calculate the week number within the month (2: Monday as the first day of the week)
                week_num_in_month = (bill_date - start_month).days // 7 + 1
                return week_num_in_month

            # Add week of the month column to the DataFrame
            sales_data['WeekMonth'] = sales_data['bill_date'].apply(week_of_month)

            # Add month name for clarity
            sales_data['MonthName'] = sales_data['bill_date'].dt.strftime('%B')

            # Combine 'patient_code' and 'bill_date' to create 'WorkLoad'
            sales_data['WorkLoad'] = sales_data['patient_code'] + ' ' + sales_data['bill_date'].dt.strftime('%Y-%m-%d')

            # Display the result
            print(sales_data)

    else:
       st.write("You  are  not  logged  in. Click   **[Account]**  on the  side  menu to Login  or  Signup  to proceed")



