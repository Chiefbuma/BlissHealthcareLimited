import streamlit as st
import mysql.connector
import sqlalchemy

# Streamlit app starts here
st.title("MySQL Database Connection Example")

conn= st.connection('sql',type='sql')


# Example: Query to select all columns from the facilities table
location_df = conn.query("SELECT * FROM facilities")

# Display the result in Streamlit
st.write("Facilities Table:")
st.write(location_df)

# ... rest of your code ...


