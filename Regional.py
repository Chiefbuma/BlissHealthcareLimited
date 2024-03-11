import streamlit as st

# Initialize connection.
conn = st.connection('mysql', type='sql')

# Perform query.
df = conn.query('SELECT * from mytable;', ttl=600)

# Print results.
for row in df.itertuples():
<<<<<<< HEAD
    st.write(f"{row.name} has a :{row.pet}:")
=======
    st.write(f"{row.Location} has a :{row.Region}:")
>>>>>>> 478a11ee7e72774671b4188cc4e65cbb189f10ac
