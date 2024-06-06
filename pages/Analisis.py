'''
Analisis entre datasets
Fecha: 2024-06-05
Autor: Patricio Araneda
'''

# librerias
import os
import pandas as pd
import numpy as np
import time
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from funciones import menu_pages, menu_inicio
from dotenv import load_dotenv

# configuration
st.set_page_config(
    page_title="Maceda",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ESTILOS
with open('style/style.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

load_dotenv()

menu_pages()

# --------------------------
# MAIN
# --------------------------


st.subheader("Análisis entre datasets")


dataframes = ['Maceda', 'Conflictos', 'Detenciones', 'Salud']

datasets = {'dfmaceda': 'Maceda',
            'dfconflictos': 'Conflictos sociales',
            'dfdetenciones': 'Detenciones',
            'dflicencias': 'Licencias médicas'}


def format_func(option):
    return datasets[option]


with st.form("my_form"):
    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        ds1 = st.selectbox("Select option", options=list(
            datasets.keys()), format_func=format_func, key="ds1")

    with col2:
        ds2 = st.selectbox("Select option", options=list(
            datasets.keys()), format_func=format_func, key="ds2")

    with col3:
        tipo = st.selectbox("Tipo de análisis", [
                            "Provincia", "Región", "Fecha"], key="tipo")

    submitted = st.form_submit_button("Analizar")
    if submitted:
        st.write(f"seleccionado {ds1} y {ds2} / {tipo} ")

        progress_text = "Cargando datos..."

        pro_bar = st.progress(0.20, text=progress_text)

        ruta = "data/"
        comunas = pd.read_csv(ruta+"comunas.csv")
        comunas['PROVINCIA_NOMBRE'] = comunas['PROVINCIA_NOMBRE'].str.upper()
        pro_bar.progress(0.40, text="Cargando datos...")
        # MACEDA
        dfmaceda = pd.read_csv(ruta+"dataset_maceda.csv",
                               sep=";", low_memory=False)
        pro_bar.progress(0.60, text="Cargando datos...")
        # CONFLICTOS
        dfconflictos = pd.read_csv(
            ruta+"dataset_conflictos_2008-2020.csv", sep=";")
        pro_bar.progress(0.80, text="Cargando datos...")
        # LICENCIAS
        dflicencias = pd.read_csv(
            ruta+"dataset_licencias_sample.csv", low_memory=False)
        pro_bar.progress(.90, text="Cargando datos...")
        # DETENCIONES
        dfdetenciones = pd.read_csv(
            ruta+"dataset_detenciones.csv", low_memory=False)

        pro_bar.empty()
