import mysql.connector
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from IPython.display import display
import calendar
import numpy as np
import plotly.express as px
from IPython.display import HTML
import streamlit as st
import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
import pandas as pd
from datetime import datetime
import streamlit_option_menu as option_menu
import plotly.graph_objects as go


# Set the page configuration
st.set_page_config(page_title="My Streamlit App", layout="wide")

def home():
    st.session_state.is_authenticated = False 
    
    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up", "Log Out"]
        choice = st.sidebar.selectbox("", menu)

        form_container = st.empty()
        with form_container :
            host = '127.0.0.1'
            port = 3306
            database = 'blisshealthcare'
            user = 'root'
            password = 'buluma'

            # Connect to the MySQL server
            connection = mysql.connector.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                allow_local_infile=True
            )
            # Query to select all columns from the facilities table
            query = "SELECT * FROM facilities"

            # Load data into a DataFrame
            location_df = pd.read_sql(query, con=connection)

            cursor = connection.cursor()

            def create_usertable():
                cursor.execute('CREATE TABLE IF NOT EXISTS usertable (staff_id INT PRIMARY KEY AUTO_INCREMENT, staffnumber INT, password TEXT, location TEXT, region TEXT)')

            def add_userdata(staffnumber, password, location, region):
                cursor.execute('INSERT INTO usertable (staffnumber, password, location, region) VALUES (%s, %s, %s, %s)', (staffnumber, password, location, region))
                connection.commit()

            def get_facilities(staffnumber):
                query = "SELECT * FROM usertable WHERE staffnumber = %s"
                params = (staffnumber,)
                Login_df = pd.read_sql(query, params=params, con=connection)
                return Login_df

            def login_user(staffnumber, password):
                # Fetch location and region based on staffnumber
                facilities_df = get_facilities(staffnumber)

                if not facilities_df.empty:
                    location = facilities_df['location'].iloc[0]
                    region = facilities_df['region'].iloc[0]

                    # Check if the credentials match
                    cursor.execute('SELECT * FROM usertable WHERE staffnumber = %s AND password = %s', (staffnumber, password))
                    data = cursor.fetchall()
                    return data, location, region
                else:
                    return None, None, None

            def view_all_users():
                cursor.execute('SELECT * FROM usertable')
                data = cursor.fetchall()
                return data

            # Fetch locations from the database
            cursor.execute("SELECT Location FROM facilities")
            locations = cursor.fetchall()
            location_names = [location[0] for location in locations]

            # log in app
            
            if choice == "Log Out":
                st.subheader("Log Out")

            elif choice == "Login":
                # Check if the user is logged in
                

                with st.form("Login Form"):
                    st.write("Login Form")
                    staffnumber = st.text_input("Staffnumber")
                    password = st.text_input("Password", type='password')
                    # Fetch location and region based on staffnumber
                    load=st.form_submit_button("Login")
                    facilities_df = get_facilities(staffnumber)
                    if not facilities_df.empty:
                        location = facilities_df['location'].iloc[0]
                        region = facilities_df['region'].iloc[0]
                    
                    if "logged_in" not in st.session_state:
                        st.session_state.logged_in= False
                        
                    if load or st.session_state.logged_in:
                        st.session_state.logged_in= True
                        create_usertable() 
                        result, location, region = login_user(staffnumber, password)
                        if result:
                            st.success("Logged In successfully")
                            st.write(f"Location: {location}, Region: {region}")
                            st.session_state.is_authenticated=True
                            st.session_state["logged_in"] == "True"
                            form_container.empty()

                        else:
                            st.warning("Invalid credentials. Please try again.")

            elif choice == "Sign up":
                with st.form("Sign-up Form"):
                    st.write("Sign-up Form")
                    new_user = st.text_input("Staffnumber")
                    new_password = st.text_input("Password", type='password')
                    location = st.selectbox("Select Location", location_names)
                    selected_location_row = location_df[location_df['Location'] == location]
                    region = selected_location_row['Region'].iloc[0] if not selected_location_row.empty else None

                    if st.form_submit_button("Sign up"):
                        create_usertable()
                        add_userdata(new_user, new_password, location, region)
                        st.success("You have created a new account")
                        st.session_state["logged_in"] == "True"
                        st.session_state.is_authenticated=True
                        form_container.empty()
    
                        
    if st.session_state.is_authenticated:
        form_container.empty()
        
        def fraction_of_days_in_month(given_date):

            # Convert the input date string to a datetime object
            given_date = pd.to_datetime(given_date, format='%Y-%m-%d')
            
            # Extract the month and year from the given date
            month = given_date.month
            year = given_date.year
            
            # Find the number of days in the month
            days_in_month = calendar.monthrange(year, month)[1]
            
            # Calculate the fraction of days passed with two decimal places
            fraction_passed = round(given_date.day / days_in_month, 2)
            
            return fraction_passed

        # Replace these with your actual database credentials
        host = '127.0.0.1'
        port = 3306
        database = 'blisshealthcare'
        user = 'root'
        password = 'buluma'

        # Connect to the MySQL server
        connection = mysql.connector.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            allow_local_infile=True
        )

        # Check if the connection is successful
        if connection.is_connected():
            
            # Create a cursor object to execute SQL queries
            cursor = connection.cursor()

            # Execute queries to fetch data from the 'Allmerged_sales' table
            query_sales = "SELECT * FROM Allmerged_sales"
            cursor.execute(query_sales)
            data_sales = cursor.fetchall()

            # Get the column names from the cursor description
            columns_sales = [i[0] for i in cursor.description]

            # Create a Pandas DataFrame with the data
            df_Allsales = pd.DataFrame(data_sales, columns=columns_sales)

            df_Allsales['bill_date'] = pd.to_datetime(df_Allsales['bill_date'])

            card_style3 = "border: 2px solid #000000; border-radius: 5px; padding: 5px; background-color:#ffffff; color:#000000; text-align: center; font-size: 15px;font-weight: bold;"
            
            st.markdown(f"<div style='{card_style3}'>{f'REVENUE AND FOOTFALLS DASHBOARD <br> {location}'}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1,col2,col3,col4 =st.columns(4)
            
            with col1:
                st.session_state.logged_in= True
                # Dropdown for selecting the year
                current_year = datetime.now().year
                selected_year = st.selectbox("Select Year:", df_Allsales['bill_date'].dt.year.unique(), index=df_Allsales['bill_date'].dt.year.unique().tolist().index(current_year))
                
                
            with col2:
                st.session_state.logged_in= True
                # Dropdown for selecting the month
                selected_month = st.selectbox("Select Month:", df_Allsales['bill_date'].dt.month_name().unique(), index=datetime.now().month - 1)
                # Filter the DataFrame based on the selected year and month
                df_filtered = df_Allsales[
                        (df_Allsales['bill_date'].dt.year == selected_year) &
                        (df_Allsales['bill_date'].dt.month_name() == selected_month)
                    ]

            with col3:
                st.session_state.logged_in= True
                # Calendar for selecting "From Date" range
                selected_from_date = st.date_input(
                        "Select From Date",
                        value=df_filtered['bill_date'].min().date(),
                        key="from_date",
                        min_value=df_filtered['bill_date'].min().date(),
                        max_value=df_filtered['bill_date'].max().date()
                        
                    )

                    # Filter the DataFrame based on the selected year and month
                df_filtered = df_Allsales[
                        (df_Allsales['bill_date'].dt.year == selected_year) &
                        (df_Allsales['bill_date'].dt.month_name() == selected_month)
                    ]

                    # Get the maximum date for the selected month, handling missing values
                max_date_for_month = df_filtered['bill_date'].dropna().max().date() if not df_filtered.empty else None

                    # Determine the maximum date based on the selected year and current year
                if selected_year < datetime.now().year and max_date_for_month:
                        max_value_to_date = max_date_for_month
                else:
                        max_value_to_date = datetime.now().date() - timedelta(days=1)
                
        
            with col4: 
                st.session_state.logged_in= True      
                # Calendar for selecting "To Date" range
                selected_to_date = st.date_input(
                        "Select To Date",
                        value=max_value_to_date,
                        key="to_date",
                        min_value=df_filtered['bill_date'].min().date() if not df_filtered.empty else datetime.now().date(),
                        max_value=df_filtered['bill_date'].max().date() if not df_filtered.empty else datetime.now().date()
                    )
                
            
            # Convert the selected date ranges to datetime64[ns]
            selected_from_date = pd.to_datetime(selected_from_date)
            selected_to_date = pd.to_datetime(selected_to_date)

            # Filter the DataFrame based on the selected date ranges and year
            df_filtered = df_Allsales[
                (df_Allsales['bill_date'] >= selected_from_date) &
                (df_Allsales['bill_date'] <= selected_to_date) &
                (df_Allsales['bill_date'].dt.year == selected_year)
            ]

            df_filtered_YTD = df_Allsales[
                (df_Allsales['bill_date'].dt.year == selected_year) &
                (df_Allsales['bill_date'].dt.year == selected_year)
            ]

            # Calculate OVERALL MTD revenue and footfalls for the selected date range
            ALL_summary_df = df_filtered.groupby(['location_name']).agg(
                MTD_Actual_Footfall=('Footfall', 'sum'),
                MTD_Budget_Footfall=('Budget_Footfalls', 'sum'),
                MTD_Actual_Revenue=('Revenue', 'sum'),
                MTD_Budget_Revenue=('Budget_Revenue', 'sum')
            ).reset_index()



            # Assuming <NA> represents missing values, replace them with blanks
            ALL_summary_df.replace('<NA>', '', inplace=True)

            # Round and convert numeric columns to integers
            Allnumeric_columns = ['MTD_Actual_Footfall', 'MTD_Budget_Footfall', 'MTD_Actual_Revenue', 'MTD_Budget_Revenue']
            ALL_summary_df[Allnumeric_columns] = ALL_summary_df[Allnumeric_columns].round(0).astype(int)

            # Add a new column %Arch_FF as the percentage of MTD_Actual_Footfall to MTD_Budget_Footfall
            ALL_summary_df['%Arch_FF'] = (ALL_summary_df['MTD_Actual_Footfall'] / ALL_summary_df['MTD_Budget_Footfall'])

            # Add a new column %Arch_REV as the percentage of MTD_Actual_Revenue to MTD_Budget_Revenue
            ALL_summary_df['%Arch_REV'] = (ALL_summary_df['MTD_Actual_Revenue'] / ALL_summary_df['MTD_Budget_Revenue'])


            # Calculate fraction of days passed for the selected month
            fraction_passed = fraction_of_days_in_month(selected_to_date)

            # Add a new column 'Projected Revenue' to ALL_summary_df
            ALL_summary_df['Projected_Revenue'] = (ALL_summary_df['MTD_Budget_Revenue'] / fraction_passed) * (ALL_summary_df['MTD_Actual_Revenue'] / ALL_summary_df['MTD_Budget_Revenue'])

            # Add a new column 'Projected Revenue' to ALL_summary_df
            ALL_summary_df['Projected_Footfalls'] = (ALL_summary_df['MTD_Budget_Footfall'] / fraction_passed) * (ALL_summary_df['MTD_Actual_Footfall'] / ALL_summary_df['MTD_Budget_Footfall'])


            # Rearrange the columns
            ALL_summary_df = ALL_summary_df[
                ['location_name', 'MTD_Budget_Revenue', 'MTD_Actual_Revenue', '%Arch_REV','Projected_Revenue', 'MTD_Actual_Footfall', 'MTD_Budget_Footfall', '%Arch_FF','Projected_Footfalls']
            ]

            # Calculate MTD revenue and footfalls for the selected date range
            MTD_summary_df = df_filtered.groupby(['location_name', 'Scheme']).agg(
                MTD_Actual_Footfall=('Footfall', 'sum'),
                MTD_Budget_Footfall=('Budget_Footfalls', 'sum'),
                MTD_Actual_Revenue=('Revenue', 'sum'),
                MTD_Budget_Revenue=('Budget_Revenue', 'sum')
            ).reset_index()

            # Replace NaN and inf values with 0
            MTD_summary_df.replace([np.inf, -np.inf, np.nan], 0, inplace=True)
            
            # Assuming <NA> represents missing values, replace them with blanks
            MTD_summary_df.replace('<NA>', '', inplace=True)

            MTD_summary_df = MTD_summary_df[MTD_summary_df['Scheme'] != 'HEALTHIER KENYA']
            MTD_summary_df = MTD_summary_df[MTD_summary_df['Scheme'] != 'NHIF CAPITATION']

            # Round and convert numeric columns to integers
            numeric_columns = ['MTD_Actual_Footfall', 'MTD_Budget_Footfall', 'MTD_Actual_Revenue', 'MTD_Budget_Revenue']
            MTD_summary_df[numeric_columns] = MTD_summary_df[numeric_columns].round(0).astype(int)

            # Add a new column %Arch_FF as the percentage of MTD_Actual_Footfall to MTD_Budget_Footfall
            MTD_summary_df['%Arch_FF'] = (MTD_summary_df['MTD_Actual_Footfall'] / MTD_summary_df['MTD_Budget_Footfall'])

            # Add a new column %Arch_REV as the percentage of MTD_Actual_Revenue to MTD_Budget_Revenue
            MTD_summary_df['%Arch_REV'] = (MTD_summary_df['MTD_Actual_Revenue'] / MTD_summary_df['MTD_Budget_Revenue'])

            # Calculate fraction of days passed for the selected month
            fraction_passed = fraction_of_days_in_month(selected_to_date)

            # Add a new column 'Projected Revenue' to ALL_summary_df
            MTD_summary_df['Projected_Revenue'] = (MTD_summary_df['MTD_Budget_Revenue'] / fraction_passed) * (MTD_summary_df['MTD_Actual_Revenue'] / MTD_summary_df['MTD_Budget_Revenue'])

            # Add a new column 'Projected Revenue' to ALL_summary_df
            MTD_summary_df['Projected_Footfalls'] = (MTD_summary_df['MTD_Budget_Footfall'] / fraction_passed) * (MTD_summary_df['MTD_Actual_Footfall'] / MTD_summary_df['MTD_Budget_Footfall'])


            # Rearrange the columns
            MTD_summary_df = MTD_summary_df[
                ['location_name', 'Scheme','MTD_Budget_Revenue', 'MTD_Actual_Revenue', '%Arch_REV','Projected_Revenue', 'MTD_Actual_Footfall', 'MTD_Budget_Footfall', '%Arch_FF','Projected_Footfalls']
            ]

            # Calculate YTD revenue and footfalls for the selected date range
            YTD_summary_df = df_filtered_YTD.groupby(['Year', 'Month', 'Scheme', 'location_name']).agg(
                YTD_Actual_Footfall=('Footfall', 'sum'),
                YTD_Budget_Footfall=('Budget_Footfalls', 'sum'),
                YTD_Actual_Revenue=('Revenue', 'sum'),
                YTD_Budget_Revenue=('Budget_Revenue', 'sum')
            ).reset_index()

            # Assuming <NA> represents missing values, replace them with blanks
            YTD_summary_df.replace('<NA>', '', inplace=True)

            # Round and convert numeric columns to integers
            YTDnumeric_columns = ['YTD_Actual_Footfall', 'YTD_Budget_Footfall', 'YTD_Actual_Revenue', 'YTD_Budget_Revenue']
            YTD_summary_df[YTDnumeric_columns] = YTD_summary_df[YTDnumeric_columns].round(0).astype(int)

            # Add a new column %Arch_FF as the percentage of YTD_Actual_Footfall to YTD_Budget_Footfall
            YTD_summary_df['%Arch_FF'] = (YTD_summary_df['YTD_Actual_Footfall'] / YTD_summary_df['YTD_Budget_Footfall'])

            # Add a new column %Arch_REV as the percentage of YTD_Actual_Revenue to YTD_Budget_Revenue
            YTD_summary_df['%Arch_REV'] = (YTD_summary_df['YTD_Actual_Revenue'] / YTD_summary_df['YTD_Budget_Revenue'])

            # Rearrange the columns
            YTD_summary_df = YTD_summary_df[
                ['Year', 'Month', 'location_name', 'Scheme', 'YTD_Budget_Revenue', 'YTD_Actual_Revenue', '%Arch_REV', 'YTD_Actual_Footfall', 'YTD_Budget_Footfall', '%Arch_FF']
            ]

            # Filter out specific schemes
            YTD_summary_df = YTD_summary_df[(YTD_summary_df['Scheme'] != 'HEALTHIER KENYA') & (YTD_summary_df['Scheme'] != 'NHIF CAPITATION')]
            
            # Create three columns in the sidebar
            col1, col2, col3 = st.sidebar.columns(3)
            
            # Dropdown filter for location_name
            selected_location = location

            # Filter the data based on the selected location, date range, and 'Scheme' column
            filtered_All_df = ALL_summary_df[
                (ALL_summary_df['location_name'] == location)
            ]


            # Sum the specified columns for the selected date range
            sum_columnsAll = ['MTD_Actual_Footfall', 'MTD_Budget_Footfall', 'MTD_Actual_Revenue', 'MTD_Budget_Revenue','Projected_Revenue','Projected_Footfalls']
            totals_sumAll = filtered_All_df[sum_columnsAll].sum()

            # Filter the data based on the selected location, date range, and 'Scheme' column
            filtered_totals_df = MTD_summary_df[
                (MTD_summary_df['location_name'] == selected_location) &
                (MTD_summary_df['Scheme'] != 'NHIF_CAPITATION')
            ]

            # Sum the specified columns for the selected date range
            sum_columns = ['MTD_Actual_Footfall', 'MTD_Budget_Footfall', 'MTD_Actual_Revenue', 'MTD_Budget_Revenue','Projected_Revenue','Projected_Footfalls']
            totals_sum = filtered_totals_df[sum_columns].sum()

            # Separate the DataFrames based on the Scheme
            filtered_totals_df_footfall = filtered_totals_df[
                ['location_name', 'Scheme', 'MTD_Actual_Footfall', 'MTD_Budget_Footfall', '%Arch_FF','Projected_Footfalls']
            ]

            filtered_totals_df_revenue = filtered_totals_df[
                ['location_name', 'Scheme', 'MTD_Actual_Revenue', 'MTD_Budget_Revenue', '%Arch_REV','Projected_Revenue']
            ]

            #Replace NaN and inf values with a specific value (e.g., 0)
            filtered_totals_df_revenue = filtered_totals_df_revenue.replace([np.inf, -np.inf, np.nan], 0)

            # Convert specific columns to integers
            int_columns_REV = ['MTD_Actual_Revenue', 'MTD_Budget_Revenue','Projected_Revenue']
            percent_columns_REV = ['%Arch_REV']

            # Use .loc to set values for filtered_totals_df_footfall
            filtered_totals_df_revenue.loc[:, int_columns_REV] = filtered_totals_df_revenue[int_columns_REV].astype(int).apply(
                lambda x: x.apply(lambda y: '{:,}'.format(y)))
            filtered_totals_df_revenue.loc[:, percent_columns_REV] = filtered_totals_df_revenue[percent_columns_REV].apply(
                lambda x: x.apply(lambda y: '{:.1%}'.format(y)))


            # Filter the data based on the selected location, date range, and 'Scheme' column
            filtered_YTD_df = YTD_summary_df[
                (YTD_summary_df['location_name'] == selected_location)
            ]    

            # Sum the specified columns for the selected date range
            sum_columnsYTD = ['YTD_Actual_Footfall', 'YTD_Budget_Footfall', 'YTD_Actual_Revenue', 'YTD_Budget_Revenue']
            totals_sumYTD = filtered_YTD_df[sum_columnsYTD].sum()

            # Separate the DataFrames based on the Scheme
            filtered_YTD_footfall = filtered_YTD_df[
                ['Month','location_name', 'Scheme', 'YTD_Actual_Footfall', 'YTD_Budget_Footfall', '%Arch_FF']
            ]

            #Define the correct order of months
            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

            # Convert 'Month' column to categorical with the specified order using .loc
            filtered_YTD_footfall.loc[:, 'Month'] = pd.Categorical(filtered_YTD_footfall['Month'], categories=month_order, ordered=True)


            FF_agg_columns = {
            'YTD_Actual_Footfall': 'sum',
            'YTD_Budget_Footfall': 'sum',
            '%Arch_FF': 'mean'
            # Using 'mean' for Total, update as needed
        }
            # Group by 'Report' and 'Type', and calculate the sum for each group
            Final_YTD = filtered_YTD_footfall.groupby(['Month','location_name','Scheme'], observed=False).agg(FF_agg_columns).reset_index()
            
            # Create pivot tables for each column
            FF_pivot_Actual = filtered_YTD_footfall.pivot_table(index=['Scheme',], columns='Month', values='YTD_Actual_Footfall', aggfunc='sum')
            
            # Add a row for totals
            FF_pivot_Actual.loc['TOTAL FOOTFALLS'] = FF_pivot_Actual.sum(numeric_only=True, axis=0)
            
            # Define the correct order of months
            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

            # Reorder columns based on the month_order list
            FF_pivot_Actual = FF_pivot_Actual.reindex(columns=month_order, fill_value=0)
            # Display MTD-Revenue table

            filtered_YTD_revenue = filtered_YTD_df[
                ['Month','location_name', 'Scheme', 'YTD_Actual_Revenue', 'YTD_Budget_Revenue', '%Arch_REV']
        ]

            #Convert 'Month' column to categorical with the specified order using .loc
            filtered_YTD_revenue.loc[:, 'Month'] = pd.Categorical(filtered_YTD_revenue['Month'], categories=month_order, ordered=True)

            
            RR_agg_columns = {
            'YTD_Actual_Revenue': 'sum',
            'YTD_Budget_Revenue': 'sum',
            '%Arch_REV': 'mean'
            # Using 'mean' for Total, update as needed
        }
            # Group by 'Report' and 'Type', and calculate the sum for each group
            Final_YTD_REV = filtered_YTD_revenue.groupby(['Month','location_name','Scheme'], observed=False).agg(RR_agg_columns).reset_index()
            
                # Create pivot table for YTD actual revenue with months as columns
            RR_pivot_Actual = filtered_YTD_revenue.pivot_table(index='Scheme', columns='Month', values='YTD_Actual_Revenue', aggfunc='sum')

            # Add a row for totals
            RR_pivot_Actual.loc['TOTAL REVENUE'] = RR_pivot_Actual.sum(numeric_only=True, axis=0)

            # Display MTD-Revenue table
            # Define the correct order of months
            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

            # Reorder columns based on the month_order list
            RR_pivot_Actual = RR_pivot_Actual.reindex(columns=month_order, fill_value=0)
            # Display MTD-Revenue table
            
                # Define column definitions for AgGrid
            column_defs_ALL = [
                {"field": col, "hide": col == "location_name", "cellRenderer": "function(params) { return params.value.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0}); }", "minWidth": 100, "editable": False, "filter": True, "resizable": True, "sortable": True}
                for col in filtered_All_df.columns
            ]

            # Build grid options for AgGrid
            grid_options_summary = GridOptionsBuilder.from_dataframe(filtered_All_df).build()
            grid_options_summary['autoHeight'] = False
            grid_options_summary['defaultColDef'] = {
                "width": 100,
                "flex": 0,
                "headerClass": "wrapped-header"
            }
            grid_options_summary["columnDefs"] = column_defs_ALL

            # Convert specific columns to integers
            int_columns_ALL = ['MTD_Budget_Footfall', 'MTD_Actual_Footfall', 'MTD_Actual_Revenue', 'MTD_Budget_Revenue','Projected_Revenue','Projected_Footfalls']
            percent_columns_ALL = ['%Arch_FF', '%Arch_REV']
            
            grid_options_Revenue = GridOptionsBuilder.from_dataframe(filtered_totals_df_revenue).build()
            grid_options_Revenue['autoHeight'] = True
            grid_options_Revenue['defaultColDef'] = {
                "width": 50,  # Set the width to 100 pixels for each column
                "flex": 10,  # Make the columns not flexible
                "headerClass": "blue-header" # Add a CSS class for wrapping headers
            }

            # Define the columnDefs to hide the 'Scheme' column
            column_defs_REV = [
            {"field": col, "hide": col == "location_name", "cellRenderer": "function(params) { return params.value.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0}); }", "minWidth": 100, "editable": False, "filter": True, "resizable": True, "sortable": True}
            for col in filtered_totals_df_revenue.columns]

            grid_options_Revenue["location_name"] = column_defs_REV

            # Add inline CSS styles for the headers
            grid_options_Revenue['css'] = {
                "header": {
                    "background-color": "blue",
                    "color": "white",
                    "font-weight": "bold",
                    "text-align": "center",
                    "padding": "8px"
                },
                "headerHover": {
                    "background-color": "#0056b3"  # Darker blue on hover
                }
            }

            #Replace NaN and inf values with a specific value (e.g., 0)
            filtered_totals_df_revenue = filtered_totals_df_revenue.replace([np.inf, -np.inf, np.nan], 0)

            # Convert specific columns to integers
            int_columns_REV = ['MTD_Budget_Revenue','MTD_Actual_Revenue','Projected_Revenue']
            percent_columns_REV = ['%Arch_REV']
            
            grid_options_Footfalls = GridOptionsBuilder.from_dataframe(filtered_totals_df_footfall).build()
            grid_options_Footfalls['autoHeight'] = True
            grid_options_Footfalls['defaultColDef'] = {
                "width": 50,  # Set the width to 100 pixels for each column
                "flex": 10,  # Make the columns not flexible
                "headerClass": "blue-header" # Add a CSS class for wrapping headers
            }
            
            # Define the columnDefs to hide the 'Scheme' column
            column_defs_FF = [
            {"field": col, "hide": col == "location_name", "cellRenderer": "function(params) { return params.value.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0}); }", "minWidth": 100, "editable": False, "filter": True, "resizable": True, "sortable": True}
            for col in filtered_totals_df_footfall.columns]

            grid_options_Footfalls["location_name"] = column_defs_FF
            
            
            #Replace NaN and inf values with a specific value (e.g., 0)
            filtered_totals_df_footfall = filtered_totals_df_footfall.replace([np.inf, -np.inf, np.nan], 0)
            
            # Convert specific columns to integers
            int_columns_FF = ['MTD_Budget_Footfall','MTD_Actual_Footfall','Projected_Footfalls']
            percent_columns_FF = ['%Arch_FF']
            
            # Use .loc to set values for filtered_totals_df_footfall
            filtered_totals_df_footfall.loc[:, int_columns_FF] = filtered_totals_df_footfall[int_columns_FF].astype(int).apply(lambda x: x.apply(lambda y: '{:,}'.format(y)))
            filtered_totals_df_footfall.loc[:, percent_columns_FF] = filtered_totals_df_footfall[percent_columns_FF].apply(lambda x: x.apply(lambda y: '{:.1%}'.format(y)))
            
            
            grid_options_FF_Monthly = GridOptionsBuilder.from_dataframe(FF_pivot_Actual).build()
            grid_options_FF_Monthly['autoHeight'] = True
            grid_options_FF_Monthly['defaultColDef'] = {
                "width": 50,  # Set the width to 100 pixels for each column
                "flex": 10,  # Make the columns not flexible
                "headerClass": "blue-header" # Add a CSS class for wrapping headers
            }
            
            # Define the columnDefs to hide the 'Scheme' column
            column_defs_FF_Monthly = [
            {"field": col, "hide": col == "location_name", "cellRenderer": "function(params) { return params.value.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0}); }", "minWidth": 100, "editable": False, "filter": True, "resizable": True, "sortable": True}
            for col in FF_pivot_Actual.columns]

            grid_options_FF_Monthly["location_name"] = column_defs_FF_Monthly
            

            # Custom CSS for styling the header
            custom_css_revenue = """
            <style>
                .revenue-header {
                    background-color: #073763db !important;  /* Blue fill color */
                    color: #fff !important;  /* White text color */
                }
            </style>

            """
            
            # Line chart for Revenue over time
            fig_line_chart_revenue = px.area(df_filtered, x='bill_date', y='Revenue',
                                            title=f'Daily Revenue Over Time for {selected_location}',
                                            labels={'Revenue': 'Revenue'}, line_shape="linear")

            # Reduce the height of the chart
            fig_line_chart_revenue.update_layout(height=250)  # Adjust the height value as needed

            fig_line_chart_footfalls = px.area(df_filtered, x='bill_date', y='Footfall',
                                            title=f'Daily Footfalls trend for {selected_location}',
                                            labels={'Footfall': 'Footfall'}, line_shape="linear")
            # Show the figure

            # Create a single column for the button
            col1 = st.columns(1)[0]

            # Add solid boundary style
            card_style3 = "border: 2px solid #000000; border-radius: 5px; padding: 5px; background-color:#ffffff; color:#000000; text-align: center; font-size: 15px;font-weight: bold;"

            
            #Create two columns for the buttons
            col1, col2, col3 = st.columns(3)
            
            # Add solid boundary style
            card_style = "border: 0px solid #00; border-radius: 10px; padding: 10px; background-color:#073763db; color:#fff; text-align: center; font-size: 15px;font-weight: bold;"
                # Add solid boundary style
            card_style1 = "border: 0px solid #00; border-radius: 10px; padding: 10px; background-color: #327e0adb; color:#fff; text-align: center; font-size: 25px; font-weight: bold;"


            # Initialize selected_period
            #st.plotly_chart(fig_line_chart_revenue)
            st.write("MTD-Revenue Table")
            ag_grid_html = AgGrid(
                filtered_totals_df_revenue,
                gridOptions=grid_options_Revenue,
                update_mode=GridUpdateMode.MODEL_CHANGED,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                height=210,
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'center'
                    } for c in filtered_totals_df_revenue.columns
                ],
                style_header={
                    'backgroundColor': 'blue',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'padding': '8px'
                },
                style_header_conditional=[
                    {
                        'if': {'header_index': 0},
                        'backgroundColor': '#0056b3'  # Darker blue for the first header
                    }
                ]
            )

            fig_request_by_type_ff = go.Figure(data=[go.Table(
                        header=dict(values=['Scheme','MTD_Budget_Footfall','MTD_Actual_Footfall','%Arch_FF','Projected_Footfalls'],
                                    fill_color='rgba(0, 84, 0, 1)',
                                    align='left',
                                    font=dict(color='White', size=18),
                                    line_color='darkslategray',  # Border color
                                    line=dict(width=1)),  # Border width
                        cells=dict(values=[filtered_totals_df_footfall["Scheme"],filtered_totals_df_footfall["MTD_Budget_Footfall"],filtered_totals_df_footfall["MTD_Actual_Footfall"],filtered_totals_df_footfall["%Arch_FF"],filtered_totals_df_footfall["Projected_Footfalls"]],
                                fill_color=[
                                        ['rgba(0, 0, 82, 1)'],  # Blue for "Report" column
                                        ['white'] * len(filtered_totals_df_footfall)  # White for "Count" column
                                    ],
                                font_color=[
                                        ['white'],  # Blue for "Report" column
                                        ['black'] * len(filtered_totals_df_footfall)  # White for "Count" column
                                    ],
                                align='left',
                                font=dict(color='black', size=18),
                                line_color='darkslategray',
                                height=30,# Border color
                                line=dict(width=1)))  # Border width
                    ])
                        
            
                
            # Display Table
            with st.expander("MTD FOOTFALL TABLE"):
                 st.plotly_chart(fig_request_by_type_ff, use_container_width=True)
      

            fig_request_by_type_Rev = go.Figure(data=[go.Table(
                header=dict(values=['Scheme','MTD_Budget_Revenue','MTD_Actual_Revenue','%Arch_REV','Projected_Revenue'],
                            fill_color='rgba(0, 84, 0, 1)',
                            align='left',
                            font=dict(color='White', size=18),
                            line_color='darkslategray',  # Border color
                            line=dict(width=1)),  # Border width
                cells=dict(values=[filtered_totals_df_revenue["Scheme"],filtered_totals_df_revenue["MTD_Budget_Revenue"],filtered_totals_df_revenue["MTD_Actual_Revenue"],filtered_totals_df_revenue["%Arch_REV"],filtered_totals_df_revenue["Projected_Revenue"]],
                        fill_color=[
                                ['rgba(0, 0, 82, 1)'],  # Blue for "Report" column
                                ['white'] * len(filtered_totals_df_revenue)  # White for "Count" column
                            ],
                        font_color=[
                                ['white'],  # Blue for "Report" column
                                ['black'] * len(filtered_totals_df_revenue)  # White for "Count" column
                            ],
                        align='left',
                        font=dict(color='black', size=18),
                        line_color='darkslategray',
                        height=30,# Border color
                        line=dict(width=1)))  # Border width
            ])

         # Display Table
            # Use the expander widget
            with st.expander("MTD REVENUE TABLE",):
                # Set the height of the expander
                st.plotly_chart(fig_request_by_type_Rev, use_container_width=True)



























            st.write("MTD-Footfalls")
            #st.plotly_chart(fig_line_chart_footfalls)
            ag_grid_html = AgGrid(filtered_totals_df_footfall,gridOptions=grid_options_Footfalls,
                update_mode=GridUpdateMode.MODEL_CHANGED, 
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED, 
                style={"backgroundColor": "blue", "color": "white", "fontWeight": "bold"},
                height=210)
            
            
            st.write("MONTHLY SUMMARY -Revenue ")
            #st.plotly_chart(fig_line_chart_footfalls)
            st.write(RR_pivot_Actual)
            
            
            st.write("MONTHLY SUMMARY -Footfalls ")
            #st.plotly_chart(fig_line_chart_footfalls)
            st.write(FF_pivot_Actual)
            
            # Execute a query to select all rows from the credential table
            cursor.execute("SELECT * FROM credentials")

            # Fetch all rows from the result set
            results = cursor.fetchall()

            form_container.empty()
            # Close the cursor and connection
            cursor.close()
            connection.close()

        else:
            st.error("Connection to the database failed.")
            
            
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

        # Specify column names to import
        selected_columns = ["Dateofreport",
                            "Typeofmaintenance",
                            "Details",
                            "Month",
                            "Approval",
                            "FacilityCoordinatorApproval",
                            "FacilitycoordinatorComments",
                            "Approvedammount",
                            "Receivedstatus",
                            "ReceivedAmmount",
                            "Maintenancestatus",
                            "ProjectsApproval",
                            "ProjectComments",
                            "AdminApproval",
                            "AdminComments",
                            "FinanceApproval",
                            "FinanceComment",
                            "FacilityApproval",
                            "Approver",
                            "Clinic2",
                            "Report",
                            "Region2",
                            "CentreManager2",
                            "Department",
                            "EmailId",
                            "Qty",
                            "FacilityQty",
                            "ProjectsQty",
                            "AdminQty",
                            "Laborcost",
                            "MainItem",
                            "Days_x0020_Pending",
                            "Created"
                            ]

        # Convert selected columns to a DataFrame
        data = []
        for item in items:
            item_data = {key: item.properties[key] for key in selected_columns}
            data.append(item_data)
        return pd.DataFrame(data)

    except Exception as e:
        st.error("Failed to load data from SharePoint. Please check your credentials and try again.")
        st.error(f"Error details: {e}")
        return None


