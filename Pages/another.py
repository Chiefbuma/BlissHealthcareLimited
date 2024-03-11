import streamlit as st

# Define a function to create the container
def create_container():
    # Generate a unique ID for the container
    container_id = st.markdown('', unsafe_allow_html=True).empty()

    # Return the container ID
    return container_id

# Define a function to insert elements into the container
def insert_element(container_id, element_html):
    # Insert the element HTML into the container
    container_id.markdown(element_html, unsafe_allow_html=True)

# Create a container
container_id = create_container()

# Insert elements into the container
insert_element(container_id, '<h1 style="color: blue;">Header 1</h1>')
insert_element(container_id, '<p style="font-size: 16px;">Paragraph 1</p>')
insert_element(container_id, '<h2 style="color: green;">Header 2</h2>')
insert_element(container_id, '<p style="font-size: 14px;">Paragraph 2</p>')
