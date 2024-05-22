import os
import streamlit as st
import pandas as pd
from funciones import menu_pages, link_page, production

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

with st.sidebar:
    st.divider()
    st.markdown("<p><strong>Planifique su viaje dentro de Chiloé</strong></p><br>",
                unsafe_allow_html=True)
    st.empty()
    st.markdown("""<p>Seleccione el origen y destino de su viaje.</p><br>
               <p>La información es recopilada desde las fuentes del Terminal de Buses de Castro y las empresas participantes.</p><br>
               <p>Toda la información es meramente informativa y sujeta a cambios de última hora en base a factores externos y/o climáticos.</p>""", unsafe_allow_html=True)

st.markdown("# <center>Chiloé Bus</center>", unsafe_allow_html=True)
st.markdown("<center>Planifique su viaje / Planning your travel</center>",
            unsafe_allow_html=True)
# st.divider()

botonbus = st.button(":bus: Horario de buses / Bus schedule", key=None, help=None,
                     args=None, kwargs=None, type="primary", disabled=False, use_container_width=False)

if botonbus:
    link_page("pages/bus.py")
    # st.stop()

st.image("images/chiloe.jpg", width=300)

st.markdown('''<center><small>Un aporte de Dataclinica Spa
        <br> Comentarios/sugerencias a <a href="mailto:patricio@aranedagarcia.cl?subject=Chiloebus">patricio@aranedagarcia.cl</a>
        <br>
        Mayo 2024</small></center>''',
            unsafe_allow_html=True)
