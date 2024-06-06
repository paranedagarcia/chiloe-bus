# salud .py
'''
Analisis de  salud mental  basado en licencias médicas otorgadas por la Superintendencia de Seguridad Social de Chile.
'''
# librerias
import os
import pandas as pd
import numpy as np
import time
import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.metric_cards import style_metric_cards

import base64
from io import BytesIO
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import FuncFormatter

from millify import millify
# import pygwalker as pgw
# from pandasai import SmartDatalake  # para multiples dataframes
from pandasai import Agent
from pandasai.llm.openai import OpenAI
from pandasai.responses.streamlit_response import StreamlitResponse

from datetime import datetime
from funciones import menu_pages, load_data_csv
from dotenv import load_dotenv


# configuration
st.set_page_config(
    page_title="Salud mental",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ESTILOS
with open('style/style.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

load_dotenv()
API_KEY = os.environ['OPENAI_API_KEY']  # st.secrets['OPENAI_API_KEY']
openai_api_key = API_KEY

menu_pages()

# public = "https://vgclabfiles.blob.core.windows.net/public/"
public = "data/"
filename = public+"dataset_licencias_sample.csv"

columnas = ['FECHA', 'LICENCIA', 'FORMULARIO', 'TRABAJADOR', 'EMISION', 'INICIO', 'DIAS', 'CODIGO', 'TIPO', 'PROFESIONAL', 'ENTIDAD', 'CAJA', 'ESTADO', 'DESDE', 'HASTA',
            'DIASAUT', 'SUBSIDIO', 'CODAUT', 'AUTORIZACION', 'CODPREV', 'RECHAZO', 'SUBCIE10', 'GRUPOCIE10', 'CIE10', 'LIQUIDO', 'SUSESO']
dtipos = {
    'FECHA': np.int16,
    'LICENCIA': str,
    'TRABAJADOR': str,
    'PROFESIONAL': str,
    'DIAS': np.int16,
    'DIASAUT': np.int16,
    'CODIGO': str,
    'CODAUT': str,
    'CODPREV': str,
}

progress_text = "Cargando datos de salud mental..."
pro_bar = st.progress(0.15, text=progress_text)

df = pd.read_csv(filename, encoding='utf-8', sep=",",
                 na_values='NA',
                 usecols=columnas,
                 dtype=dtipos
                 )
df['LIQUIDO'] = df['LIQUIDO'].fillna(0).astype(int)
df['SUSESO'] = df['SUSESO'].fillna(0).astype(int)
df['EMISION'] = pd.to_datetime(df['EMISION'])
df['DESDE'] = pd.to_datetime(df['DESDE'])
df['HASTA'] = pd.to_datetime(df['HASTA'])


# filtro por  años
# years = df['FECHA'].unique().tolist()
# years.insert(0, "Todos")
# anual = st.sidebar.selectbox("Seleccione un año", years)

# if anual is not 'Todos':
#     df = df[df["FECHA"] == anual]
# else:
#     pass

st.sidebar.subheader("Licencias médicas ")
# Filtro de rango de fechas
min_date = df['EMISION'].min()
max_date = df['EMISION'].max()
date_start = st.sidebar.date_input(
    'Emisión desde', value=pd.to_datetime(min_date))
date_end = st.sidebar.date_input(
    'Emisión hasta', value=pd.to_datetime(max_date))

df = df[
    (df['EMISION'] >= pd.to_datetime(date_start)) &
    (df['EMISION'] <= pd.to_datetime(date_end))]


# Filtro por SUBCIE10
# cie10 = df['CIE10'].unique().tolist()
# cie10.insert(0, "Todos")
# cie10_to_filter = st.sidebar.multiselect(
#     'CIE10', cie10, default="Todos")
# if cie10_to_filter is not 'Todos':
#     df = df[df["CIE10"] == cie10_to_filter]
# else:
#     pass

pro_bar.progress(0.3, text="Estableciendo métricas...")
# --------------------------
# METRICAS
# --------------------------

total_records = df.shape[0]
total_licencias = df["LICENCIA"].nunique()
total_trabajadores = df["TRABAJADOR"].nunique()
total_profesional = df["PROFESIONAL"].nunique()
total_rechazadas = df[df["ESTADO"] == "RECHAZADA"].shape[0]
total_autorizadas = df[df["ESTADO"] == "CONFIRMADA"].shape[0]

# --------------------------
# MAIN
# --------------------------
st.subheader(f"Licencias por salud mental")

tabPanel, tabTable, tabIA, tabInfo = st.tabs(
    ["Panel", "Tabla", "IA-EDA",  "Información"])

with tabPanel:
    col1, col2, col3, col4, col5 = st.columns(5, gap="medium")
    col1.metric("Licencias", millify(total_licencias, precision=2))
    col2.metric("Rechazadas", millify(total_rechazadas, precision=2))
    col3.metric("Autorizadas", millify(total_autorizadas, precision=2))
    col4.metric("Solicitantes", millify(total_trabajadores, precision=2))
    col5.metric("Profesionales", millify(total_profesional, precision=2))

    style_metric_cards()

    pro_bar.progress(0.5, text="Procesando gráficos...")
    # -------------------------------------------
    coll, colr = st.columns(2, gap="medium")

    with coll:
        fig = px.pie(df, names='ESTADO',
                     title='Estado de las licencias')
        st.plotly_chart(fig, use_container_width=True)

    with colr:
        fig = px.pie(df, names='TIPO', title='Tipo de licencia')
        st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------
    # Create a line plot for 'LIQUIDO' and 'SUSESO' based on 'FECHA'

    df['YearMonth'] = df['EMISION'].dt.to_period('M')

    df_line = df.groupby('FECHA')[['LIQUIDO', 'SUSESO']].sum().reset_index()
    fig_line = px.line(df_line, x='FECHA', y=[
                       'LIQUIDO', 'SUSESO'], title='Tendencias de pagos de licencia', markers=True)
    fig_line.update_layout(title={'xanchor': 'center', 'x': 0.5})
    st.plotly_chart(fig_line, use_container_width=True)

    # ----------------------------------------------
    # Create a line plot for 'LIQUIDO' and 'SUSESO' based on 'EMISION'
    df_liquidacion = df.groupby(
        'YearMonth')[['SUSESO']].sum().reset_index()
    # st.dataframe(licencias_por_mes)
    df_liquidacion['YearMonth'] = df_liquidacion['YearMonth'].astype(str)
    fig_mes = px.line(df_liquidacion, x='YearMonth', y='SUSESO',
                      title='Tendencia de emisión de licencias y pagos', markers=True,
                      # hovertemplate='Fecha: {x}<br>Licencias: {y}'
                      )
    fig_mes.update_traces(hovertemplate='Fecha: %{x}<br>Licencias: %{y}')
    fig_mes.update_xaxes(tickangle=-90, ticks="outside",
                         nticks=48, showgrid=True, showline=True)
    fig_mes.update_yaxes(showgrid=True, showline=True)
    fig_mes.update_layout(yaxis_title='Monto de pagos',
                          xaxis_title='Fecha', title={'xanchor': 'center', 'x': 0.5})
    st.plotly_chart(fig_mes, use_container_width=True)
    # df_liquidacion = df.groupby(
    #     'YearMonth')[['LIQUIDO', 'SUSESO']].sum().reset_index(name='Cantidad')
    # df_liquidacion['YearMonth'] = df_liquidacion['YearMonth'].astype(str)
    # fig_line_emission = px.line(df_line_emission, x='YearMonth', y=[
    #                             'LIQUIDO', 'SUSESO'],
    #                             title='Tendencia de emisión de licencias y pagos')
    # fig_line_emission.update_layout(showlegend=True, xaxis_title=None, yaxis_title=None,
    #                                 title={'xanchor': 'center', 'x': 0.5},
    #                                 legend=dict(title=None,
    #                                             yanchor='top', xanchor='center', x=0.5))
    # fig_line_emission.update_xaxes(tickangle=-90, ticks="outside",
    #                                nticks=48, showgrid=True, showline=True)
    # fig_line_emission.update_yaxes(showgrid=True, showline=True)
    # st.plotly_chart(fig_line_emission, use_container_width=True)

    # ----------------------------------------------
    # Create a bar plot for 'LIQUIDO' and 'SUSESO' based on 'FECHA'

    df_bar = df.groupby('FECHA')[['LIQUIDO', 'SUSESO']].sum().reset_index()
    fig_bar = px.bar(df_bar, x='FECHA', y=[
                     'LIQUIDO', 'SUSESO'], title='Tendencias de pagos en Años')
    fig_bar.update_layout(yaxis_title=None, xaxis_title='FECHA',
                          title={'xanchor': 'center', 'x': 0.5},
                          legend=dict(title=None,
                                      yanchor='top', xanchor='center', x=0.5))
    st.plotly_chart(fig_bar, use_container_width=True)

    # ----------------------------------------------
    # Configuraciones de visualización
    st.write("Tendencias a lo largo del tiempo para la emisión de licencias médicas.")
    st.divider()
    sns.set(style="whitegrid")

    # 1. Tendencias a lo largo del tiempo para 'EMISION'
    df['Año'] = df['EMISION'].dt.year
    df['Mes'] = df['EMISION'].dt.month

    # Agrupar por año y mes para contar el número de licencias emitidas
    licencias_por_mes = df.groupby(
        ['Año', 'Mes']).size().reset_index(name='Cantidad')

    # Visualización
    plt.figure(figsize=(15, 6))
    sns.lineplot(data=licencias_por_mes, x='Año', y='Cantidad',
                 estimator='sum', ci=None, marker='o')
    plt.title('Tendencia de Licencias Médicas Emitidas por Año', fontsize=18)
    plt.xlabel('Año', fontsize=14)
    plt.ylabel('Cantidad de licencias emitidas', fontsize=14)
    plt.xticks(licencias_por_mes['Año'].unique())
    st.pyplot(plt)

    # ----------------------------------------------
    # 2. Distribución del estado de las licencias médicas ('ESTADO')
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, y='ESTADO',
                  order=df['ESTADO'].value_counts().index)
    plt.title('Distribución de Estados de Licencias Médicas')
    plt.xlabel('Cantidad')
    plt.ylabel('Estado')
    st.pyplot(plt)

    # ----------------------------------------------
    # 3. Análisis de la columna 'AUTORIZACION'
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, y='AUTORIZACION',
                  order=df['AUTORIZACION'].value_counts().index)
    plt.title('Distribución de Autorizaciones de Licencias Médicas')
    plt.xlabel('Cantidad')
    plt.ylabel('Autorización')
    st.pyplot(plt)

    st.divider()
    # ----------------------------------------------
    coll, colr = st.columns(2, gap="medium")
    with coll:
        st.write("La visualización corregida muestra la tendencia mensual de licencias médicas emitidas en el período. A través de esta gráfica, podemos observar cómo la cantidad de licencias varía mes a mes a lo largo del período de estudio.")
    with colr:
        st.write("Podría haber patrones estacionales evidentes, donde ciertos meses muestran variación en el número de licencias emitidas. Estos patrones podrían estar relacionados con factores estacionales como enfermedades comunes en ciertas épocas del año.")
    st.write("")

    # Corregir el formato de 'AñoMes' para visualización, convirtiéndolo a cadena
    if 'AñoMes' not in df.columns:
        df['AñoMes'] = df['Año'].astype(
            str) + '-' + df['Mes'].astype(str)
    # data['AñoMes'] = data['AñoMes'].astype(str)

    # Agrupar nuevamente por 'AñoMes' corregido para contar el número de licencias emitidas

    # ----------------------------------------------
    # idem plotly
    # 2024-03-31
    # ----------------------------------------------
    licencias_por_mes = df.groupby(
        'YearMonth').size().reset_index(name='Cantidad')
    # st.dataframe(licencias_por_mes)
    licencias_por_mes['YearMonth'] = licencias_por_mes['YearMonth'].astype(str)
    fig_mes = px.line(licencias_por_mes, x='YearMonth', y='Cantidad',
                      title='Tendencia Mensual de Licencias Médicas Emitidas', markers=True,
                      )
    fig_mes.update_traces(hovertemplate='Fecha: %{x}<br>Licencias: %{y}')
    fig_mes.update_xaxes(tickangle=-90, ticks="outside",
                         nticks=48, showgrid=True, showline=True)
    fig_mes.update_yaxes(showgrid=True, showline=True)
    fig_mes.update_layout(yaxis_title='Cantidad de licencias emitidas',
                          xaxis_title='Fecha', title={'xanchor': 'center', 'x': 0.5})
    st.plotly_chart(fig_mes, use_container_width=True)

    st.divider()
    # ----------------------------------------------
    # variables estacionales
    licencias_por_mes_promedio = df.groupby(
        'Mes').size().reset_index(name='Cantidad')
    licencias_por_mes_promedio['CantidadPromedio'] = licencias_por_mes_promedio['Cantidad'] / len(
        df['Año'].unique())

    # Visualización

    plt.figure(figsize=(12, 6))
    sns.barplot(data=licencias_por_mes_promedio, x='Mes',
                y='CantidadPromedio', palette='coolwarm')
    plt.title('Promedio de Licencias Médicas Emitidas por Mes', fontsize=16)
    plt.xlabel('Mes', fontsize=14)
    plt.ylabel('Promedio de Licencias Médicas Emitidas', fontsize=14)
    plt.xticks(range(0, 12), ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
               'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'])
    plt.tight_layout()
    st.pyplot(plt)

    # ----------------------------------------------
    # codigos CIE10
    # Identificar los 10 códigos de diagnóstico (CIE10) más comunes
    st.subheader("CIE10")
    st.write("Patrones específicos por condición de salud: Ciertos códigos de diagnóstico muestran picos claros en meses específicos, lo que puede indicar la estacionalidad de estas condiciones. Por ejemplo, si los códigos relacionados con enfermedades respiratorias aumentan en los meses de invierno, esto sugeriría una influencia estacional.")
    st.write("")
    st.write("La categoría F de la CIE-10 incluye trastornos mentales y del comportamiento. A continuación, se muestra la tendencia mensual de los 10 códigos de diagnóstico más comunes en esta categoría.")
    st.write("")
    st.write("F00: Trastornos mentales y del comportamiento debidos al uso de alcohol")
    st.write("F01: Demencia en la enfermedad de Alzheimer, tipo Alzheimer")
    st.write("F02: Demencia en otras enfermedades clasificadas en otra parte")
    st.write("F03: Demencia, no especificada")
    # st.write("F04: Síndrome amnésico orgánico no inducido por alcohol")
    # st.write("F05: Delirio no inducido por alcohol")
    st.write("F06: Otros trastornos mentales debidos a lesión y disfunción cerebral y a enfermedad somática")
    st.write("F07: Trastornos de la personalidad y del comportamiento en adultos")
    st.write("F10: Trastornos mentales y del comportamiento debidos al uso de alcohol")
    st.write("F14: Trastornos mentales y del comportamiento debidos al uso de cocaína")
    st.write("F19: Trastornos mentales y del comportamiento debidos al uso de múltiples drogas y al uso de otras sustancias psicoactivas")
    st.write("F20: Esquizofrenia")
    st.write("F22: Trastorno delirante persistente")
    st.write("F25: Trastornos esquizoafectivos")
    st.write("F064: Trastorno de ansiedad, orgánico")
    st.write("F065: Trastorno disociativo, orgánico")
    st.write("F070: Trastorno de personalidad, orgánico")
    st.write(
        "F102: Trastornos mentales y del comportamiento debidos al uso de alcohol síndrome de dependencia")
    st.write(
        "F141: Trastornos mentales y del comportamiento debidos al uso de cocaína, uso nocivo")

    top_cie10 = df['CIE10'].value_counts().nlargest(10).index.tolist()

    # Filtrar los datos para incluir solo los registros con los códigos de diagnóstico más comunes
    data_top_cie10 = df[df['CIE10'].isin(top_cie10)]

    # ----------------------------------------------
    # idem plotly CIE10
    # 2024-03-31
    # ----------------------------------------------

    licencias_por_cie = df.groupby(
        ['YearMonth', 'CIE10']).size().reset_index(name='Cantidad')
    licencias_por_cie['YearMonth'] = licencias_por_cie['YearMonth'].astype(str)
    fig_cie = px.line(licencias_por_cie, x='YearMonth', y='Cantidad', color='CIE10',
                      title='Tendencia Mensual de Licencias por Tipo CIE10', markers=True,
                      # hovertemplate='Fecha: {x}<br>Licencias: {y}'
                      )
    fig_cie.update_traces(hovertemplate='Fecha: %{x}<br>Licencias: %{y}')
    fig_cie.update_xaxes(tickangle=-90, ticks="outside",
                         nticks=48, showgrid=True, showline=True)
    fig_cie.update_yaxes(showgrid=True, showline=True)
    fig_cie.update_layout(yaxis_title='Cantidad de licencias emitidas',
                          xaxis_title='Fecha', title={'xanchor': 'center', 'x': 0.5})
    st.plotly_chart(fig_cie, use_container_width=True)


