
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
>>>>>>> 750aa3c21907c68e54da850ba9e388d3d4195ee9
