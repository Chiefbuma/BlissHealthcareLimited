import streamlit as st
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import plotly.graph_objects as go
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import UserCredential
import streamlit_option_menu as option_menu
import streamlit_shadcn_ui as ui
from local_components import card_container
from streamlit_shadcn_ui import slider, input, textarea, radio_group, switch
from sharepoint import SharePoint
from postgrest import APIError
from IPython.display import HTML
import main
from streamlit_dynamic_filters import DynamicFilters
from streamlit_gsheets import GSheetsConnection



def app():
    
    try:

        if 'is_authenticated' not in st.session_state:
            st.session_state.is_authenticated = False 
            st.write(f"""<span style="color: red;">
                        You are not Logged in,click account to  Log in/Sign up to proceed.
                    </span>""", unsafe_allow_html=True)
        
            # Initialize session state if it doesn't exist
                    
        if st.session_state.is_authenticated:
            
            # Display Title and Description
            st.title("New Optical Oder form")
            st.markdown("Enter the details of the new Order.")

            # Establishing a Google Sheets connection
            conn = st.experimental_connection("gsheets", type=GSheetsConnection)

            # Fetch existing vendors data
            existing_data = conn.read(worksheet="Vendors", usecols=list(range(6)), ttl=5)
            existing_data = existing_data.dropna(how="all")

            # List of Business Types and Products
            BUSINESS_TYPES = [
            "Manufacturer",
            "Distributor",
            "Wholesaler",
            "Retailer",
            "Service Provider",
            ]
            PRODUCTS = [
            "Electronics",
            "Apparel",
            "Groceries",
            "Software",
            "Other",
            ]

            # Onboarding New Vendor Form
            with st.form(key="vendor_form"):
                company_name = st.text_input(label="Company Name*")
                business_type = st.selectbox("Business Type*", options=BUSINESS_TYPES, index=None)
                products = st.multiselect("Products Offered", options=PRODUCTS)
                years_in_business = st.slider("Years in Business", 0, 50, 5)
                onboarding_date = st.date_input(label="Onboarding Date")
                additional_info = st.text_area(label="Additional Notes")

                # Mark mandatory fields
                st.markdown("**required*")

                submit_button = st.form_submit_button(label="Submit Vendor Details")

                # If the submit button is pressed
                if submit_button:
                    # Check if all mandatory fields are filled
                    if not company_name or not business_type:
                        st.warning("Ensure all mandatory fields are filled.")
                        st.stop()
                    elif existing_data["CompanyName"].str.contains(company_name).any():
                        st.warning("A vendor with this company name already exists.")
                        st.stop()
                    else:
                        # Create a new row of vendor data
                        vendor_data = pd.DataFrame(
                            [
                                {
                                    "CompanyName": company_name,
                                    "BusinessType": business_type,
                                    "Products": ", ".join(products),
                                    "YearsInBusiness": years_in_business,
                                    "OnboardingDate": onboarding_date.strftime("%Y-%m-%d"),
                                    "AdditionalInfo": additional_info,
                                }
                            ]
                        )

                        # Add the new vendor data to the existing data
                        updated_df = pd.concat([existing_data, vendor_data], ignore_index=True)

                        # Update Google Sheets with the new vendor data
                        conn.update(worksheet="Vendors", data=updated_df)

                        st.success("Vendor details successfully submitted!")
            
            
        else:
            st.write("You  are  not  logged  in. Click   **[Account]**  on the  side  menu to Login  or  Signup  to proceed")
    
    
    except APIError as e:
            st.error("Cannot connect, Kindly refresh")
            st.stop() 
