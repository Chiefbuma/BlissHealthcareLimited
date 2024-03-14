import mysql.connector
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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
import os
from sqlalchemy import create_engine



            
            
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
                            "Month",
                            "Clinic2",
                            "Region2",
                            "Typeofmaintenance",
                            "Department",
                            "Report",
                            "Details",
                            "FacilityCoordinatorApproval",
                            "FacilitycoordinatorComments",
                            "ProjectsApproval",
                            "ProjectComments",
                            "AdminApproval",
                            "AdminComments",
                            "Approvedammount",
                            "Maintenancestatus",
                            "FinanceApproval",
                            "FinanceComment",
                            "Approver",
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

elif selected_page == "Maintenance Dashboard":
    maintenance()

else:
    pass