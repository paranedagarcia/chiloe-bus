import os
import pandas as pd
import numpy as np
import streamlit as st
import hmac
from dotenv import load_dotenv

load_dotenv()
login_pwd = os.environ["login_pwd"]


@st.cache_data
def menu_pages():

    st.sidebar.page_link("Inicio.py", label=":house: Inicio / Home")
    st.sidebar.page_link("pages/bus.py",
                         label=":bus: Viajes / Travels")
    # st.sidebar.page_link("pages/empresa.py",
    #                      label=":lock: Login empresa")
    st.sidebar.page_link("pages/table.py",
                         label=":calendar: Edición de horarios")


def link_page(page):
    st.switch_page(page)


def check_password():
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], login_pwd):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    col1, col2, col3 = st.columns([1, 3, 1], gap="small")
    col1.empty()
    with col2:
        # st.image("images/imagina-sm-logo.png")
        # st.divider()
        st.markdown(
            """Bienvenido a **Chiloé Buses**. Ingrese la contraseña para acceder a la edicion de su itinerario y rutas.""")
        st.subheader("Iniciar sesión")
        st.text_input(
            "Contraseña", type="password", on_change=password_entered, key="password")
        if "password_correct" in st.session_state:
            st.error("😕 Contraseña incorrecta")
    col3.empty()
    return False


def production():
    st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
    """, unsafe_allow_html=True)
