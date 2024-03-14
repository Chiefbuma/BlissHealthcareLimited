import streamlit as st
import pymssql

# Initialize connection.
# Uses st.cache_resource to only run once.
conn = pymssql.connect(server='169.254.127.154', user='sa', password='buluma', database='mydb', port=1433)

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

rows = run_query("SELECT * from mytable;")

# Print results.
for row in rows:
    st.write(f"{row[0]} has a :{row[1]}:")