def maintenance():
    st.session_state.is_authenticated=False


    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up", "Log Out"]
        choice = st.sidebar.selectbox("", menu)

        form_container = st.empty()
        with form_container :
            host = '127.0.0.1'
            port = 3306
            database = 'blisshealthcare'
            user = 'root'
            password = 'buluma'

            # Connect to the MySQL server
            connection = mysql.connector.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                allow_local_infile=True
            )
            # Query to select all columns from the facilities table
            query = "SELECT * FROM facilities"

            # Load data into a DataFrame
            location_df = pd.read_sql(query, con=connection)

            cursor = connection.cursor()

            def create_usertable():
                cursor.execute('CREATE TABLE IF NOT EXISTS usertable (staff_id INT PRIMARY KEY AUTO_INCREMENT, staffnumber INT, password TEXT, location TEXT, region TEXT)')

            def add_userdata(staffnumber, password, location, region):
                cursor.execute('INSERT INTO usertable (staffnumber, password, location, region) VALUES (%s, %s, %s, %s)', (staffnumber, password, location, region))
                connection.commit()

            def get_facilities(staffnumber):
                query = "SELECT * FROM usertable WHERE staffnumber = %s"
                params = (staffnumber,)
                Login_df = pd.read_sql(query, params=params, con=connection)
                return Login_df

            def login_user(staffnumber, password):
                # Fetch location and region based on staffnumber
                facilities_df = get_facilities(staffnumber)

                if not facilities_df.empty:
                    location = facilities_df['location'].iloc[0]
                    region = facilities_df['region'].iloc[0]

                    # Check if the credentials match
                    cursor.execute('SELECT * FROM usertable WHERE staffnumber = %s AND password = %s', (staffnumber, password))
                    data = cursor.fetchall()
                    return data, location, region
                else:
                    return None, None, None

            def view_all_users():
                cursor.execute('SELECT * FROM usertable')
                data = cursor.fetchall()
                return data

            # Fetch locations from the database
            cursor.execute("SELECT Location FROM facilities")
            locations = cursor.fetchall()
            location_names = [location[0] for location in locations]

                        # log in app
            
            if choice == "Log Out":
                st.subheader("Log Out")

            elif choice == "Login":
                # Check if the user is logged in
                

                with st.form("Login Form"):
                    st.write("Login Form")
                    staffnumber = st.text_input("Staffnumber")
                    password = st.text_input("Password", type='password')
                    # Fetch location and region based on staffnumber
                    load=st.form_submit_button("Login")
                    facilities_df = get_facilities(staffnumber)
                    if not facilities_df.empty:
                        location = facilities_df['location'].iloc[0]
                        region = facilities_df['region'].iloc[0]
                    
                    if "logged_in" not in st.session_state:
                        st.session_state.logged_in= False
                        
                    if load or st.session_state.logged_in:
                        st.session_state.logged_in= True
                        create_usertable() 
                        result, location, region = login_user(staffnumber, password)
                        if result:
                            st.success("Logged In successfully")
                            st.write(f"Location: {location}, Region: {region}")
                            st.session_state.is_authenticated=True

                            form_container.empty()

                        else:
                            st.warning("Invalid credentials. Please try again.")

            elif choice == "Sign up":
                with st.form("Sign-up Form"):
                    st.write("Sign-up Form")
                    new_user = st.text_input("Staffnumber")
                    new_password = st.text_input("Password", type='password')
                    location = st.selectbox("Select Location", location_names)
                    selected_location_row = location_df[location_df['Location'] == location]
                    region = selected_location_row['Region'].iloc[0] if not selected_location_row.empty else None

                    if st.form_submit_button("Sign up"):
                        create_usertable()
                        add_userdata(new_user, new_password, location, region)
                        st.success("You have created a new account")
                        st.session_state["logged_in"] == "True"
                        st.session_state.is_authenticated=True
                        form_container.empty()
    
                     
    if st.session_state.is_authenticated:
        form_container.empty()                   
    
        sharepoint_url = "https://blissgvske.sharepoint.com/sites/BlissHealthcareReports"
        list_name_maintenance_report = "Maintenance Report"
        list_name_maintenance_tracker = "Maintenance Tracker"

        
        # Hardcoded email and password
        email_user = "biosafety@blisshealthcare.co.ke"
        password_user = "NaSi#2024"

        # Authentication and connection to SharePoint
        Main_df = load_data(email_user, password_user, sharepoint_url, list_name_maintenance_report)
        Maintenance_tracker_df = load_data(email_user, password_user, sharepoint_url, list_name_maintenance_tracker)
        if Main_df is not None and Maintenance_tracker_df is not None:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                Region = st.selectbox("Region:", options=[""] + list(Main_df["Region2"].unique()))
                st.markdown("<style>div[data-baseweb='card'] {background-color: blue !important;}</style>", unsafe_allow_html=True)
            with col2:
                Location = st.selectbox("Medical Centre:", options=[""] + list(Main_df["Clinic2"].unique()))
            with col3:
                Status = st.selectbox("Request Status:", options=[""] + list(Main_df["Maintenancestatus"].unique()))

            if Region == "" and Location == "" and Status == "":
                df_mainselected = Main_df
            else:
                df_mainselected = Main_df.query("Clinic2 == @Location or Region2 == @Region or Maintenancestatus == @Status")

            Total_requests = int(df_mainselected.shape[0])  # Count all rows in the filtered DataFrame

            # Filter the DataFrame to include only rows where "Maintenancestatus" is "Pending"
            pending_requests_calc = df_mainselected[df_mainselected["Maintenancestatus"] == "Pending"]

            # Count the number of rows in the filtered DataFrame
            pending_request = int(pending_requests_calc.shape[0])

            # Filter the DataFrame to include only rows where "Maintenancestatus" is "Closed"
            closed_requests_calc = df_mainselected[df_mainselected["Maintenancestatus"] == "Closed"]

            # Count the number of rows in the filtered DataFrame
            closed_request = int(closed_requests_calc.shape[0])

            # Filter out rows with non-numeric values in "Days_x0020_Pending" column
            numeric_days_pending = df_mainselected["Days_x0020_Pending"].apply(pd.to_numeric, errors="coerce")
            df_mainselected["Days_x0020_Pending"] = numeric_days_pending
            df_mainselected.dropna(subset=["Days_x0020_Pending"], inplace=True)

            # Calculate average days pending
            Average_Days_pending = int(df_mainselected["Days_x0020_Pending"].mean())
            
            # Display Table
            with st.expander("View Table"):
                st.dataframe(df_mainselected, use_container_width=True)
                
           # Define the metrics
            metrics = [
                {"label": "Total", "value": Total_requests},
                {"label": "Closed", "value": closed_request},
                {"label": "Pending", "value": pending_request},
                {"label": "TAT(days)", "value": Average_Days_pending}
            ]

            # Create the data cards
            fig_data_cards = go.Figure()

            for i, metric in enumerate(metrics):
                fig_data_cards.add_trace(go.Indicator(
                    mode="number",
                    value=metric["value"],
                    number={'font': {'size': 25, 'color': 'white'}},
                    domain={'row': i, 'column': 0},  # Set the row and column to stack vertically
                    title={'text': metric["label"],'font': {'size': 20,'color': 'white'}},
                    align="center"
                ))

            # Update layout
            fig_data_cards.update_layout(
                grid={'rows': len(metrics), 'columns': 1, 'pattern': "independent"},
                template="plotly_white",
                height=100*len(metrics),  # Adjust the height based on the number of metrics
                paper_bgcolor='rgba(0, 131, 184, 1)',  # Set background color to transparent
                plot_bgcolor='rgba(0, 137, 184, 1)',   # Set plot area background color to transparent
                uniformtext=dict(minsize=40, mode='hide'),
                margin=dict(l=20, r=20, t=50, b=5)
                
                )

            st.markdown(
                """
                <style>
                .st-cd {
                    border: 1px solid #e6e9ef;
                    border-radius: 5px;
                    padding: 10px;
                    margin-bottom: 10px;
                }
                </style>
                """,
                unsafe_allow_html=True
)
            with st.container():
                c1, c2, c3 = st.columns([0.5, 3, 1.5])
                # Add content to the columns
                with c1:
                    # Display the figure
                    st.plotly_chart(fig_data_cards, use_container_width=True) 
                with c2:
                    graph(df_mainselected)  # Call the graph function with df_mainselecte
                with c3:
                    graphy(df_mainselected)  # Call the graph function with df_mainselected
                    st.markdown("""<div class='.st-cd'>•</div>""", unsafe_allow_html=True)


              