# ----------------------------------------------
    # idem plotly SUBCIE10
    # 2024-03-31
    # ----------------------------------------------
    licencias_por_cie = df.groupby(
        ['YearMonth', 'SUBCIE10']).size().reset_index(name='Cantidad')
    licencias_por_cie['YearMonth'] = licencias_por_cie['YearMonth'].astype(str)
    fig_cie = px.line(licencias_por_cie, x='YearMonth', y='Cantidad', color='SUBCIE10',
                      title='Tendencia Mensual de Licencias por SUBCIE10', markers=True,
                      # hovertemplate='Fecha: {x}<br>Licencias: {y}'
                      hover_name='SUBCIE10',
                      )
    fig_cie.update_traces(
        hovertemplate='Fecha: %{x}<br>Licencias: %{y}')
    fig_cie.update_xaxes(tickangle=-90, ticks="outside",
                         nticks=48, showgrid=True, showline=True)
    fig_cie.update_yaxes(showgrid=True, showline=True)
    fig_cie.update_layout(yaxis_title='Cantidad de licencias emitidas',
                          xaxis_title='Fecha', title={'xanchor': 'center', 'x': 0.5})
    st.plotly_chart(fig_cie, use_container_width=True)

    coll, colr = st.columns(2, gap="medium")
    coll.write("Diferencias en los patrones estacionales: No todas las condiciones de salud siguen el mismo patrón estacional, lo cual es esperado. Algunas condiciones pueden ser consistentemente altas a lo largo del año, mientras que otras muestran variabilidad mensual significativa.")
    colr.write("Importancia del contexto clínico y social: Para interpretar estos patrones correctamente, es crucial considerar el contexto clínico de cada código de diagnóstico (CIE10) y posibles factores sociales o ambientales que puedan influir en estas tendencias.")


