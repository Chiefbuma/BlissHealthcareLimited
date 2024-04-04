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
        
    if 'is_Regionauthenticated' not in st.session_state:
        st.session_state.is_Regionauthenticated = False 
 
        # Initialize session state if it doesn't exist

   
    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up"]
        choice = st.sidebar.selectbox("", menu)

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


            def get_regions(staffnumber):
                # Perform a Supabase query to fetch data from the 'users' table
                response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
                login_df = pd.DataFrame(response.data)
                return login_df

            def add_regionuserdata(staffnumber, password, location, region):
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

            

            def login_regionuser(staffnumber,password):
                
                try:
                    # Perform a Supabase query to fetch user data based on staff number
                    response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
                    user_data = response.data
                    facilities_df = get_regions(staffnumber)
                    if not facilities_df.empty:
                        location = facilities_df['location'].iloc[0]
                        region = facilities_df['region'].iloc[0]

                        # Check if the credentials match
                        if password == facilities_df['password'].iloc[0]:
                            return True, location, region
                        return False, None, None
                except APIError as e:
                    st.error("Invalid credentials. Please log in again.")
                    st.stop()  # Stop the execution to prevent further code execution


            def view_all_regionusers():
                response = supabase.from_('users').select('*').execute()
                data = response.data
                return data
 
            
            # log in app
            

            if choice == "Login":
                # Check if the user is logged in
                

                with st.form("Login Form"):
                    st.write("Login Form")
                    staffnumber = st.text_input("Staffnumber",key="staff_region")
                    password = st.text_input("Password", type='password',key="pass_region")
                    # Fetch location and region based on staffnumber
                    load=st.form_submit_button("Login")
                    
                    
                    if "Regionlogged_in" not in st.session_state:
                        st.session_state.Regionlogged_in= False
                        
                        
                    if load or st.session_state.Regionlogged_in:
                        st.session_state.Regionlogged_in= True
                        st.session_state.staffnumber = staffnumber
                        st.session_state.password = password
                        result, location, region = login_regionuser(staffnumber, password)
                        if result:
                            st.success("Logged In successfully")
                            st.write(f"Location: {location}, Region: {region}")
                            st.session_state.is_Regionauthenticated=True
                            
   
                        else:
                            st.warning("Invalid credentials. Please try again.")

            elif choice == "Sign up":
                with st.form("Sign-up Form"):  
                    st.write("Sign-up Form")
                    staffnumber = st.text_input('Staff Number', key='signupregion_staff_number')
                    location = st.selectbox("Select Location", location_names)
                    selected_location_row = location_df[location_df['Location'] == location]
                    region = selected_location_row['Region'].iloc[0] if not selected_location_row.empty else None
                    password = st.text_input('Password', key='signupregion_password')
                    signup_btn = st.form_submit_button('Sign Up')
                    if signup_btn:
                        add_regionuserdata(staffnumber, password, location, region)
                        st.success("You have created a new account")
                        st.session_state.is_Regionauthenticated=True
                        st.session_state.Regionlogged_in= True
                        st.session_state.staffnumber = staffnumber
                        st.session_state.password = password
                        form_container.empty()
                        
                        
                        
    if st.session_state.is_Regionauthenticated:
        @st.cache_resource
        def init_connection():
            url = "https://effdqrpabawzgqvugxup.supabase.co"
            key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmZmRxcnBhYmF3emdxdnVneHVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA1MTQ1NDYsImV4cCI6MjAyNjA5MDU0Nn0.Dkxicm9oaLR5rm-SWlvGfV5OSZxFrim6x8-QNnc2Ua8"
            return create_client(url, key)

        supabase = init_connection()
        
        # Check if the connection is successful
        if init_connection():

            st.session_state.Regionlogged_in= True
            # Dropdown for selecting the year
                      
            current_month = "March"
            #current_month =datetime.now().strftime('%B')

            # Query the MTD_Revenue table with the filter for location_name and Month
            response = supabase.from_('MTD_Region').select('*').eq('Region', region).eq('Month', current_month).execute()

            performance_df = pd.DataFrame(response.data)
            
            # Query the MTD_Revenue table with the filter for location_name and Month
            response2 = supabase.from_('MTD_Region').select('*').eq('Region', region).eq('Month', current_month).execute()

            Allperformance_df = pd.DataFrame(response2.data)
            
            
            
            # Create a new figure
            fig3 = go.Figure()
            
            # # Define the metrics
            
            Total_budget = performance_df['Total_Revenue_Budget'].sum()
            formatted_Rev_budget = "{:,.0f}".format(Total_budget)
            
            MTD_Revenue_budget = performance_df['MTD_Budget_Revenue'].sum()
            formatted_Rev_budget = "{:,.0f}".format(MTD_Revenue_budget)
            #Total_budget_FF = performance_df['Budget_Footfall'].sum()
            #formatted_FF_budget = "{:,.0f}".format(Total_budget_FF)
            
            
            fig3.add_trace(
            go.Indicator(
                title={'text': "MTD BUDGET",'font': {'size': 15,'color': 'green'}},
                value= int(Total_budget)
            )
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
            fig2 = go.Figure()
            
            # # Define the Reveneu metrics
            Total_Revenue = performance_df['MTD_Actual_Revenue'].sum()
            formatted_total_revenue = "{:,.0f}".format(Total_Revenue)
            
            Arch_Rev = (performance_df['MTD_Actual_Revenue'].sum() / performance_df['MTD_Budget_Revenue'].sum()) * 100
            formatted_arch_rev = "{:.2f}%".format(Arch_Rev)
            
            
            # # Define Footfalls  metrics
            #Total_footfalls = performance_df['Footfall'].sum()
            #formatted_total_footfalls = "{:,.0f}".format(Total_footfalls)
            #Arch_FF = performance_df['%Arch_FF'].mean() * 100
            #formatted_arch_ff = "{:.0f}%".format( Arch_FF)
            
            
            fig2.add_trace(
            go.Indicator(
                title={'text': "MTD REVENUE",'font': {'size': 15,'color': 'green'}},
                value= int(Total_Revenue)
            )
        )
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
            
            
            # Create a new figure
            fig5 = go.Figure()
            fig5.add_trace(
            go.Indicator(
                title={'text': "MTD BUDGET",'font': {'size': 15,'color': 'green'}},
                value= int(Total_budget)
            )
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
             #fig6 = go.Figure()
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
                
            performance_df["MTD_Budget_Revenue"] = performance_df["MTD_Budget_Revenue"].apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Actual_Revenue"] = performance_df["MTD_Actual_Revenue"].apply(lambda x: '{:,}'.format(x))
            performance_df["%Arch_REV"] = performance_df["%Arch_REV"].apply(lambda x: '{:.1f}%'.format(x ))
            performance_df["Total_Revenue_Budget"] = performance_df["Total_Revenue_Budget"].apply(lambda x: '{:,}'.format(x))
            performance_df["Projected_Revenue"] = performance_df["Projected_Revenue"].apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Actual_Footfall"] = performance_df["MTD_Actual_Footfall"].apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Budget_Footfall"] = performance_df["MTD_Budget_Footfall"].apply(lambda x: '{:,}'.format(x))
            performance_df["%Arch_FF"] = performance_df["%Arch_FF"].apply(lambda x: '{:.1f}%'.format(x/100 ))
            performance_df["Total_Footfall_Budget"] = performance_df["Total_Footfall_Budget"].apply(lambda x: '{:,}'.format(x))
            performance_df["Projected_Footfalls"] = performance_df["Projected_Footfalls"].apply(lambda x: '{:,}'.format(x))

            
            fig_request_by_type_Rev = go.Figure(data=[go.Table(
                header=dict(values=['Scheme','Revenue<br>Budget','Revenue<br>Actual','%Arch<br>REV','Total<br>Budget','Projected<br>Revenue',
                                    'Footfall<br>Budget','Footfall<br>Actual','%Arch<br>FF','Total<br>Budget','Projected<br>Footfalls'],
                            fill_color='rgba(0, 84, 0, 1)',
                            align='left',
                            font=dict(family='Georgia', color='White', size=14),
                            line_color='darkslategray',  # Border color
                            line=dict(width=1)),
                            columnwidth=[40, 30, 30,30, 30, 30, 30, 30, 30, 30,40],# Border width
                cells=dict(values=[performance_df["Scheme"],
                                   performance_df["MTD_Budget_Revenue"],
                                   performance_df["MTD_Actual_Revenue"],
                                   performance_df["%Arch_REV"],
                                    performance_df["Total_Revenue_Budget"],
                                    performance_df["Projected_Revenue"],
                                     performance_df["MTD_Budget_Footfall"],
                                    performance_df["MTD_Actual_Footfall"],
                                    performance_df["%Arch_FF"],
                                    performance_df["Total_Footfall_Budget"],
                                    performance_df["Projected_Footfalls"]]
,
                        fill_color=[
                                ['rgba(0, 0, 82, 1)'],  # Blue for "Report" column
                                ['white'] * len(performance_df)  # White for "Count" column
                            ],
                        font_color=[
                                ['white'],  # Blue for "Report" column
                                ['black'] * len(performance_df)  # White for "Count" column
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
            
            
            
            def generate_sales_data():
                np.random.seed(0)  # For reproducible results
                months = ['Jan', 'Feb', 'Mar']
                sales = np.random.randint(1000, 5000, size=len(months))
                return pd.DataFrame({'Month': months, 'Sales': sales})
            
            with card_container(key="MTDREVENUE"):
                card_style3 = "border: 2px solid #000000; border-radius: 5px; padding: 10px; background-color:#ffffff; color:#000000; text-align: center; font-size: 15px;font-weight: bold; width: 100%; height: 30;"
                ui.card(
                    content="Region: " + region,
                    key="MCcard3"
                ).render()

                cols = st.columns(4)
                with cols[0]:
                    ui.card(title="MTD Revenue", content=formatted_total_revenue, key="Revcard1").render()
                with cols[1]:
                    ui.card(title="MTD Budget", content= formatted_Rev_budget, key="Revcard2").render()
                with cols[2]:
                    ui.card(title="MTD Archievement", content=formatted_arch_rev, key="Revcard3").render()
                with cols[3]:
                    ui.card(title="Last Updated:", content="31/03/2024", key="Revcard4").render()    
                st.plotly_chart(fig_request_by_type_Rev, use_container_width=True)
                with st.expander("DEPARTMENTAL MTD REVENUE (CASH & FSS)"):
                    st.write(Allperformance_df , use_container_width=True)
        
        
        # Use the expander widget
        #with st.expander("MONTHWISE REVENUE SUMMARY TABLE"):
            # Set the height of the expander
            #st.write(RR_pivot_Actual, use_container_width=True)
            #st.write(FF_pivot_Actual, use_container_width=True)


        form_container.empty()
        
             

