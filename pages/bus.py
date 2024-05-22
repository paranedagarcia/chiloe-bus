#
import os
import streamlit as st
import pandas as pd
import sqlite3
from funciones import menu_pages, production

# configuration
st.set_page_config(
    page_title="Chiloé buses",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

production()

# styles
with open('style/style.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


# pages
menu_pages()

# sqlite connection
# Connect to the SQLite database
full_path = os.path.join('bus.db')
conn = sqlite3.connect('bus.db')

# Query the data from the database
query = "SELECT * FROM buses"
df = pd.read_sql_query(query, conn)
conn.close()
origins = df['origin'].unique()
origins.sort()
destinations = df['destination'].unique()
destinations.sort()
dayweeks = df['dayweek'].unique()
dayweeks.sort()


with st.sidebar:
    st.divider()
    # origin = st.selectbox("Origen/Origin",
    #                       options=origins, index=2, key="origin", placeholder="Seleccione Origen/Origin")
    # if origin:
    #     filtered_destinations = df[df['origin']
    #                                == origin]['destination'].unique()
    #     filtered_destinations.sort()
    #     destination = st.selectbox("Destino/Destination",
    #                                options=filtered_destinations, index=0, key="destination", placeholder="Seleccione Destino/Destination")

    # dayweek = st.multiselect("Día / Day", options=dayweeks,
    #                          key="dayweek", default=dayweeks)

    # buslist = st.button("Rutas / Routes", type="primary")

# main page
st.subheader("Chiloé Bus")

with st.expander("VIAJES / TRAVELS:"):
    col1, col2 = st.columns(2, gap="small")
    with col1:
        origin = st.selectbox("Origen/Origin",
                              options=origins, index=1, key="origin", placeholder="Seleccione Origen/Origin")
    with col2:
        if origin:
            filtered_destinations = df[df['origin']
                                       == origin]['destination'].unique()
            filtered_destinations.sort()
        destination = st.selectbox("Destino/Destination",
                                   options=filtered_destinations, index=0, key="destination", placeholder="Seleccione Destino/Destination")
    dayweek = st.multiselect("Día / Day", options=dayweeks,
                             key="dayweek", default=dayweeks)

if origin and destination and dayweek:
    df.drop(['idbus', 'value', 'arrival', 'contact'], axis=1, inplace=True)
    filtered_df = df[(df['origin'] == origin) & (
        df['destination'] == destination) & (df['dayweek'].isin(dayweek))]
    filtered_df.sort_values(by=['dayweek', 'departure'], inplace=True)
    # change content in column contact to a link with tel: protocol with the phone number of column contact
    # filtered_df['contact'] = filtered_df['contact'].apply(
    #   lambda x: f'<a href="tel:{x}">{x}</a>')

    filtered_df.rename(columns={'origin': 'Origen',
                                'destination': 'Destino',
                                'departure': 'Salida',
                                'dayweek': 'Día',
                                'company': 'Compañía'}, inplace=True)

    st.dataframe(filtered_df,
                 height=550, hide_index=True,
                 use_container_width=True)
