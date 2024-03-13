import streamlit as st
import os

# Everything is accessible via the st.secrets dict:
st.write("DB username:", st.secrets["DB_USERNAME"])
st.write("DB password:", st.secrets["DB_TOKEN"])


# And the root-level secrets are also accessible as environment variables:
st.write(
    "Has environment variables been set:",
    os.environ["DB_USERNAME"] == st.secrets["DB_USERNAME"],
)