def graph(df_mainselected):
    
    request_by_report = df_mainselected.groupby(by=["Typeofmaintenance"]).size().reset_index(name='Count').sort_values(by="Count", ascending=True)
    
    fig_request_by_report = px.bar(request_by_report, x="Count", y="Typeofmaintenance",
                                orientation="h", title="<b> Category of Works </b>",
                                color_discrete_sequence=["#0083b8"]*len(request_by_report), template="plotly_white")

    fig_request_by_report.update_layout(plot_bgcolor="rgba(0,255,0,0)", xaxis=dict(showgrid=True))
    
    st.plotly_chart(fig_request_by_report, use_container_width=True)
    
def graphy(df_mainselected):
    request_by_type = df_mainselected.groupby(by=["Report"]).size().reset_index(name='Count').sort_values(by="Count", ascending=False)
    
    fig_request_by_type = go.Figure(data=[go.Table(
        header=dict(values=["ITEM", "NO."],
                    fill_color='rgba(0, 131, 184, 1)',
                    align='left',
                    font=dict(color='White', size=11),
                    line_color='darkslategray',  # Border color
                    line=dict(width=1)),  # Border width
        cells=dict(values=[request_by_type["Report"], request_by_type["Count"]],
                   fill_color=[
                        ['rgba(0, 131, 184, 1)'],  # Blue for "Report" column
                        ['white'] * len(request_by_type)  # White for "Count" column
                    ],
                   font_color=[
                        ['white'],  # Blue for "Report" column
                        ['black'] * len(request_by_type)  # White for "Count" column
                    ],
                   align='left',
                   font=dict(color='black', size=11),
                   line_color='darkslategray',  # Border color
                   line=dict(width=1)))  # Border width
    ])

    fig_request_by_type.update_layout(title="<b> Type of items </b>", template="plotly_white")
    
    st.plotly_chart(fig_request_by_type, use_container_width=True)
        

with st.sidebar:
    #st.image("Dashboard/logo.png", caption="Bliss Healthcare")
        selected_page = option_menu.option_menu(
        menu_title='DASHBOARDS',
        options=['Medical centre Dashboard', 'Region Dashboard', 'Departments Dashboard', "Maintenance Dashboard", 'Summary Dashboard', 'Account'],
        icons=['house-fill', 'receipt', 'receipt', 'receipt', 'receipt', 'person-circle'],
        menu_icon='house-fill',
        default_index=0,
        styles={
            "container": {"padding": "15", "background-color": {"grey": "black", "font-size": "10px"}},
            "nav-link": {"color": "Blck", "font-size": "13px", "text-align": "left"},
            "nav-link-selected": {"background-color": "Black"}
        }
    )

if st.session_state.get('selected_page'):
    selected_page = st.session_state['selected_page']
if selected_page == "Medical centre Dashboard":
    home()
elif selected_page == "Maintenance Dashboard":
    maintenance()
else:
    pass