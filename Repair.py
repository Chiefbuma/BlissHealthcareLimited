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
from st_aggrid import AgGrid, GridOptionsBuilder,JsCode



def app():
    
    try:

        if 'is_authenticated' not in st.session_state:
            st.session_state.is_authenticated = False 
            st.write(f"""<span style="color: red;">
                        You are not Logged in,click account to  Log in/Sign up to proceed.
                    </span>""", unsafe_allow_html=True)
        
            # Initialize session state if it doesn't exist
                    
        if st.session_state.is_authenticated:
            
            # get clients sharepoint list
            st.cache_data(ttl=80, max_entries=2000, show_spinner=False, persist=False, experimental_allow_widgets=False)
            def load_new():
                columns = [
                    "Title",
                    "Edit",
                    "Region",
                    "Name of Staff",
                    "Department",
                    "Date Number ",
                    "Details",
                    "Date of report",
                    "Departmental report",
                    "Report",
                    "MainItem",
                    "Total cost",
                    "Labor cost",
                    "Centre Qty",
                    "Rate",
                    "Clinic",
                    "MainLINK",
                    "QUOTES",
                    "PHOTOS",
                    "Month",
                    "Approval",
                    "Facility Coordinator  Approval",
                    "Facility comments",
                    "Facility Qty",
                    "Facility Rate",
                    "Facility Total",
                    "Facility amount",
                    "Time Line",
                    "Approved amount",
                    "Received status",
                    "Received Amount",
                    "MainStatus",
                    "Projects Approval",
                    "Project Comments",
                    "Projects Total",
                    "Project amount",
                    "Projects Qty",
                    "Project Rate",
                    "Admin Approval",
                    "Admin amount",
                    "Admin Comments",
                    "Admin Qty",
                    "Admin Rate",
                    "Admin Total",
                    "Director amount",
                    "Director Approval",
                    "Director Qty",
                    "Director Total",
                    "Director Rate",
                    "Director Comments",
                    "Centre Manager Approval",
                    "Centre Manager Comment",
                    "STATUS",
                    "MainLink flow",
                    "Facility Flow",
                    "Project flow",
                    "Admin flow",
                    "Centre flow",
                    "Facility Approval",
                    "Approver",
                    "LinkEdit",
                    "UpdateLink",
                    "DesignLINK",
                    "ID",
                    "TYPE",
                    "PhotoLINK",
                    "Days",
                    "Email",
                    "MAINTYPE",
                    "Confirmed"

                ]
                
                try:
                    clients = SharePoint().connect_to_list(ls_name='Maintenance Tracker', columns=columns)
                    df = pd.DataFrame(clients)
                    
                    # Ensure all specified columns are in the DataFrame, even if empty
                    for col in columns:
                        if col not in df.columns:
                            df[col] = None

                    return df
                except APIError as e:
                    st.error("Connection not available, check connection")
                    st.stop()
                    
            Main_df = load_new()
            
            #st.write(Main_df)
           
                                # JavaScript for link renderer
            cellRenderer_link = JsCode("""
            class LinkRenderer {
                init(params) {
                    this.params = params;
                    this.eGui = document.createElement('a');
                    this.eGui.innerHTML = 'View Prescription';
                    this.eGui.href = 'javascript:void(0)';
                    this.eGui.addEventListener('click', () => {
                        const selectedCategory = params.data.Patientname;
                        window.parent.postMessage({ type: 'VIEW_CHILD_GRID', category: selectedCategory }, '*');
                    });
                }
                getGui() {
                    return this.eGui;
                }
            }
            """)

            # JavaScript for checkbox renderer
            checkbox_renderer = JsCode("""
            class CheckboxRenderer {
                init(params) {
                    this.params = params;
                    this.eGui = document.createElement('input');
                    this.eGui.setAttribute('type', 'checkbox');
                    
                    // Default the checkbox to unchecked
                    this.eGui.checked = params.value === '';
                    
                    this.eGui.addEventListener('click', (event) => {
                        if (event.target.checked) {
                            params.setValue('Received');
                        } else {
                            params.setValue('');
                        }
                    });
                }

                getGui() {
                    return this.eGui;
                }

                refresh(params) {
                    // Update the checkbox state when the cell is refreshed
                    this.eGui.checked = params.value === 'Received';
                }
            }
            """)
            
            
            # JavaScript for checkbox renderer
            checkbox_renderer2 = JsCode("""
            class CheckboxRenderer {
                init(params) {
                    this.params = params;
                    this.eGui = document.createElement('input');
                    this.eGui.setAttribute('type', 'checkbox');
                    
                    // Default the checkbox to unchecked
                    this.eGui.checked = params.value === '';
                    
                    this.eGui.addEventListener('click', (event) => {
                        if (event.target.checked) {
                            params.setValue('Transferred');
                        } else {
                            params.setValue('');
                        }
                    });
                }

                getGui() {
                    return this.eGui;
                }

                refresh(params) {
                    // Update the checkbox state when the cell is refreshed
                    this.eGui.checked = params.value === 'Transferred';
                }
            }
            """)
            
            textarea_renderer = JsCode("""
                class TextareaRenderer {
                    init(params) {
                        this.params = params;
                        this.eGui = document.createElement('textarea');
                        
                        // Set the width and height of the textarea
                        this.eGui.style.width = '120px'; // Adjust the width as needed
                        this.eGui.style.height = '20px'; // Adjust the height as needed

                        this.eGui.value = this.params.value || '';

                        this.eGui.addEventListener('change', (event) => {
                            this.params.setValue(event.target.value);
                        });
                    }

                    getGui() {
                        return this.eGui;
                    }
                }
                """)

            # JavaScript for date renderer
            date_renderer = JsCode("""
            class DateRenderer {
                init(params) {
                    this.params = params;
                    this.eGui = document.createElement('input');
                    this.eGui.type = 'date';
                    if (params.value) {
                        this.eGui.value = params.value;
                    }
                    this.eGui.addEventListener('change', e => {
                        this.params.node.setDataValue(this.params.colDef.field, e.target.value);
                    });
                }
                getGui() {
                    return this.eGui;
                }
            }
            """)
            
            #st.write(Main_df)
            
            cols=st.columns([1,2,1])
            
            with cols[1]:
                   
                with card_container(key="Main1"):
                       
                        with card_container(key="Main3"):
            
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
                            
                            
                            d = {
                                    "Title": [''],
                                    "Edit": [''],
                                    "Region": [''],
                                    "Name of Staff": [''],
                                    "Department": [''],
                                    "Date Number ": [''],
                                    "Details": [''],
                                    "Date of report": [''],
                                    "Departmental report": [''],
                                    "Report": [''],
                                    "MainItem": [''],
                                    "Total cost": [''],
                                    "Labor cost": [''],
                                    "Centre Qty": [''],
                                    "Rate": [''],
                                    "Clinic": [''],
                                    "MainLINK": [''],
                                    "QUOTES": [''],
                                    "PHOTOS": [''],
                                    "Month": [''],
                                    "Approval": [''],
                                    "Facility Coordinator  Approval": [''],
                                    "Facility comments": [''],
                                    "Facility Qty": [''],
                                    "Facility Rate": [''],
                                    "Facility Total": [''],
                                    "Facility amount": [''],
                                    "Time Line": [''],
                                    "Approved amount": [''],
                                    "Received status": [''],
                                    "Received Amount": [''],
                                    "MainStatus": [''],
                                    "Projects Approval": [''],
                                    "Project Comments": [''],
                                    "Projects Total": [''],
                                    "Project amount": [''],
                                    "Projects Qty": [''],
                                    "Project Rate": [''],
                                    "Admin Approval": [''],
                                    "Admin amount": [''],
                                    "Admin Comments": [''],
                                    "Admin Qty": [''],
                                    "Admin Rate": [''],
                                    "Admin Total": [''],
                                    "Director amount": [''],
                                    "Director Approval": [''],
                                    "Director Qty": [''],
                                    "Director Total": [''],
                                    "Director Rate": [''],
                                    "Director Comments": [''],
                                    "Centre Manager Approval": [''],
                                    "Centre Manager Comment": [''],
                                    "STATUS": [''],
                                    "MainLink flow": [''],
                                    "Facility Flow": [''],
                                    "Project flow": [''],
                                    "Admin flow": [''],
                                    "Centre flow": [''],
                                    "Facility Approval": [''],
                                    "Approver": [''],
                                    "LinkEdit": [''],
                                    "UpdateLink": [''],
                                    "DesignLINK": [''],
                                    "ID": [''],
                                    "TYPE": [''],
                                    "PhotoLINK": [''],
                                    "Days": [''],
                                    "Email": [''],
                                    "MAINTYPE": [''],
                                    "Confirmed": ['']
                                }
                            df = pd.DataFrame(data = d)
                            
                            df = df.rename(columns={
                                  'MainItem':'Item',
                               'Centre Qty':'Qty',
                               'Total cost':'Total'
                               
                               })
                            # Display the Dataframe in AgGrid
                            #AgGrid(df)

                            # JavaScript function to add a new row to the AgGrid table
                            js_add_row = JsCode("""
                            function(e) {
                                let api = e.api;
                                let rowPos = e.rowIndex + 1; 
                                api.applyTransaction({addIndex: rowPos, add: [{}]})    
                            };
                            """     
                            )
                            
                            cellRenderer_addButton = JsCode('''
                                     class BtnCellRenderer {
                                        init(params) {
                                            this.params = params;
                                            this.eGui = document.createElement('div');
                                            this.eGui.innerHTML = `
                                            <span>
                                                <style>
                                                .btn_add {
                                                    background-color: #71DC87;
                                                    border: 2px solid black;
                                                    color: black;
                                                    text-align: center;
                                                    display: inline-block;
                                                    font-size: 20px; /* Adjust font size as needed */
                                                    font-weight: bold;
                                                    height: 2em; /* Adjust height as needed */
                                                    width: 2em; /* Adjust width as needed */
                                                    border-radius: 50%; /* Make it a circle */
                                                    padding: 0px;
                                                    line-height: 2em; /* Vertically center text */
                                                    cursor: pointer; /* Show pointer cursor on hover */
                                                }
                                                </style>
                                                <div id='click-button' class="btn_add">&#43;</div> <!-- Plus sign -->
                                            </span>
                                            `;
                                        }
                                        getGui() {
                                            return this.eGui;
                                        }
                                    };
                                ''')
                            # Create a GridOptionsBuilder object from our DataFrame
                            gd = GridOptionsBuilder.from_dataframe(df)
                            
                             # List of columns to hide
                            book_columns = ["Title", "Edit", "Region", 
                                            "Name of Staff", "Department",
                                            "Date Number ", "Details", "Date of report",
                                            "Departmental report", "Report",
                                            "Labor cost", "Clinic", "MainLINK", 
                                            "QUOTES", "PHOTOS", "Month", "Approval",
                                            "Facility Coordinator Approval", "Facility comments",
                                            "Facility Qty", "Facility Rate", "Facility Total",
                                            "Facility amount", "Time Line", "Approved amount", 
                                            "Received status", "Received Amount", "MainStatus",
                                            "Projects Approval", "Project Comments",
                                            "Projects Total", "Project amount", "Projects Qty",
                                            "Project Rate", "Admin Approval", "Admin amount",
                                            "Admin Comments", "Admin Qty", "Admin Rate", "Admin Total",
                                            "Director amount", "Director Approval", "Director Qty",
                                            "Director Total", "Director Rate", "Director Comments",
                                            "Centre Manager Approval", "Centre Manager Comment", 
                                            "STATUS", "MainLink flow", "Facility Flow", "Project flow",
                                            "Admin flow", "Centre flow", "Facility Approval", "Approver",
                                            "LinkEdit", "UpdateLink", "DesignLINK", "ID", "TYPE",
                                            "PhotoLINK", "Days", "Email", "MAINTYPE", "Confirmed","Facility Coordinator  Approval"
                               
                            ]
                            
                            # Hide specified columns
                            for col in book_columns:
                                gd.configure_column(field=col, hide=True, pinned='right')

                            # Configure the default column to be editable
                            # sets the editable option to True for all columns
                            gd.configure_default_column(editable=True)

                            # Configure the '🔧' column to use our the cell renderer 
                            # and onCellClicked function
                            gd.configure_column( field = 'Add', 
                                                onCellClicked = js_add_row,
                                                cellRenderer = cellRenderer_addButton
                                                )
                            gridoptions = gd.build()

                            with st.form('Work Order form') as f:
                                st.write("Work Oder form")
                                
                                response = AgGrid(df,
                                                gridOptions = gridoptions, 
                                                editable=True,
                                                allow_unsafe_jscode = True, 
                                                theme = 'balham',
                                                height = 200,
                                                fit_columns_on_grid_load = True)
                                st.write(" *Note: Don't forget to hit enter ↩ on new entry.*")
                                st.form_submit_button("Confirm item(s) ", type="primary")

                            # Visualize the AgGrid when submit button triggered           
                            st.subheader("Updated Inventory")
                            # Fetch the data from the AgGrid Table
                            res = response['data']
                            st.table(res)
                    
                            ui_result = ui.button("Submit", key="btn2")  
                            if ui_result: 
                                with st.spinner('Wait! Reloading view...'):
                                    st.cache_data.clear()
                             
        else:
            st.write("You  are  not  logged  in. Click   **[Account]**  on the  side  menu to Login  or  Signup  to proceed")
    
    
    except APIError as e:
            st.error("Cannot connect, Kindly refresh")
            st.stop() 
