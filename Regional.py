import mysql.connector
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from IPython.display import display
import calendar
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from IPython.display import HTML
import streamlit as st


def app():
    
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

    #   # Create a sidebar and place widgets there
        with st.sidebar:
            st.title("SELECT DATES")

            # Dropdown for selecting the year
            current_year = datetime.now().year
            selected_year = st.selectbox("Select Year:", df_Allsales['bill_date'].dt.year.unique(), index=df_Allsales['bill_date'].dt.year.unique().tolist().index(current_year))

            # Dropdown for selecting the month
            selected_month = st.selectbox("Select Month:", df_Allsales['bill_date'].dt.month_name().unique(), index=datetime.now().month - 1)

            # Filter the DataFrame based on the selected year and month
            df_filtered = df_Allsales[
                (df_Allsales['bill_date'].dt.year == selected_year) &
                (df_Allsales['bill_date'].dt.month_name() == selected_month)
            ]

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

            # Calendar for selecting "To Date" range
            selected_to_date = st.date_input(
                "Select To Date",
                value=max_value_to_date,
                key="to_date",
                min_value=df_filtered['bill_date'].min().date() if not df_filtered.empty else datetime.now().date(),
                max_value=df_filtered['bill_date'].max().date() if not df_filtered.empty else datetime.now().date()
            )
            # Add a placeholder to prevent collapsing
            st.markdown("&nbsp;")  # You can add more spaces or content here to customize the appearance

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
        
        with st.sidebar:
            st.title("SELECT REPORTS")

            # Dropdown filter for location_name
            selected_location = st.selectbox("Select Location:", MTD_summary_df['location_name'].unique())

            # Filter the data based on the selected location, date range, and 'Scheme' column
            filtered_All_df = ALL_summary_df[
                (ALL_summary_df['location_name'] == selected_location)
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

        # Display data values in cards
        with col1:
            st.markdown(f"<div style='{card_style3}'>{f'REVENUE AND FOOTFALLS DASHBOARD <br> {selected_location}'}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            # Initialize selected_period
            selected_period = 'MTD'
        
        #Create two columns for the buttons
        col1, col2, col3 = st.columns(3)
        col1.metric(label="BUDGET", value=filtered_All_df['MTD_Budget_Revenue'].iloc[0], delta=600)
        col2.metric(label="REVENUE", value=filtered_All_df['MTD_Actual_Revenue'].iloc[0], delta=600)
        col3.metric(label="ARCHIEVEMENT", value=filtered_All_df['%Arch_REV'].iloc[0], delta=600)
        


        # Add solid boundary style
        card_style = "border: 0px solid #00; border-radius: 10px; padding: 10px; background-color:#073763db; color:#fff; text-align: center; font-size: 15px;font-weight: bold;"
            # Add solid boundary style
        card_style1 = "border: 0px solid #00; border-radius: 10px; padding: 10px; background-color: #327e0adb; color:#fff; text-align: center; font-size: 25px; font-weight: bold;"


        # Display data values in cards
        with col1:
            st.markdown(f"<div style='{card_style}'>{f'BUDGET'}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<div style='{card_style1}'>{f'{filtered_All_df['MTD_Budget_Revenue'].iloc[0]:,}'}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='{card_style}'>{f'REVENUE'}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<div style='{card_style1}'>{f"{filtered_All_df['MTD_Actual_Revenue'].iloc[0]:,}"}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div style='{card_style}'>{f'ARCHIEVEMENT'}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<div style='{card_style1}'>{f"{filtered_All_df['%Arch_REV'].iloc[0]:.1%}"}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)


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


        # Close the cursor and connection
        cursor.close()
        connection.close()

    else:
        st.error("Connection to the database failed.")
        