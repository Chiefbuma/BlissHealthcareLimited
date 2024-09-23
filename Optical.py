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
from postgrest import APIError
from IPython.display import HTML
import main
from streamlit_dynamic_filters import DynamicFilters
from urllib.error import HTTPError


def app():
    try:
        if 'is_authenticated' not in st.session_state:
            st.session_state.is_authenticated = False 
            st.write(
                """<span style="color: red;">
                You are not Logged in, click account to Log in/Sign up to proceed.
                </span>""", unsafe_allow_html=True
            )
        
        if st.session_state.is_authenticated:
            # Display Title and Description
            st.title("New Optical Order form")
            st.markdown("Enter the details of the new Order.")

            with card_container(key="table1"):
                with card_container(key="summary"):
# Define the layout using `ui.input` for inputs and `st.write` for labels
                    colz = st.columns([1,2,1])
                    with colz[1]:
                      st.markdown("### Maintenance Request")
                    # Column layout for Patient Name
                    cola = st.columns([2, 6,1])
                    with cola[0]:
                        st.write("**Department:**")
                    with cola[1]:
                        Department = ui.input(key="Dep")
                    # Column layout for UHID
                    colb = st.columns([2, 6,1])
                    with colb[0]:
                        st.write("**Report Type:**")
                    with colb[1]:
                        Report = ui.input(key="report")
                    # Column layout for Modality
                    colc = st.columns([2, 6,1])
                    with colc[0]:
                        st.write("**Item:**")
                    with colc[1]:
                        Item = ui.input(key="item")

                    # Column layout for Procedure
                    cold = st.columns([2, 6,1])
                    with cold[0]:
                        st.write("**Description of works:**")
                    with cold[1]:
                        description = ui.input(key="works")

                    # Column layout for Referred By
                    cole = st.columns([2, 6,1])
                    with cole[0]:
                        st.write("**Labour:**")
                    with cole[1]:
                        Labor = ui.input(key="Labor")

                    # Column layout for Facility
                    colf = st.columns([2, 6,1])
                    with colf[0]:
                        st.write("**Total Amount:**")
                    with colf[1]:
                        Total = ui.input(key="Total")

                    # Column layout for MPESA No
                    colg = st.columns([2, 6,1])
                    with colg[0]:
                        st.write("**MPESA Number.:**")
                    with colg[1]:
                        MPESA_no = ui.input(key="MPESA_no")
                    colj=st.columns(7)
                    with colj[3]:
                            ui_result = ui.button("Submit", key="btn2")  
                            if ui_result: 
                             with st.spinner('Wait! Reloading view...'):
                                st.cache_data.clear()

        else:
            st.write("You are not logged in. Click **[Account]** on the side menu to Login or Signup to proceed")
    
    except APIError as e:
        st.error("Cannot connect, Kindly refresh")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.stop()

if __name__ == "__main__":
    app()