# -------------------------------------------
with tabTable:
    st.dataframe(df, height=500)

# -------------------------------------------
with tabIA:
    st.subheader("Análisis exploratorio con Inteligencia Artificial")
    with st.expander("Información importante"):
        st.write("Las respuestas son generadas por un modelo de lenguaje de OpenAI, el cual permite realizar consultas sobre el dataset de MACEDA. Ingrese su consulta la que pudiera ser respondida por el modelo en forma de texto o una imagen gráfica.")
        st.write(
            "Por ejemplo, puede preguntar: ¿Cuántos eventos de tipo 'X' ocurrieron en la región 'Y' en el año '2018'?")
        st.info(
            "*Nota*: Esta es una tecnología en experimentación por lo que las respuestas pueden no ser del todo exactas.")
    st.write("")
    user_path = os.getcwd()
    # llm = OpenAI(api_token=API_KEY)
    llm = OpenAI(client=OpenAI, streaming=True,
                 api_token=API_KEY, temperature=0.5)

    prompt = st.text_area("Ingrese su consulta:")

    if st.button("Generar respuesta"):
        if prompt:
            with st.spinner("Generando respuesta... por favor espere."):
                llm = OpenAI(api_token=os.environ["OPENAI_API_KEY"])
                # query = SmartDataframe(df, config={"llm": llm})
                query = Agent(df, config={"llm": llm,
                                          "save_charts": False,
                                          # "save_charts_path": user_path,
                                          "open-charts": True,
                                          "verbose": True,
                                          "response_parser": StreamlitResponse
                                          })

                response = query.chat(prompt)

                if isinstance(response, str) and response.endswith("png"):
                    st.image(response)
                else:
                    st.write(response)
        else:
            st.write("Por favor ingrese una consulta.")
