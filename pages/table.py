#
import os
import time
import streamlit as st
import pandas as pd
import sqlite3

from funciones import menu_pages, check_password, production


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


# update database


def update_table(df, db):
    msg = st.toast('Actualizando base de datos')
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    msg.toast('Actualizando...', icon="⏳")
    cursor.execute("DELETE FROM buses")
    for index, row in df.iterrows():
        idbus = row['idbus']
        origin = row['origin']
        destination = row['destination']
        departure = row['departure']
        dayweek = row['dayweek']
        company = row['company']
        cursor.execute("INSERT INTO buses (origin, destination, departure, dayweek, company) VALUES (?, ?, ?, ?, ?)",
                       (origin, destination, departure, dayweek, company))
    conn.commit()
    conn.close()
    msg.toast('Listo!', icon="✅")


def updatedb():
    msg = st.toast('Actualizando base de datos')
    time.sleep(1)
    msg.toast('Actualizando...', icon="⏳")
    time.sleep(1)
    msg.toast('Listo!', icon="✅")


if not check_password():
    st.stop()
else:
    # sqlite connection
    # Connect to the SQLite database
    full_path = os.path.join('bus.db')
    conn = sqlite3.connect('bus.db')

    # Query the data from the database
    query = "SELECT idbus, origin, destination, departure, dayweek, company FROM buses"
    df = pd.read_sql_query(query, conn)
    conn.close()

    # df['Salida'] = pd.to_datetime(df['Salida']).dt.time
    # main page
    st.subheader("Chiloé Bus - Horario de buses")

    editable = st.data_editor(df,
                              height=550, hide_index=True, key="idbus",
                              column_config={"idbus": {"disabled": True, "editable": False, "width": 50, "label": "ID"},
                                             "origin": {"editable": True, "label": "ORIGEN"},
                                             "destination": {"editable": True, "label": "DESTINO"},
                                             "dayweek": {"editable": True, "label": "DIA", "width": "small", "default": "LUN-VIE"},
                                             "company": {"editable": True, "label": "EMPRESA", "default": "NA"},
                                             "departure": {"editable": True, "label": "SALIDA",
                                                           "format": "HH:mm", "step": 1, "time_format": "HH:mm", "width": "small",
                                                           "help": "Utilice siempre el formato HH:mm"}
                                             },
                              use_container_width=True, num_rows="dynamic", on_change=None)

    cargar = st.button("Actualizar datos a la base", type="primary")
    if cargar:
        update_table(editable, 'bus.db')
        st.rerun()
