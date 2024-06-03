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
        
        
            # Get the previous month as a date
            #previous_month_date = datetime.now() - relativedelta(months=1)

            
            current_month = datetime.now().month 
            #current_month = datetime.now() - relativedelta(months=1)
            current_month_name = calendar.month_name[current_month]
            

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
            
            performance_df["MTD_Budget_Revenue"] = performance_df["MTD_Budget_Revenue"].replace([np.inf, -np.inf], 0).fillna(0).astype(int).apply(lambda x: '{:,.0f}'.format(x))
            performance_df["MTD_Actual_Revenue"] = performance_df["MTD_Actual_Revenue"].replace([np.inf, -np.inf], 0).fillna(0).astype(int).apply(lambda x: '{:,}'.format(x))
            performance_df["%Arch_REV"] = performance_df["%Arch_REV"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:.1f}%'.format(x*100 ))
            performance_df["Total_Revenue_Budget"] = performance_df["Total_Revenue_Budget"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:,}'.format(x))
            performance_df["Projected_Revenue"] = performance_df["Projected_Revenue"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:,.0f}'.format(x))
            performance_df["MTD_Actual_Footfall"] = performance_df["MTD_Actual_Footfall"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:,}'.format(x))
            performance_df["MTD_Budget_Footfall"] = performance_df["MTD_Budget_Footfall"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:,.0f}'.format(x))
            performance_df["%Arch_FF"] = performance_df["%Arch_FF"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:.1f}%'.format(x*100))
            performance_df["Total_Footfall_Budget"] = performance_df["Total_Footfall_Budget"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:,}'.format(x))
            performance_df["Projected_Footfalls"] = performance_df["Projected_Footfalls"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:,.0f}'.format(x))
            
           
              # Rearrange the columns
            MTD_All = performance_df[
                [ 'Month','Scheme','location_name', 'MTD_Budget_Revenue', 'MTD_Actual_Revenue', '%Arch_REV','Total_Revenue_Budget', 'Projected_Revenue','MTD_Actual_Footfall', 'MTD_Budget_Footfall', '%Arch_FF', 'Total_Footfall_Budget','Projected_Footfalls']
            ]
            
            #ALL MONRH DATA
            
            
            # Rearrange the columns
            Monthly_All = Allperformance_df[
                [ 'Month','Scheme','location_name', 'MTD_Budget_Revenue', 'MTD_Actual_Revenue', '%Arch_REV','Total_Revenue_Budget','MTD_Actual_Footfall', 'MTD_Budget_Footfall', '%Arch_FF', 'Total_Footfall_Budget']
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
                    height=300,
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
                
                with st.expander("DOWNLOAD PREVIOUS MONTH"):
                    
                    Allperformance_df["MTD_Budget_Revenue"] = Allperformance_df["MTD_Budget_Revenue"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:,}'.format(x))
                    Allperformance_df["MTD_Actual_Revenue"] = Allperformance_df["MTD_Actual_Revenue"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:,}'.format(x))
                    Allperformance_df["%Arch_REV"] = Allperformance_df["%Arch_REV"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:.1f}%'.format(x))
                    Allperformance_df["Total_Revenue_Budget"] = Allperformance_df["Total_Revenue_Budget"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:,}'.format(x))
                    Allperformance_df["Projected_Revenue"] = Allperformance_df["Projected_Revenue"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:,}'.format(x))
                    Allperformance_df["MTD_Actual_Footfall"] = Allperformance_df["MTD_Actual_Footfall"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:,}'.format(x))
                    Allperformance_df["MTD_Budget_Footfall"] = Allperformance_df["MTD_Budget_Footfall"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:,}'.format(x))
                    Allperformance_df["%Arch_FF"] = Allperformance_df["%Arch_FF"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:.1f}%'.format(x/100))
                    Allperformance_df["Total_Footfall_Budget"] = Allperformance_df["Total_Footfall_Budget"].apply(lambda x: '{:,}'.format(x))
                    Allperformance_df["Projected_Footfalls"] = Allperformance_df["Projected_Footfalls"].replace([np.inf, -np.inf], 0).fillna(0).apply(lambda x: '{:,}'.format(x))

                    
                    current_month = datetime.now().month
                    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][:current_month]
                    
                    # Create a list of months up to the previous month
                    display_months = months[:current_month - 1]

                    # Set the default value to the previous month
                    default_month_index = current_month - 2  #
            
                    # Selectbox for choosing a month
                    search_text = st.selectbox("Select Month", [""] + display_months, index=default_month_index, key="search_text")
                
                    # Use the session state value for filtering the dataframe
                    if st.session_state.search_text:
                        filtered_df = Monthly_All[Allperformance_df['Month']==search_text]
                    else:
                        filtered_df = MTD_All
                            
                    st.write(filtered_df, use_container_width=True)
            
        
        # Use the expander widget
        #with st.expander("MONTHWISE REVENUE SUMMARY TABLE"):
            # Set the height of the expander
            #st.write(RR_pivot_Actual, use_container_width=True)
            #st.write(FF_pivot_Actual, use_container_width=True)
    else:
       st.write("You  are  not  logged  in. Click   **[Account]**  on the  side  menu to Login  or  Signup  to proceed")



