
import streamlit as st
from st_login_form import login_form
from st_supabase_connection import SupabaseConnection


# Initialize connection.
conn = st.connection("supabase",type=SupabaseConnection)

# Perform query.
rows = conn.query("*", table="users", ttl="10m").execute()

# Print results.
for row in rows.data:
    st.write(f"{row['staffnumber']} has a :{row['region']}:")