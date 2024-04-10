import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
import pandas as pd
import main
from datetime import datetime, timedelta

def app():
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



    