import pandas as pd
from sqlalchemy import create_engine
import streamlit as st


# Assuming Allmerged_df is your DataFrame
# Export Allmerged_df to MySQL using SQLAlchemy
engine = create_engine(f"mysql+mysqlconnector://{'root'}:{'buluma'}@{'127.0.0.1'}:{3306}/{'blisshealthcare'}")

try:
    # Connect to the MySQL server using SQLAlchemy engine
    connection = engine.connect()
    print("Connected to MySQL")
    
    # Use the engine to execute SQL queries with pandas
    df = pd.read_sql_query('SELECT * FROM facilities', engine)
    
    st.write(df)
    print("Data loaded successfully")

except Exception as e:
    print(f"Error: {e}")

finally:
    if 'connection' in locals() and connection is not None:
        # Close the SQLAlchemy connection
        connection.close()
        print("Connection closed")
