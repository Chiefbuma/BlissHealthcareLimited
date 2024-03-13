import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

# Load database credentials from Streamlit Secrets
secrets = st.secrets["database"]
username = secrets["db_username"]
password = secrets["db_password"]
host = secrets["db_host"]
port = secrets["db_port"]
database_name = secrets["db_name"]

# Export Allmerged_df to MySQL using SQLAlchemy
engine = create_engine(f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database_name}")

try:
    # Connect to the MySQL server using SQLAlchemy engine
    connection = engine.connect()
    print("Connected to MySQL")
    
    # Use the engine to execute SQL queries with pandas
    df = pd.read_sql_query('SELECT * FROM facilities', engine)
    
    st.write(df)
    print("Data loaded successfully")
    st.write(df)

except Exception as e:
    print(f"Error: {e}")

finally:
    if 'connection' in locals() and connection is not None:
        # Do not close the SQLAlchemy connection
        print("Connection not closed")

# Streamlit will keep running until the user closes the app