pro_bar.empty()
# -------------------------------------------
# with tabBleau:
#     st.write("Análisis con Pywalker")
# report = pgw.walk(df, return_html=True)
# components.html(report, height=1000, scrolling=True)

# -------------------------------------------
with tabInfo:
    st.write("Información")
    st.write(
        "Analisis de  salud mental  basado en licencias médicas otorgadas por la [Superintendencia de Seguridad Social de Chile](https://www.suseso.cl/).")
    st.markdown('''El conjunto de datos contiene una variedad de columnas que ofrecen información detallada sobre las licencias médicas otorgadas por diagnóstico CIE-10 de salud mental. A continuación, se detalla una descripción inicial de las columnas relevantes para el análisis exploratorio:

- FECHA: Año de la emisión de la licencia.
- LICENCIA: Número de licencia médica.
- FORMULARIO: Tipo de formulario de licencia (electrónico, papel, etc.).
- TRABAJADOR: Identificación del trabajador.
- EMISION: Fecha de emisión de la licencia.
- INICIO: Fecha de inicio de la licencia.
- DIAS: Duración en días de la licencia.
- TIPO: Tipo de licencia (por enfermedad, accidente no laboral, etc.).
- CIE10: Código CIE-10 del diagnóstico.
- GRUPOCIE10: Grupo del diagnóstico CIE-10.
- SUBCIE10: Subcategoría del diagnóstico CIE-10.

''')
