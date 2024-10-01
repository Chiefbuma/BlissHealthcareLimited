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
from urllib.error import HTTPError
import streamlit_option_menu as option_menu
from st_aggrid import AgGrid, GridOptionsBuilder,JsCode
import streamlit.components.v1 as components


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
            location=st.session_state.Region
            staffname=st.session_state.staffname
            
            #st.write(Trans_df)
            current_date = datetime.now().date()
            formatted_date = current_date.strftime("%d/%m/%Y")
            
            textarea_renderer2 = JsCode("""
                    class SingleLineTextRenderer {
                        init(params) {
                            this.params = params;
                            this.eGui = document.createElement('input');
                            this.eGui.type = 'text'; // Set the input type to text for single-line input
                           
                            // Set the width of the input
                            this.eGui.style.width = '100px'; // Adjust the width as needed
                            this.eGui.style.height = '25px'; // Adjust the height as needed

                            // Add rounded corners using border-radius
                            this.eGui.style.borderRadius = '10px'; // Adjust the radius for more or less rounding

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
            #st.write(staffname)
            names_list = [
                "Full",
                "Partial"
    
            ]
            
            dropdown_renderer = JsCode(f"""
                class DropdownRenderer {{
                    init(params) {{
                        this.params = params;
                        this.eGui = document.createElement('select');

                        // Set the width and height of the dropdown
                        this.eGui.style.width = '120px'; // Adjust the width as needed
                        this.eGui.style.height = '25px'; // Adjust the height as needed
                        
                        // Add rounded corners using border-radius
                        this.eGui.style.borderRadius = '10px'; // Adjust the radius for more or less rounding


                        // Add an empty option as the default
                        let emptyOption = document.createElement('option');
                        emptyOption.value = '';
                        emptyOption.innerHTML = '--Select--';
                        this.eGui.appendChild(emptyOption);

                        // Add options from the predefined list
                        const options = {names_list};
                        options.forEach(option => {{
                            let optionElement = document.createElement('option');
                            optionElement.value = option;
                            optionElement.innerHTML = option;
                            this.eGui.appendChild(optionElement);
                        }});

                        this.eGui.value = this.params.value || '';

                        this.eGui.addEventListener('change', (event) => {{
                            this.params.setValue(event.target.value);
                        }});
                    }}

                    getGui() {{
                        return this.eGui;
                    }}
                }}
                """)      
            st.markdown(
                """
                <style>
                /* Apply styles to the form container */
                div[data-testid="stForm"] {
                    border: 2.0px solid black; /* Bold border */
                    padding: 10px;
                    border-radius: 10px;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
          
            
            with st.form('newoptical') as f:
                with st.container():
                    Con_label = location
                    Con_label2 = "Date"
                    cols = st.columns(6)
                
                    with cols[5]:
                        st.image("logo.png", width=150)
                    
                    with cols[2]:
                        st.markdown(
                            f"""
                           <div style="background-color:white; padding:5px; border-radius:10px; width:500px; border: 0.0px solid white; margin-bottom:5px; line-height: 4.5;">
                                <span>
                                    <div style="font-size:26px; font-weight:bold; color:black;">
                                        {Con_label}
                                    </div>
                                </span>
                            </div>
                            """, 
                            unsafe_allow_html=True
                    )
                    
                    
                    with cols[0]:
                        st.markdown(
                            f"""
                            <div style="background-color:white; padding:20px; border-radius:10px; width:500px; border: 0.0px solid white; margin-bottom:5px;">
                                <div style="font-size:20px; font-weight:bold; color:black;">
                                {Con_label2}&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:green; font-weight:bold;">{formatted_date}</span>
                                </div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                    )

                container1 = st.container(border=True, height=300)
                                
                with container1:
                    # Create four main columns for inputs
                    col1, col2, col3, col4 = st.columns([2,2,2,2])

                    with col1:
                        patient_name = st.text_input("Patient Name", key="input1")
                        membertype =st.selectbox("Member Type:", ["Scheme 1", "Scheme 2", "Scheme 3"], key="input2")
                        billammount = st.text_input("Billed Amt.:", key="input3")
                    with col2:
                        memebrnumber = st.text_input("Member No.:", key="input4")
                        Mpesa = st.text_input("Mpesa Code.:", key="input5")
                        Billnumber = st.text_input("Bill No:.", key="input6")
                    with col3:
                        phone = st.text_input("Phone", key="input7")
                        vendor_type = st.selectbox("Vendor Type:", ["Scheme 1", "Scheme 2", "Scheme 3"], key="input8")
                        discount = st.text_input("Discount Amt.", key="input9")
                    with col4:
                        scheme = st.selectbox("Scheme", ["Scheme 1", "Scheme 2", "Scheme 3"], key="input10")
                        mrn= st.text_input("MRN OR MCC:", key="input11")
                        MVCnO = st.text_input("MVC:", key="input12")
                
                # Define the columns
                columns = [
                    "DATE OF ORDER", "PATIENT NAME", "MRN OR MCC", "SPECIAL REMARKS" ,"PRODUCT TYPE", "BRANCH", "SIDE",
                    "SIMPLE CODE", "SEARCH NAME", "SPHERE", "CYLINDER", "AXIS", "ADDITION", "QTY", "HEIGHT", "PD", "SHAPE",
                    "FRAME TYPE", "A", "DBL", "B", "SCHEME", "FRAME SELECTION TYPE", "VENDOR TYPE", "NAME OF STAFF",
                    "ORDER STATUS", "APPROVED STATUS", "LENS PRODUCT TYPE", "PHONE", "AMT. DISCOUNTED/TOPPED",
                    "MPESA CODE", "MVC NUMBER", "BILLED AMMOUNT", "BILLING NUMBER", "MEMBER NUMBER"
                ]
                
                
                
                
                # Specify some values for certain columns
                lens_data = {
                    "DATE OF ORDER": [formatted_date, formatted_date],
                    "PATIENT NAME": [patient_name, patient_name],
                    "MRN OR MCC": [mrn, mrn],
                    "SPECIAL REMARKS": [phone, phone],
                    "BRANCH": [location, location],
                    "SIDE": ["LEFT", "RIGHT"],
                    "SEARCH NAME": [patient_name,patient_name],
                    "PRODUCT TYPE": ["LE", "LE"],
                    "SCHEME": [scheme, scheme],
                    "VENDOR TYPE": [vendor_type,vendor_type],
                    "NAME OF STAFF": [staffname, staffname],
                    "PHONE": [phone,phone],
                    "AMT. DISCOUNTED/TOPPED": [discount, discount],
                    "MPESA CODE": [Mpesa, Mpesa],
                    "QTY":[1,1],
                    "MVC NUMBER": [MVCnO, MVCnO],
                    "BILLED AMMOUNT": [billammount, billammount],
                    "BILLING NUMBER": [Billnumber,Billnumber],
                    "MEMBER NUMBER": [memebrnumber, memebrnumber]
                }
                
                # Specify some values for certain columns
                Frames_data = {
                    "DATE OF ORDER": [formatted_date],
                    "PATIENT NAME": [patient_name],
                    "MRN OR MCC": [mrn],
                    "SPECIAL REMARKS": [phone],
                    "BRANCH": [location],
                    "SIDE": ["FRAME"],
                    "SEARCH NAME": [patient_name],
                    "PRODUCT TYPE": ["FRM"],
                    "SCHEME": [scheme],
                    "VENDOR TYPE": [vendor_type],
                    "NAME OF STAFF": [staffname],
                    "PHONE": [phone],
                    "AMT. DISCOUNTED/TOPPED": [discount],
                    "MPESA CODE": [Mpesa],
                    "QTY":[1],
                    "MVC NUMBER": [MVCnO],
                    "BILLED AMMOUNT": [billammount],
                    "BILLING NUMBER": [Billnumber],
                    "MEMBER NUMBER": [memebrnumber]
                }
                
                
                # Create an empty DataFrame with these columns
                lens_df = pd.DataFrame(columns=columns)
                frame_df = pd.DataFrame(columns=columns)
                
                # Create a DataFrame from new_data
                framesNew_df = pd.DataFrame(Frames_data)
                
                #Create a DataFrame from new_data
                lenNew_df = pd.DataFrame(lens_data)

                # Concatenate the original DataFrame with the new DataFrame
                lens_df = pd.concat([lens_df, lenNew_df], ignore_index=True)
                
                # Concatenate the original DataFrame with the new DataFrame
                frame_df = pd.concat([frame_df, framesNew_df], ignore_index=True)

                
                
                # Configure GridOptions for the main grid
                gb = GridOptionsBuilder.from_dataframe(lens_df)
                
                book_columns = [
                    
                    "DATE OF ORDER", "PATIENT NAME", "QTY","MRN OR MCC", "SPECIAL REMARKS" ,"PRODUCT TYPE", "BRANCH",
                    "SEARCH NAME","SCHEME", "FRAME SELECTION TYPE", "VENDOR TYPE", "NAME OF STAFF","SHAPE",
                    "ORDER STATUS", "APPROVED STATUS", "LENS PRODUCT TYPE", "PHONE", "AMT. DISCOUNTED/TOPPED",
                    "MPESA CODE", "MVC NUMBER", "BILLED AMMOUNT", "BILLING NUMBER", "MEMBER NUMBER", "FRAME TYPE", "A", "DBL", "B","FRAME SELECTION TYPE"
                ]
                
                
                # Hide specified columns
                for col in book_columns:
                    gb.configure_column(field=col, hide=True, pinned='right',filter=True)
                    
                # Configuring each column individually
              
                gb.configure_column('SPHERE', editable=True, cellRenderer=textarea_renderer2, minWidth=100)
                gb.configure_column('CYLINDER', editable=True, cellRenderer=textarea_renderer2, minWidth=50)
                gb.configure_column('AXIS', editable=True, cellRenderer=textarea_renderer2, minWidth=50)
                gb.configure_column('ADDITION', editable=True, cellRenderer=textarea_renderer2, minWidth=50)
                gb.configure_column('HEIGHT', editable=True, cellRenderer=textarea_renderer2, minWidth=50)
                gb.configure_column('PD', editable=True, cellRenderer=textarea_renderer2, minWidth=50)
                gb.configure_column('SIMPLE CODE', cellEditor='agSelectCellEditor', cellEditorParams={'values': names_list}, cellRenderer=dropdown_renderer)
               

                # Build the grid options
                gridoptions = gb.build()
                
                gridoptions['suppressCellSelection'] = True
                
                container2 = st.container(border=True, height=300)
                                
                with container2:
                    st.write("*Left and Right Lens prescription")

                    # Render the filtered DataFrame with AgGrid
                    response1 = AgGrid(
                        lens_df,
                        gridOptions=gridoptions, 
                        editable=False,
                        allow_unsafe_jscode=True,
                        theme='material',
                        height=200,
                        fit_columns_on_grid_load=True,
                        key='lens_grid' 
                    )
                
                
                # Configure GridOptions for the main grid
                gd = GridOptionsBuilder.from_dataframe(frame_df)
                
                book_columns = [
                    
                    "DATE OF ORDER", "PATIENT NAME", "QTY","MRN OR MCC", "SPECIAL REMARKS" ,"PRODUCT TYPE", "BRANCH",
                    "SEARCH NAME","SCHEME", "FRAME SELECTION TYPE", "VENDOR TYPE", "NAME OF STAFF",
                    "ORDER STATUS", "APPROVED STATUS", "LENS PRODUCT TYPE", "PHONE", "AMT. DISCOUNTED/TOPPED",
                    "MPESA CODE", "MVC NUMBER", "BILLED AMMOUNT", "BILLING NUMBER", "MEMBER NUMBER",
                    "SPHERE", "CYLINDER", "AXIS", "ADDITION", "QTY", "HEIGHT", "PD"
                ]
                
                
                # Hide specified columns
                for col in book_columns:
                    gd.configure_column(field=col, hide=True, pinned='right',filter=True)
                    
                
                gd.configure_column('A', editable=True, cellRenderer=textarea_renderer2, minWidth=50)
                gd.configure_column('DBL', editable=True, cellRenderer=textarea_renderer2, minWidth=50)
                gd.configure_column('B', editable=True, cellRenderer=textarea_renderer2,minWidth=50)


                # Build the grid options
                gridoptions = gd.build()
                
                gridoptions['suppressCellSelection'] = True
                
                container3 = st.container(border=True, height=230)
                                
                with container3:
                    st.write("*Frame selection")
          
                    # Render the filtered DataFrame with AgGrid
                    response2= AgGrid(
                        frame_df,
                        gridOptions=gridoptions, 
                        editable=False,
                        allow_unsafe_jscode=True, 
                        theme='material',
                        height=130,
                        fit_columns_on_grid_load=True,
                        key='frames_grid' 
                    )
                
                # Submit button
                colj = st.columns(7)
                with colj[3]:
                    ui_result = st.form_submit_button("Confirm", type="primary")
                    if ui_result: 
                        with st.spinner('Wait! Reloading view...'):
                            st.cache_data.clear()

            #st.write(df)


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
