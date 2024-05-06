#
import os
import streamlit as st
import pandas as pd
import sqlite3

# configuration
st.set_page_config(
    page_title="Imagina-Planillas",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# styles
with open('style/style.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

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
    st.write("Planifique su viaje en bus dentro de Chiloé")
    # st.write("It's a good place to put widgets that control the main page")
    st.divider()
    origin = st.selectbox("Origen/Origin",
                          options=origins, index=None, key="origin", placeholder="Seleccione Origen/Origin", help="Seleccione Origen/origin")
    if origin:
        filtered_destinations = df[df['origin']
                                   == origin]['destination'].unique()
        filtered_destinations.sort()
        destination = st.selectbox("Destino/Destination",
                                   options=filtered_destinations, index=0, key="destination", placeholder="Seleccione Destino/Destination", help="Seleccione Destino/Destination")

    # destination = st.selectbox("Destino/Destination",
    #                            options=destinations, index=None, key="destination", placeholder="Seleccione Destino/Destination", help="Seleccione Destino/Destination")
    dayweek = st.multiselect("Select Day of the week", options=dayweeks,
                             key="dayweek", default=dayweeks)

    buslist = st.button("List Buses", type="primary")

# main page
st.subheader("Chiloé Bus")


if origin and destination and dayweek:
    df.drop(['idbus', 'value'], axis=1, inplace=True)
    filtered_df = df[(df['origin'] == origin) & (
        df['destination'] == destination) & (df['dayweek'].isin(dayweek))]
    filtered_df.sort_values(by=['dayweek', 'departure'], inplace=True)
    # rename the columns of the dataframe 'df'
    filtered_df.rename(columns={'origin': 'Origen',
                       'destination': 'Destino',
                                'departure': 'Salida',
                                'arrival': 'Llegada/',
                                'dayweek': 'Día',
                                # 'value': 'Valor',
                                'contact': 'Contacto',
                                'company': 'Compañía'}, inplace=True)

    st.dataframe(filtered_df, height=550)
