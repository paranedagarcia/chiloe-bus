import os
import streamlit as st
import pandas as pd

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

st.title("Chiloe Bus")
st.write("Planifique su viaje en bus dentro de Chiloé")
st.divider()
col1, col2, col3 = st.columns([1, 2, 1], gap="small")
col1.empty()
with col2:
    st.page_link("pages/bus.py", label="Ver horario de buses", icon="🚌")
    st.image("images/chiloe.png", width=450)
col3.empty()
