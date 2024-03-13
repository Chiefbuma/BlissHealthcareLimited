
import streamlit as st

# Initialize connection.
conn = st.connection('mysql', type='sql')

# Perform query.
query = 'SELECT * FROM facilities;'
df = conn.query(query, ttl=600)

# Display the DataFrame.
<<<<<<< HEAD
st.write(df)
=======
st.write(df)

