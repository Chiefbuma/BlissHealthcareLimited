import streamlit as st
from sqlalchemy import create_engine

# Load connection details from secrets.toml
secrets = st.secrets("secrets.toml")
mysql_url = secrets["connections"]["mysql"]["url"]

secrets = st.secrets["secrets.toml"]


# Create a SQLAlchemy engine
engine = create_engine(mysql_url)

# Create a connection
conn = engine.connect()

# Streamlit app starts here
st.title("MySQL Database Connection Example")

# Example: Query to select all columns from the facilities table
location_df = conn.execute("SELECT * FROM facilities").fetchall()

# Display the result in Streamlit
st.write("Facilities Table:")
st.write(location_df)

# ... rest of your code ...

# Close the connection when you're done
conn.close()
