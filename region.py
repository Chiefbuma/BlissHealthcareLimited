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


def app():
        
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False 
        # Initialize session state if it doesn't exist

   
    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up"]
        choice = st.sidebar.selectbox("", menu,key="choice_medical")

        form_container = st.empty()
        with form_container :
            @st.cache_resource
            def init_connection():
                url = "https://effdqrpabawzgqvugxup.supabase.co"
                key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmZmRxcnBhYmF3emdxdnVneHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA1MTQ1NDYsImV4cCI6MjAyNjA5MDU0Nn0.Dkxicm9oaLR5rm-SWlvGfV5OSZxFrim6x8-QNnc2Ua8"
                return create_client(url, key)

            supabase = init_connection()
            
            response = supabase.table('facilities').select("*").execute()
    
            location_df = pd.DataFrame(response.data)
            #st.write(location_df)


            def get_facilities(staffnumber):
                # Perform a Supabase query to fetch data from the 'users' table
                response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
                login_df = pd.DataFrame(response.data)
                return login_df

            def add_userdata(staffnumber, password, location, region):
                # Define the data to insert
                data = {
                    'staffnumber': staffnumber,
                    'password': password,
                    'location': location,
                    'region': region
                }

                # Insert the data into the 'userdata' table using Supabase
                _, count = supabase.table('users').insert(data).execute()

                # Return the count of rows affected by the insert operation
                return count

                # Return the count of rows affected by the insert operation
                return count

            location_names = location_df['Location'].unique().tolist()
                # Create a dictionary mapping each location to its region

            def login_user(staffnumber,password):
                
                try:
                    # Perform a Supabase query to fetch user data based on staff number
                    response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
                    user_data = response.data
                    facilities_df = get_facilities(staffnumber)
                    if not facilities_df.empty:
                        location = facilities_df['location'].iloc[0]
                        region = facilities_df['region'].iloc[0]
                        
                        
                        # Check if the credentials match
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
                # Check if the user is logged in
                
                with st.form("Login Form"):
                    st.write("Login Form")
                    staffnumber = st.text_input("Staffnumber",key="staff_medical")
                    password = st.text_input("Password", type='password',key="pass_medical")
                    # Fetch location and region based on staffnumber
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
                        form_container.empty()
                        
                        
                        
    if st.session_state.is_authenticated:
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
          
            
            current_month = datetime.now().month
            current_month_name = calendar.month_name[current_month]
            

            # Query the MTD_Revenue table with the filter for location_name and Month
            response = supabase.from_('MTD_Revenue').select('*').eq('Region', region).eq('Month', current_month_name ).execute()
            FinalMerged_df = pd.DataFrame(response.data)
            
            # Calculate MTD revenue and footfalls for the selected date range
            performance_df = FinalMerged_df.groupby(['Region', 'Scheme']).agg(
                MTD_Actual_Footfall=('MTD_Actual_Footfall', 'sum'),
                MTD_Budget_Footfall=('MTD_Budget_Footfall', 'sum'),
                Total_Revenue_Budget=('Total_Revenue_Budget', 'sum'),
                Total_Footfall_Budget=('Total_Footfall_Budget', 'sum'),
                Projected_Revenue=('Projected_Revenue', 'sum'),
                Projected_Footfalls=('Projected_Footfalls', 'sum'),
                MTD_Budget_Revenue=('MTD_Budget_Revenue', 'sum'),
                MTD_Actual_Revenue=('MTD_Actual_Revenue', 'sum')
            ).reset_index()

            # Query the MTD_Revenue table with the filter for location_name and Month
            Allresponse = supabase.from_('MTD_Revenue').select('*').eq('Region', region).execute()
            Allperformance_df = pd.DataFrame(Allresponse.data)
            
            # Calculate MTD revenue and footfalls for the selected date range
            MTDPerformance_df = Allperformance_df.groupby(['Region', 'Scheme','Month']).agg(
                MTD_Actual_Footfall=('MTD_Actual_Footfall', 'sum'),
                MTD_Budget_Footfall=('MTD_Budget_Footfall', 'sum'),
                Total_Revenue_Budget=('Total_Revenue_Budget', 'sum'),
                Total_Footfall_Budget=('Total_Footfall_Budget', 'sum'),
                Projected_Revenue=('Projected_Revenue', 'sum'),
                Projected_Footfalls=('Projected_Footfalls', 'sum'),
                MTD_Budget_Revenue =('MTD_Budget_Revenue', 'sum'),
                MTD_Actual_Revenue=('MTD_Actual_Revenue', 'sum')
            ).reset_index()
            
            
            
            # Query the MTD_Revenue table with the filter for location_name and Month
            REGresponse = supabase.from_('MTD_Region').select('*').eq('Region', region).execute()
            New_df = pd.DataFrame(REGresponse)
            
            # Calculate MTD revenue and footfalls for the selected date range
            REGperformance_df=   New_df.groupby(['Region', 'Scheme','Month']).agg(
                MTD_Actual_Footfall=('MTD_Actual_Footfall', 'sum'),
                MTD_Budget_Footfall=('MTD_Budget_Footfall', 'sum'),
                Total_Revenue_Budget=('Total_Revenue_Budget', 'sum'),
                Total_Footfall_Budget=('Total_Footfall_Budget', 'sum'),
                Projected_Revenue=('Projected_Revenue', 'sum'),
                Projected_Footfalls=('Projected_Footfalls', 'sum'),
                MTD_Budget_Revenue =('MTD_Budget_Revenue', 'sum'),
                MTD_Actual_Revenue=('MTD_Actual_Revenue', 'sum')
            ).reset_index()
            
            
            # Calculate MTD revenue and footfalls for the selected date range
            NewDPerformance_df = Allperformance_df.groupby(['Scheme','Month']).agg(
                MTD_Actual_Footfall=('MTD_Actual_Footfall', 'sum'),
                MTD_Budget_Footfall=('MTD_Budget_Footfall', 'sum'),
                Total_Revenue_Budget=('Total_Revenue_Budget', 'sum'),
                Total_Footfall_Budget=('Total_Footfall_Budget', 'sum'),
                Projected_Revenue=('Projected_Revenue', 'sum'),
                Projected_Footfalls=('Projected_Footfalls', 'sum'),
                MTD_Budget_Revenue=('MTD_Budget_Revenue', 'sum'),
                MTD_Actual_Revenue=('MTD_Actual_Revenue', 'sum')
            ).reset_index()
            
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
                           
            # For example, let's say you want to add a trace for the "Projection" metric
            fig3.update_layout(
                template="plotly_white",
                height=80,
                font_family="TimesNew Roman",
                width=100,
                paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                uniformtext=dict(minsize=40, mode='hide'),
                margin=dict(l=20, r=20, t=50, b=5)
                )
            
                        # Create a new figure
            fig2 = go.Figure()
            
            
            MTD_Revenue_budget = performance_df['MTD_Budget_Revenue'].sum()*fraction_passed
            formatted_Rev_budget = "{:,.0f}".format(MTD_Revenue_budget)
            
            # # Define the Reveneu metrics
            MTD_Actual_Revenue = performance_df['MTD_Actual_Revenue'].sum()
            formatted_Actual_revenue = "{:,.0f}".format(MTD_Actual_Revenue)
            
            Total_Budget_Reveneu = performance_df['Total_Revenue_Budget'].sum()
            formatted_Total_revenue = "{:,.0f}".format(Total_Budget_Reveneu)
            
            Arch_Rev = (MTD_Actual_Revenue /MTD_Revenue_budget) * 100
            formatted_arch_rev = "{:.2f}%".format(Arch_Rev)
            
            projected_revenue =performance_df['Total_Revenue_Budget'].sum()*(performance_df['MTD_Actual_Revenue'].sum()/(performance_df['MTD_Budget_Revenue'].sum()*fraction_passed))
            formatted_projected_reveue = "{:,.0f}".format(projected_revenue )
                        
            MTD_footfall_budget = performance_df['MTD_Budget_Footfall'].sum()*fraction_passed
            formatted_ff_budget = "{:,.0f}".format(   MTD_footfall_budget)
            # # Define the Reveneu metrics
            MTD_Actual_Footfall = performance_df['MTD_Actual_Footfall'].sum()
            formatted_Actual_footfall = "{:,.0f}".format(MTD_Actual_Footfall)
            
            Total_Budget_Footfall = performance_df['Total_Footfall_Budget'].sum()
            formatted_Total_footfall = "{:,.0f}".format(Total_Budget_Footfall)
            
            projected_Footfall = performance_df['Total_Footfall_Budget'].sum()*(performance_df['MTD_Actual_Footfall'].sum()/(performance_df['MTD_Budget_Footfall'].sum()*fraction_passed))
            formatted_projected_footfall = "{:,.0f}".format(projected_Footfall )
            
            Arch_Rev = (MTD_Actual_Footfall/MTD_footfall_budget) * 100
            formatted_arch_ff = "{:.2f}%".format(Arch_Rev)
            
           
            
            #ALL MONTHS 
            
            # Create a dropdown selectbox for searching
            
            # # Define Footfalls  metrics
            #Total_footfalls = performance_df['Footfall'].sum()
            #formatted_total_footfalls = "{:,.0f}".format(Total_footfalls)
            #Arch_FF = performance_df['%Arch_FF'].mean() * 100
            #formatted_arch_ff = "{:.0f}%".format( Arch_FF)
            
            
            # For example, let's say you want to add a trace for the "Projection" metric
            fig2.update_layout(
                template="plotly_white",
                height=80,
                font_family="TimesNew Roman",
                width=100,
                paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                uniformtext=dict(minsize=40, mode='hide'),
                margin=dict(l=20, r=20, t=50, b=5)
                )
            
            
            
            # For example, let's say you want to add a trace for the "Projection" metric
            fig3.update_layout(
                template="plotly_white",
                height=80,
                font_family="TimesNew Roman",
                width=100,
                paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                uniformtext=dict(minsize=40, mode='hide'),
                margin=dict(l=20, r=20, t=50, b=5)
                )
            
            # Create a new figure
             #fig6.add_trace(
             #go.Indicator(
                 #title={'text': "MTD FOOTFALL",'font': {'size': 15,'color': 'green'}},
                 #value= int(Total_budget)
            # For example, let's say you want to add a trace for the "Projection" metric
            #fig6.update_layout(
                #template="plotly_white",
                #height=80,
                #font_family="TimesNew Roman",
               # width=100,
                #paper_bgcolor='rgba(209, 255, 119, 0.1)',  # Set background color to transparent
                #plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                #uniformtext=dict(minsize=40, mode='hide'),
                #margin=dict(l=20, r=20, t=50, b=5)
                
            # The above code is formatting the columns in a DataFrame called `performance_df`. It is
            # applying specific formatting to the numerical values in the columns to make them more
            # readable and presentable.
            performance_df['MTD_Budget_Revenue'] = (performance_df['MTD_Budget_Revenue'] * fraction_passed).round(0)

            performance_df['MTD_Budget_Footfall']=(performance_df['MTD_Budget_Footfall']*fraction_passed).round(0)
            # Add a new column %Arch_FF as the percentage of MTD_Actual_Footfall to MTD_Budget_Footfall
            performance_df['%Arch_FF'] = (performance_df['MTD_Actual_Footfall'] / performance_df['MTD_Budget_Footfall'])
            # Add a new column %Arch_REV as the percentage of MTD_Actual_Revenue to MTD_Budget_Revenue
            performance_df['%Arch_REV'] = (performance_df['MTD_Actual_Revenue'] / performance_df['MTD_Budget_Revenue'])
                        
            performance_df['Projected_Footfalls']=(performance_df['Total_Footfall_Budget'] ) * (performance_df['MTD_Actual_Footfall'] / performance_df['MTD_Budget_Footfall'])           
            performance_df['Projected_Revenue']=(performance_df['Total_Revenue_Budget'] ) * (performance_df['MTD_Actual_Revenue'] / performance_df['MTD_Budget_Revenue'])           
            
            
            
            performance_df["MTD_Budget_Revenue"] = performance_df["MTD_Budget_Revenue"].apply(lambda x: '{:,.0f}'.format(x))
            performance_df["MTD_Actual_Revenue"] = performance_df["MTD_Actual_Revenue"].apply(lambda x: '{:,}'.format(x))
            performance_df["%Arch_REV"] = performance_df["%Arch_REV"].apply(lambda x: '{:.1f}%'.format(x*100 ))
            performance_df["Total_Revenue_Budget"] = performance_df["Total_Revenue_Budget"].apply(lambda x: '{:,.0f}'.format(x))
            performance_df["Projected_Revenue"] = performance_df["Projected_Revenue"].apply(lambda x: '{:,.0f}'.format(x))
            performance_df["MTD_Actual_Footfall"] = performance_df["MTD_Actual_Footfall"].apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Budget_Footfall"] = performance_df["MTD_Budget_Footfall"].apply(lambda x: '{:,.0f}'.format(x))
            performance_df["%Arch_FF"] = performance_df["%Arch_FF"].apply(lambda x: '{:.1f}%'.format(x*100))
            performance_df["Total_Footfall_Budget"] = performance_df["Total_Footfall_Budget"].apply(lambda x: '{:,}'.format(x))
            performance_df["Projected_Footfalls"] = performance_df["Projected_Footfalls"].apply(lambda x: '{:,.0f}'.format(x))
            
            
            MTDPerformance_df['MTD_Budget_Revenue'] = (MTDPerformance_df['MTD_Budget_Revenue'] * fraction_passed).round(0)

            MTDPerformance_df['MTD_Budget_Footfall'] = (MTDPerformance_df['MTD_Budget_Footfall']*fraction_passed).round(0)

            # Add a new column %Arch_FF as the percentage of MTD_Actual_Footfall to MTD_Budget_Footfall
            MTDPerformance_df['%Arch_FF'] = (MTDPerformance_df['MTD_Actual_Footfall'] / MTDPerformance_df['MTD_Budget_Footfall'])

            # Add a new column %Arch_REV as the percentage of MTD_Actual_Revenue to MTD_Budget_Revenue
            MTDPerformance_df['%Arch_REV'] = (MTDPerformance_df['MTD_Actual_Revenue'] / MTDPerformance_df['MTD_Budget_Revenue'])

            MTDPerformance_df['Projected_Footfalls'] = (MTDPerformance_df['Total_Footfall_Budget'] ) * (MTDPerformance_df['MTD_Actual_Footfall'] / MTDPerformance_df['MTD_Budget_Footfall'])           
            MTDPerformance_df['Projected_Revenue'] = (MTDPerformance_df['Total_Revenue_Budget'] ) * (MTDPerformance_df['MTD_Actual_Revenue'] / MTDPerformance_df['MTD_Budget_Revenue'])           

            MTDPerformance_df["MTD_Budget_Revenue"] = MTDPerformance_df["MTD_Budget_Revenue"].apply(lambda x: '{:,.0f}'.format(x))
            MTDPerformance_df["MTD_Actual_Revenue"] = MTDPerformance_df["MTD_Actual_Revenue"].apply(lambda x: '{:,}'.format(x))
            MTDPerformance_df["%Arch_REV"] = MTDPerformance_df["%Arch_REV"].apply(lambda x: '{:.1f}%'.format(x*100))
            MTDPerformance_df["Total_Revenue_Budget"] = MTDPerformance_df["Total_Revenue_Budget"].apply(lambda x: '{:,.0f}'.format(x))
            MTDPerformance_df["Projected_Revenue"] = MTDPerformance_df["Projected_Revenue"].apply(lambda x: '{:,.0f}'.format(x))
            MTDPerformance_df["MTD_Actual_Footfall"] = MTDPerformance_df["MTD_Actual_Footfall"].apply(lambda x: '{:,}'.format(x))
            MTDPerformance_df["MTD_Budget_Footfall"] = MTDPerformance_df["MTD_Budget_Footfall"].apply(lambda x: '{:,.0f}'.format(x))
            MTDPerformance_df["%Arch_FF"] = MTDPerformance_df["%Arch_FF"].apply(lambda x: '{:.1f}%'.format(x*100))
            MTDPerformance_df["Total_Footfall_Budget"] = MTDPerformance_df["Total_Footfall_Budget"].apply(lambda x: '{:,}'.format(x))
            MTDPerformance_df["Projected_Footfalls"] = MTDPerformance_df["Projected_Footfalls"].apply(lambda x: '{:,.0f}'.format(x))
            
            
            
            
            NewDPerformance_df['MTD_Budget_Revenue'] = (NewDPerformance_df['MTD_Budget_Revenue'] * fraction_passed).round(0)

            NewDPerformance_df['MTD_Budget_Footfall'] = (NewDPerformance_df['MTD_Budget_Footfall']*fraction_passed).round(0)

            # Add a new column %Arch_FF as the percentage of MTD_Actual_Footfall to MTD_Budget_Footfall
            NewDPerformance_df['%Arch_FF'] = (NewDPerformance_df['MTD_Actual_Footfall'] / NewDPerformance_df['MTD_Budget_Footfall'])

            # Add a new column %Arch_REV as the percentage of MTD_Actual_Revenue to MTD_Budget_Revenue
            NewDPerformance_df['%Arch_REV'] = (NewDPerformance_df['MTD_Actual_Revenue'] / NewDPerformance_df['MTD_Budget_Revenue'])

            NewDPerformance_df['Projected_Footfalls'] = (NewDPerformance_df['Total_Footfall_Budget'] ) * (NewDPerformance_df['MTD_Actual_Footfall'] / NewDPerformance_df['MTD_Budget_Footfall'])           
            NewDPerformance_df['Projected_Revenue'] = (NewDPerformance_df['Total_Revenue_Budget'] ) * (NewDPerformance_df['MTD_Actual_Revenue'] / NewDPerformance_df['MTD_Budget_Revenue'])           

            NewDPerformance_df["MTD_Budget_Revenue"] = NewDPerformance_df["MTD_Budget_Revenue"].apply(lambda x: '{:,.0f}'.format(x))
            NewDPerformance_df["MTD_Actual_Revenue"] = NewDPerformance_df["MTD_Actual_Revenue"].apply(lambda x: '{:,}'.format(x))
            NewDPerformance_df["%Arch_REV"] = NewDPerformance_df["%Arch_REV"].apply(lambda x: '{:.1f}%'.format(x*100))
            NewDPerformance_df["Total_Revenue_Budget"] = NewDPerformance_df["Total_Revenue_Budget"].apply(lambda x: '{:,.0f}'.format(x))
            NewDPerformance_df["Projected_Revenue"] = NewDPerformance_df["Projected_Revenue"].apply(lambda x: '{:,.0f}'.format(x))
            NewDPerformance_df["MTD_Actual_Footfall"] = NewDPerformance_df["MTD_Actual_Footfall"].apply(lambda x: '{:,}'.format(x))
            NewDPerformance_df["MTD_Budget_Footfall"] = NewDPerformance_df["MTD_Budget_Footfall"].apply(lambda x: '{:,.0f}'.format(x))
            NewDPerformance_df["%Arch_FF"] = NewDPerformance_df["%Arch_FF"].apply(lambda x: '{:.1f}%'.format(x*100))
            NewDPerformance_df["Total_Footfall_Budget"] = NewDPerformance_df["Total_Footfall_Budget"].apply(lambda x: '{:,}'.format(x))
            NewDPerformance_df["Projected_Footfalls"] = NewDPerformance_df["Projected_Footfalls"].apply(lambda x: '{:,.0f}'.format(x))

            
            
            REGperformance_df['MTD_Budget_Revenue'] = (REGperformance_df['MTD_Budget_Revenue'] * fraction_passed).round(0)

            REGperformance_df['MTD_Budget_Footfall'] = (REGperformance_df['MTD_Budget_Footfall']*fraction_passed).round(0)

            # Add a new column %Arch_FF as the percentage of MTD_Actual_Footfall to MTD_Budget_Footfall
            REGperformance_df['%Arch_FF'] = (REGperformance_df['MTD_Actual_Footfall'] / REGperformance_df['MTD_Budget_Footfall'])

            # Add a new column %Arch_REV as the percentage of MTD_Actual_Revenue to MTD_Budget_Revenue
            REGperformance_df['%Arch_REV'] = (REGperformance_df['MTD_Actual_Revenue'] / REGperformance_df['MTD_Budget_Revenue'])

            REGperformance_df['Projected_Footfalls'] = (REGperformance_df['Total_Footfall_Budget'] ) * (REGperformance_df['MTD_Actual_Footfall'] / REGperformance_df['MTD_Budget_Footfall'])           
            REGperformance_df['Projected_Revenue'] = (REGperformance_df['Total_Revenue_Budget'] ) * (REGperformance_df['MTD_Actual_Revenue'] / REGperformance_df['MTD_Budget_Revenue'])           

            REGperformance_df["MTD_Budget_Revenue"] = REGperformance_df["MTD_Budget_Revenue"].apply(lambda x: '{:,.0f}'.format(x))
            REGperformance_df["MTD_Actual_Revenue"] = REGperformance_df["MTD_Actual_Revenue"].apply(lambda x: '{:,}'.format(x))
            REGperformance_df["%Arch_REV"] = REGperformance_df["%Arch_REV"].apply(lambda x: '{:.1f}%'.format(x*100))
            REGperformance_df["Total_Revenue_Budget"] = REGperformance_df["Total_Revenue_Budget"].apply(lambda x: '{:,.0f}'.format(x))
            REGperformance_df["Projected_Revenue"] = REGperformance_df["Projected_Revenue"].apply(lambda x: '{:,.0f}'.format(x))
            REGperformance_df["MTD_Actual_Footfall"] = REGperformance_df["MTD_Actual_Footfall"].apply(lambda x: '{:,}'.format(x))
            REGperformance_df["MTD_Budget_Footfall"] = REGperformance_df["MTD_Budget_Footfall"].apply(lambda x: '{:,.0f}'.format(x))
            REGperformance_df["%Arch_FF"] = REGperformance_df["%Arch_FF"].apply(lambda x: '{:.1f}%'.format(x*100))
            REGperformance_df["Total_Footfall_Budget"] = REGperformance_df["Total_Footfall_Budget"].apply(lambda x: '{:,}'.format(x))
            REGperformance_df["Projected_Footfalls"] = REGperformance_df["Projected_Footfalls"].apply(lambda x: '{:,.0f}'.format(x))
            
            
              # Rearrange the columns
            MTD_All =  MTDPerformance_df[
                [ 'Month','Region','Scheme','MTD_Budget_Revenue', 'MTD_Actual_Revenue', '%Arch_REV','Total_Revenue_Budget', 'Projected_Revenue','MTD_Actual_Footfall', 'MTD_Budget_Footfall', '%Arch_FF', 'Total_Footfall_Budget','Projected_Footfalls']
            ]
            
            #ALL MONRH DATA
            
            
            # Rearrange the columns
            Monthly_All = Allperformance_df[
                [ 'Month','Region','Scheme', 'MTD_Budget_Revenue', 'MTD_Actual_Revenue', '%Arch_REV','Total_Revenue_Budget', 'Projected_Revenue','MTD_Actual_Footfall', 'MTD_Budget_Footfall', '%Arch_FF', 'Total_Footfall_Budget','Projected_Footfalls']
            ]
            
            
            
           # Calculate the total values for each column
            total_values = {
                'Scheme': 'TOTAL',
                'MTD_Budget_Revenue': formatted_Rev_budget ,
                'MTD_Actual_Revenue': formatted_Actual_revenue,
                '%Arch_REV': formatted_arch_rev,
                'Total_Revenue_Budget': formatted_Total_revenue,
                'Projected_Revenue': formatted_projected_reveue,
                'MTD_Budget_Footfall': formatted_ff_budget,
                'MTD_Actual_Footfall': formatted_Actual_footfall,
                '%Arch_FF': formatted_arch_ff,
                'Total_Footfall_Budget': formatted_Total_footfall,
                'Projected_Footfalls':formatted_projected_footfall
}
                            # Create a DataFrame for the total row
            total_row_df = pd.DataFrame(total_values, index=[0])

                # Concatenate the total row with performance_df
            performance_total = pd.concat([performance_df, total_row_df], ignore_index=True)

            
            
            fig_request_by_type_Rev = go.Figure(data=[go.Table(
                header=dict(values=['Scheme','Revenue<br>Budget','Revenue<br>Actual','%Arch<br>REV',
                                    'Total<br>Budget','Projected<br>Revenue',
                                    'Footfall<br>Budget','Footfall<br>Actual','%Arch<br>FF','Total<br>Budget','Projected<br>Footfalls'],
                            fill_color='rgba(0, 84, 0, 1)',
                            align='left',
                            font=dict(family='Garamond', color='White', size=14),
                            line_color='darkslategray',  # Border color
                            line=dict(width=1)),
                            columnwidth=[40, 30, 30,30, 30, 30, 30, 30, 30, 30,40],# Border width
                cells=dict(values=[performance_total["Scheme"],
                                   performance_total["MTD_Budget_Revenue"],
                                   performance_total["MTD_Actual_Revenue"],
                                   performance_total["%Arch_REV"],
                                    performance_total["Total_Revenue_Budget"],
                                    performance_total["Projected_Revenue"],
                                     performance_total["MTD_Budget_Footfall"],
                                    performance_total["MTD_Actual_Footfall"],
                                    performance_total["%Arch_FF"],
                                    performance_total["Total_Footfall_Budget"],
                                    performance_total["Projected_Footfalls"]]
                        ,
                        
                

                        fill_color = ['rgba(0, 0, 82, 1)']+ ['white']+ ['white']+ ['white']+ ['white']+ ['white']+ ['lightgrey'] * (len(performance_total) - 5)
,
                        font_color=[
                                ['white'],  # Blue for "Report" column
                                ['black'] * len(performance_total)  # White for "Count" column
                            ],
                        align='left',
                        font=dict(color='black', size=14),
                        line_color='darkslategray',
                        height=25,# Border color
                        line=dict(width=0.3))),
                       
            ])
            fig_request_by_type_Rev.update_layout(
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=200,
                    width=1000,# Set all margins to 0
                    paper_bgcolor='rgba(0, 0, 0, 0)', 
                    # Set paper background color to transparent
                )
            
            
            # The above code is formatting the columns in a DataFrame called `performance_df`. It is
            # applying specific formatting to the numerical values in the columns to make them more
            # readable and presentable.
            
            
            
            def generate_sales_data():
                np.random.seed(0)  # For reproducible results
                months = ['Jan', 'Feb', 'Mar']
                sales = np.random.randint(1000, 5000, size=len(months))
                return pd.DataFrame({'Month': months, 'Sales': sales})
            
            with card_container(key="MTDREVENUE"):
                card_style3 = "border: 2px solid #000000; border-radius: 5px; padding: 10px; background-color:#ffffff; color:#000000; text-align: center; font-size: 15px;font-weight: bold; width: 100%; height: 30;"
                ui.card(
                    content="Region:" + region,
                    key="MCcard3"
                ).render()

                cols = st.columns(4)
                with cols[0]:
                    ui.card(title="MTD Revenue", content=formatted_Actual_revenue, key="Revcard1").render()
                with cols[1]:
                    ui.card(title="MTD Budget", content=formatted_Rev_budget, key="Revcard2").render()
                with cols[2]:
                    ui.card(title="MTD Archievement", content=formatted_arch_rev, key="Revcard3").render()
                with cols[3]:
                    ui.card(title="Last Updated on:", content=formatted_date, key="Revcard4").render()  
                st.plotly_chart(fig_request_by_type_Rev, use_container_width=True)
                
                with st.expander("DOWNLOAD PREVIOUS MONTH"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        
                        current_month = datetime.now().month
                        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][:current_month]
                            # Create a list of months up to the previous month
                        display_months = months[:current_month - 1]

                        # Set the default value to the previous month
                        default_month_index = current_month - 1  #   
                        
                        Month = st.selectbox("Select Month", [""] + display_months, index=default_month_index,key="Allmonth") 
                        if Month == "":
                            Newfiltered_df = performance_total
                        else:
                            Newfiltered_df =REGperformance_df.query("`Month` == @Month")

                    st.write(Newfiltered_df, use_container_width=True)   
           
                
                with st.expander("DOWNLOAD MEDICAL CENTRES-click the download icon on the upper right corner of the table"):
                    
                    Allperformance_df["MTD_Budget_Revenue"] = Allperformance_df["MTD_Budget_Revenue"].apply(lambda x: '{:,}'.format(x))
                    Allperformance_df["MTD_Actual_Revenue"] = Allperformance_df["MTD_Actual_Revenue"].apply(lambda x: '{:,}'.format(x))
                    Allperformance_df["%Arch_REV"] = Allperformance_df["%Arch_REV"].apply(lambda x: '{:.1f}%'.format(x))
                    Allperformance_df["Total_Revenue_Budget"] = Allperformance_df["Total_Revenue_Budget"].apply(lambda x: '{:,}'.format(x))
                    Allperformance_df["Projected_Revenue"] = Allperformance_df["Projected_Revenue"].apply(lambda x: '{:,}'.format(x))
                    Allperformance_df["MTD_Actual_Footfall"] = Allperformance_df["MTD_Actual_Footfall"].apply(lambda x: '{:,}'.format(x))
                    Allperformance_df["MTD_Budget_Footfall"] = Allperformance_df["MTD_Budget_Footfall"].apply(lambda x: '{:,}'.format(x))
                    Allperformance_df["%Arch_FF"] = Allperformance_df["%Arch_FF"].apply(lambda x: '{:.1f}%'.format(x/100))
                    Allperformance_df["Total_Footfall_Budget"] = Allperformance_df["Total_Footfall_Budget"].apply(lambda x: '{:,}'.format(x))
                    Allperformance_df["Projected_Footfalls"] = Allperformance_df["Projected_Footfalls"].apply(lambda x: '{:,}'.format(x))

                    col1, col2, col3 = st.columns(3)
            
                    st.markdown("""<style>
                    div.st.container > button:first-child {
                        background-color: #00cc00;
                        color: white;
                        font-size: 20px;
                        height: 3em;
                        width: 30em;
                        border-radius: 10px;
                    }
                    </style>""", unsafe_allow_html=True)

                
                    Region = region
                    
                    Region_location_names = location_df[location_df['Region'] == region]['Location'].unique().tolist()

                    
                    current_month = datetime.now().month
                    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][:current_month]
                    # Create a list of months up to the previous month
                    display_months = months[:current_month - 1]

                    # Set the default value to the previous month
                    default_month_index = current_month - 1  #
    
                    with col1:
                        location = st.selectbox("Select Location", [""] +  Region_location_names)
                    with col2:
                        Month = st.selectbox("Select Month", [""] + display_months, index=default_month_index,key="MTDmonth") 
                    if Month == "" or location =="":
                        filtered_df = MTD_All
                    else:
                        filtered_df = Monthly_All.query("`Month` == @Month and `location_name` == @location")
                        
  
                    st.write(filtered_df, use_container_width=True)
                    
                
                        
                
        
        # Use the expander widget
        #with st.expander("MONTHWISE REVENUE SUMMARY TABLE"):
            # Set the height of the expander
            #st.write(RR_pivot_Actual, use_container_width=True)
            #st.write(FF_pivot_Actual, use_container_width=True)
        form_container.empty()


