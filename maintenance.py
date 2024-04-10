import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
import pandas as pd
import plotly_express as px
from datetime import datetime, timedelta

@st.cache_resource
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

def app():
    sharepoint_url = "https://blissgvske.sharepoint.com/sites/BlissHealthcareReports"
    list_name_maintenance_report = "Maintenance Report"
    list_name_maintenance_tracker = "Maintenance Tracker"

    # Initialize session state variables
    if "email" not in st.session_state:
        st.session_state["email"] = ""
    if "password" not in st.session_state:
        st.session_state["password"] = ""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    email_user = st.session_state["email"]
    password_user = st.session_state["password"]

    # First section: e-mail and password as input
    col1, col2 = st.columns([2, 1])
    with col1:
        form_container = st.empty()
        with form_container:
            form = st.form(key="login_form")
            email_user = form.text_input("Your e-mail", key="email_input", value=email_user)
            password_user = form.text_input("Your password", type="password", key="password_input", value=password_user)
            # Save the button status
            button_pressed = form.form_submit_button("Connect")

    # Authentication and connection to SharePoint
    if button_pressed or st.session_state["logged_in"]:
        st.session_state["logged_in"] = True
        form_container.empty()
        Main_df = load_data(email_user, password_user, sharepoint_url, list_name_maintenance_report)
        Maintenance_tracker_df = load_data(email_user, password_user, sharepoint_url, list_name_maintenance_tracker)
        if Main_df is not None and Maintenance_tracker_df is not None:
            col1, col2, col3 = st.columns(3)
            with col1:
                Region = st.selectbox("Region:", options=[""] + list(Main_df["Region2"].unique()))
            with col2:
                Location = st.selectbox("Medical Centre:", options=[""] + list(Main_df["Clinic2"].unique()))
            with col3:
                Status = st.selectbox("Request Status:", options=[""] + list(Main_df["Maintenancestatus"].unique()))

            if Region == "" and Location == "" and Status == "":
                df_mainselected = Main_df
            else:
                df_mainselected = Main_df.query("Clinic2 == @Location or Region2 == @Region or Maintenancestatus == @Status")

            # Display Table
            with st.expander("View Table"):
                st.dataframe(df_mainselected, use_container_width=True)

            Total_requests = float(df_mainselected.shape[0])  # Count all rows in the filtered DataFrame

            # Filter the DataFrame to include only rows where "Maintenancestatus" is "Pending"
            pending_requests_calc = df_mainselected[df_mainselected["Maintenancestatus"] == "Pending"]

            # Count the number of rows in the filtered DataFrame
            pending_request = float(pending_requests_calc.shape[0])

            # Filter the DataFrame to include only rows where "Maintenancestatus" is "Closed"
            closed_requests_calc = df_mainselected[df_mainselected["Maintenancestatus"] == "Closed"]

            # Count the number of rows in the filtered DataFrame
            closed_request = float(closed_requests_calc.shape[0])

            # Filter out rows with non-numeric values in "Days_x0020_Pending" column
            numeric_days_pending = df_mainselected["Days_x0020_Pending"].apply(pd.to_numeric, errors="coerce")
            df_mainselected["Days_x0020_Pending"] = numeric_days_pending
            df_mainselected.dropna(subset=["Days_x0020_Pending"], inplace=True)

            # Calculate average days pending
            Average_Days_pending = float(df_mainselected["Days_x0020_Pending"].mean())

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.info("Pending Approval")
                st.metric(label="Pending Request", value=f"{pending_request:,.0f}")
            with c2:
                st.info("Approved")
                st.metric(label="Closed Request", value=f"{closed_request:,.0f}")
            with c3:
                st.info("Total")
                st.metric(label="Total Request", value=f"{Total_requests:,.0f}")
            with c4:
                st.info("Mean TAT")
                st.metric(label="Pending Average Time", value=f"{Average_Days_pending:,.0f}")

            st.markdown("""---""")
            with st.container():
                graph(df_mainselected)  # Call the graph function with df_mainselected

def graph(df_mainselected):
    request_by_type = df_mainselected.groupby(by=["Report"]).size().reset_index(name='Count').sort_values(by="Count", ascending=True)
    
    fig_request_by_type = px.bar(request_by_type, x="Count", y="Report",
                                  orientation="h", title="<b> Number of Requests by Items </b>",
                                  color_discrete_sequence=["#0083b8"]*len(request_by_type), template="plotly_white")

    fig_request_by_type.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False))
    
    
    request_by_report = df_mainselected.groupby(by=["Typeofmaintenance"]).size().reset_index(name='Count').sort_values(by="Count", ascending=True)
    
    fig_request_by_report = px.bar(request_by_report, x="Count", y="Typeofmaintenance",
                                  orientation="h", title="<b> Number of Requests by issue </b>",
                                  color_discrete_sequence=["#0083b8"]*len(request_by_report), template="plotly_white")

    fig_request_by_report.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=True))
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.plotly_chart(fig_request_by_report, use_container_width=True)
    
    with c2:
        
        st.plotly_chart(fig_request_by_type, use_container_width=True)

app()
