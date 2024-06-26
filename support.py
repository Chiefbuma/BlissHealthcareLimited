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
        
    if " choice" not in st.session_state:
        st.session_state.choice=False
        
    if "form_container" not in st.session_state:
        st.session_state.form_container=False  
   
    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up"]
        
        choice = st.sidebar.selectbox("", menu,key="choice_medical")

        
        
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
 
        form_container=st.container(border=False)
        
        
        if choice == "Login":
            st.session_state.choice=True
            st.session_state.form_container=True
            # Check if the user is logged in
            
            with form_container:  
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
            st.session_state.choice=True
            st.session_state.form_container=True
            
            
            with form_container: 
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
        st.session_state.choice=False
        st.session_state.form_container=False
        
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
            

            response = supabase.from_('MTD_Overall').select('*').eq('Month', current_month_name ).execute()
            performance_df = pd.DataFrame(response.data)

            
            Regionresponse = supabase.from_('MTD_RegionALL').select('*').eq('Month', current_month_name ).execute()
            Regionperformance_df = pd.DataFrame(Regionresponse.data)
            
            
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
            
            
            
                      # # Define the Reveneu metrics
            AllMTD_Actual_Revenue = Regionperformance_df['MTD_Actual_Revenue'].sum()
            formatted_Actual_revenue = "{:,.0f}".format(AllMTD_Actual_Revenue)
            
            AllTotal_Budget_Reveneu = Regionperformance_df['Total_Revenue_Budget'].sum()
            formatted_Total_revenue = "{:,.0f}".format(AllTotal_Budget_Reveneu)
            
            AllArch_Rev = (MTD_Actual_Revenue /MTD_Revenue_budget) * 100
            formatted_arch_rev = "{:.2f}%".format(AllArch_Rev)
            # It looks like the code is a comment in Python. Comments in Python start with a hash
            # symbol (#) and are used to provide explanations or notes within the code. In this case,
            # the comment appears to say "projecte".
            
            projected_revenue =Regionperformance_df['Total_Revenue_Budget'].sum()*(Regionperformance_df['MTD_Actual_Revenue'].sum()/(Regionperformance_df['MTD_Budget_Revenue'].sum()*fraction_passed))
            formatted_projected_reveue = "{:,.0f}".format(projected_revenue )
            
            
            MTD_footfall_budget = Regionperformance_df['MTD_Budget_Footfall'].sum()*fraction_passed
            formatted_ff_budget = "{:,.0f}".format(   MTD_footfall_budget)
            # # Define the Reveneu metrics
            MTD_Actual_Footfall = Regionperformance_df['MTD_Actual_Footfall'].sum()
            formatted_Actual_footfall = "{:,.0f}".format(MTD_Actual_Footfall)
            
            Total_Budget_Footfall = Regionperformance_df['Total_Footfall_Budget'].sum()
            formatted_Total_footfall = "{:,.0f}".format(Total_Budget_Footfall)
            
            projected_Footfall = Regionperformance_df['Total_Footfall_Budget'].sum()*(Regionperformance_df['MTD_Actual_Footfall'].sum()/(performance_df['MTD_Budget_Footfall'].sum()*fraction_passed))
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
            
            performance_df["MTD_Budget_Revenue"] = performance_df["MTD_Budget_Revenue"].fillna(0).astype(int).apply(lambda x: '{:,.0f}'.format(x))
            performance_df["MTD_Actual_Revenue"] = performance_df["MTD_Actual_Revenue"].fillna(0).astype(int).apply(lambda x: '{:,}'.format(x))
            performance_df["%Arch_REV"] = performance_df["%Arch_REV"].fillna(0).apply(lambda x: '{:.1f}%'.format(x*100 ))
            performance_df["Total_Revenue_Budget"] = performance_df["Total_Revenue_Budget"].fillna(0).apply(lambda x: '{:,}'.format(x))
            performance_df["Projected_Revenue"] = performance_df["Projected_Revenue"].fillna(0).apply(lambda x: '{:,.0f}'.format(x))
            performance_df["MTD_Actual_Footfall"] = performance_df["MTD_Actual_Footfall"].fillna(0).apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Budget_Footfall"] = performance_df["MTD_Budget_Footfall"].fillna(0).apply(lambda x: '{:,.0f}'.format(x))
            performance_df["%Arch_FF"] = performance_df["%Arch_FF"].fillna(0).apply(lambda x: '{:.1f}%'.format(x*100))
            performance_df["Total_Footfall_Budget"] = performance_df["Total_Footfall_Budget"].fillna(0).apply(lambda x: '{:,}'.format(x))
            performance_df["Projected_Footfalls"] = performance_df["Projected_Footfalls"].fillna(0).apply(lambda x: '{:,.0f}'.format(x))
            
            
            
            
            Regionperformance_df['MTD_Budget_Revenue'] = (Regionperformance_df['MTD_Budget_Revenue'] * fraction_passed).round(0)

            Regionperformance_df['MTD_Budget_Footfall']=(Regionperformance_df['MTD_Budget_Footfall']*fraction_passed).round(0)
            # Add a new column %Arch_FF as the percentage of MTD_Actual_Footfall to MTD_Budget_Footfall
            Regionperformance_df['%Arch_FF'] = (Regionperformance_df['MTD_Actual_Footfall'] / Regionperformance_df['MTD_Budget_Footfall'])
            # Add a new column %Arch_REV as the percentage of MTD_Actual_Revenue to MTD_Budget_Revenue
            Regionperformance_df['%Arch_REV'] = (Regionperformance_df['MTD_Actual_Revenue'] / Regionperformance_df['MTD_Budget_Revenue'])

            Regionperformance_df['Projected_Footfalls']=(Regionperformance_df['Total_Footfall_Budget'] ) * (Regionperformance_df['MTD_Actual_Footfall'] / Regionperformance_df['MTD_Budget_Footfall'])           
            Regionperformance_df['Projected_Revenue']=(Regionperformance_df['Total_Revenue_Budget'] ) * (Regionperformance_df['MTD_Actual_Revenue'] / Regionperformance_df['MTD_Budget_Revenue'])           

            Regionperformance_df["MTD_Budget_Revenue"] = Regionperformance_df["MTD_Budget_Revenue"].fillna(0).astype(int).apply(lambda x: '{:,.0f}'.format(x))
            Regionperformance_df["MTD_Actual_Revenue"] = Regionperformance_df["MTD_Actual_Revenue"].fillna(0).astype(int).apply(lambda x: '{:,}'.format(x))
            Regionperformance_df["%Arch_REV"] = Regionperformance_df["%Arch_REV"].fillna(0).apply(lambda x: '{:.1f}%'.format(x*100 ))
            Regionperformance_df["Total_Revenue_Budget"] = Regionperformance_df["Total_Revenue_Budget"].fillna(0).apply(lambda x: '{:,}'.format(x))
            Regionperformance_df["Projected_Revenue"] = Regionperformance_df["Projected_Revenue"].fillna(0).apply(lambda x: '{:,.0f}'.format(x))
            Regionperformance_df["MTD_Actual_Footfall"] = Regionperformance_df["MTD_Actual_Footfall"].fillna(0).apply(lambda x: '{:,}'.format(x))
            Regionperformance_df["MTD_Budget_Footfall"] = Regionperformance_df["MTD_Budget_Footfall"].fillna(0).apply(lambda x: '{:,.0f}'.format(x))
            Regionperformance_df["%Arch_FF"] = Regionperformance_df["%Arch_FF"].fillna(0).apply(lambda x: '{:.1f}%'.format(x*100))
            Regionperformance_df["Total_Footfall_Budget"] = Regionperformance_df["Total_Footfall_Budget"].fillna(0).apply(lambda x: '{:,}'.format(x))
            Regionperformance_df["Projected_Footfalls"] = Regionperformance_df["Projected_Footfalls"].fillna(0).apply(lambda x: '{:,.0f}'.format(x))

             
            
            #ALL MONRH DATA
            
            
            # Rearrange the columns
            
            
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
                    content=location,
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

                            # Use the expander widget
        #with st.expander("MONTHWISE REVENUE SUMMARY TABLE"):
            # Set the height of the expander
            #st.write(RR_pivot_Actual, use_container_width=True)
            #st.write(FF_pivot_Actual, use_container_width=True)
        form_container.empty()


