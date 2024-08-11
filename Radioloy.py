import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd
import numpy as np
from local_components import card_container
from streamlit_shadcn_ui import slider, input, textarea, radio_group, switch
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
from datetime import datetime, timedelta
import plotly.graph_objects as go
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import UserCredential
import streamlit_option_menu as option_menu
import streamlit_shadcn_ui as ui
from streamlit_shadcn_ui import slider, input, textarea, radio_group, switch
from sharepoint import SharePoint
from postgrest import APIError
from IPython.display import HTML
import main
from streamlit_dynamic_filters import DynamicFilters

def app():
    
    try:
        
        if 'is_authenticated' not in st.session_state:
            st.session_state.is_authenticated = False
            st.write(f"""<span style="color:red;">
                        You are not Logged in, click account to Log in/Sign up to proceed.
                    </span>""", unsafe_allow_html=True)
            
        if st.session_state.is_authenticated:
            location=st.session_state.Region
            staffnumber=st.session_state.staffnumber
            department = st.session_state.Department
            staffname=st.session_state.staffname
        
        
            with card_container(key="summary"):
            # Define the layout using `ui.input` for inputs and `st.write` for labels
                with card_container(key="rad"):
                    colz = st.columns([1,2,1])
                    with colz[1]:
                       st.markdown("### Radiology BD form")
                    # Column layout for Patient Name
                    cola = st.columns([2, 6,1])
                    with cola[0]:
                        st.write("**Patient Name:**")
                    with cola[1]:
                        PatientName = ui.input(key="Patient")
                    # Column layout for UHID
                    colb = st.columns([2, 6,1])
                    with colb[0]:
                        st.write("**UHID:**")
                    with colb[1]:
                        uhid = ui.input(key="uhid")
                    # Column layout for Modality
                    colc = st.columns([2, 6,1])
                    with colc[0]:
                        st.write("**Modality:**")
                    with colc[1]:
                        Modality = ui.input(key="Modality")

                    # Column layout for Procedure
                    cold = st.columns([2, 6,1])
                    with cold[0]:
                        st.write("**Procedure:**")
                    with cold[1]:
                        Procedure = ui.input(key="Procedure")

                    # Column layout for Referred By
                    cole = st.columns([2, 6,1])
                    with cole[0]:
                        st.write("**Referred By:**")
                    with cole[1]:
                        ReferredBy = ui.input(key="ReferredBy")

                    # Column layout for Facility
                    colf = st.columns([2, 6,1])
                    with colf[0]:
                        st.write("**Facility:**")
                    with colf[1]:
                        Facility = ui.input(key="Facility")

                    # Column layout for MPESA No
                    colg = st.columns([2, 6,1])
                    with colg[0]:
                        st.write("**MPESA No:**")
                    with colg[1]:
                        MPESA_no = ui.input(key="MPESA_no")

                    # Column layout for BD Amount
                    colh = st.columns([2, 6,1])
                    with colh[0]:
                        st.write("**BD Amount:**")
                    with colh[1]:
                        BD_amount = ui.input(key="BD_amount")

                    colj=st.columns(7)
                    with colj[3]:
                            ui_result = ui.button("Submit", key="btn")  
                            if ui_result: 
                              with st.spinner('Wait! Reloading view...'):
                                st.cache_data.clear()
        else:
            st.write("You  are  not  logged  in. Click   **[Account]**  on the  side  menu to Login  or  Signup  to proceed")
    
    
    except APIError as e:
            st.error("Cannot connect, Kindly refresh")
            st.stop() 
                   