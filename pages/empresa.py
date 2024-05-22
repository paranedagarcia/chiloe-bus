#
import os
import streamlit as st
import pandas as pd
import sqlite3
from funciones import menu_pages

# configuration
st.set_page_config(
    page_title="Chiloé buses",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# styles
with open('style/style.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# pages
menu_pages()

#main
st.title("Chiloé Bus")
st.subheader("Acceso usuario empresa")
st.write("Ingrese su usuario y contraseña para acceder a la plataforma.")
st.write("Si no tiene cuenta, por favor contacte al administrador.")
st.empty()
st.write("Esta es una página en desarrollo.")