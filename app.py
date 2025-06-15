
# Este archivo es el punto de entrada principal de la aplicación Streamlit.
# Orquesta la carga de datos, la configuración de la app y la integración de todas las funciones y módulos anteriores.

# - Configura el layout y el título de la app.
# - Carga los datos y los prepara para el análisis.
# - Permite buscar, filtrar y explorar los datos de manera interactiva.
# - Muestra indicadores generales, gráficos de CPK, completitud, histogramas y comparativos entre tractos.
# - Integra todas las funciones utilitarias y de visualización para ofrecer una experiencia de análisis completa y flexible.
# - Usar versión de Streamlit 1.37.1 IMPORTANTE PARA QUE FUNCIONE 
# - Instalar pip install streamlit-aggrid 
# - Iniciarlizar la app con el comando: streamlit run app.py

import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import math
from utils import show_info_columns, df_completitud, plot_completitud_y_mediana
from turtle import width
import plotly.graph_objects as go
import colorsys
from tracto_utils import seccion_graficos_tracto, plot_acumulado_vs_kms, plot_costos_vs_kms_bars, monocromatic_color
from historial_cargas import historial_entre_cargas
import numpy as np  
from calculos_cpk import agrupar_componentes_cpk, plot_cpk_barras_comparativo, cpk_desglosado
from df_filter_utils import search_and_filter_interface, groupby_interface
from graph_hist_utils import streamlit_viz_selector, get_viz_figure
from comparar_comp_utils import construir_df_cpk_periodo, comparar_componentes_cpk



def horas_a_dhm(horas):
    """Convierte horas (float) a una cadena con días, horas y minutos"""
    total_min = int(round(horas * 60))
    dias = total_min // (60 * 24)
    horas_rest = (total_min // 60) % 24
    minutos = total_min % 60
    partes = []
    if dias > 0:
        partes.append(f"{dias} día{'s' if dias != 1 else ''}")
    if horas_rest > 0 or dias > 0:
        partes.append(f"{horas_rest} h")
    return ", ".join(partes)


if __name__ == "__main__":

    st.set_page_config(page_title="Proyecto - PyTrack Analytics", layout="wide")

    if 'df' not in st.session_state:
        df = pd.read_excel('Base_viz.xlsx', index_col=0)

        df['Duración Viaje'] = df['Cierre de la Orden'] - df['Inicio de la Orden']

        if 'Duración Viaje (hrs)' not in df.columns and pd.api.types.is_timedelta64_dtype(df['Duración Viaje']):
            df['Duración Viaje (hrs)'] = (df['Duración Viaje'].dt.total_seconds() / 3600).round(2)

        df = df[['EC', 'Proyecto', 'Cliente', 'Tracto', 'Inicio de la Orden', 'Cierre de la Orden', 'Duración Viaje (hrs)', 'Edo. Origen', 'Edo. Destino', 'Cdad. Origen', 'Cdad. Destino', 'Ruta Estados', 'Ruta Ciudades',
                'Conductor', 'kmstotales', 'No. Remolques','Litros','Costo por litro', 'Costo Combustible', 'Costo Peajes', 'Costo Mantenimiento','Costo Total','CPK Orden', 'Periodo', 'Conteo',
                'lat_origen', 'lon_origen', 'lat_destino', 'lon_destino','Orden con Costo de Combustible','Orden con Costo de Peajes', 'Orden con Costo de Mantenimiento']].rename({'Conteo':'No. Viajes'}, axis = 1).copy()

        df.index.name = 'No. Orden'

        df.drop(['lat_origen', 'lon_origen', 'lat_destino', 'lon_destino'], axis=1, inplace=True, errors='ignore')

        df.reset_index(inplace=True)
        
        st.session_state.df = df.copy()

    if 'historial_cargas' and 'historial_cargas_grouped' not in st.session_state:
        historial_cargas, historial_cargas_grouped = historial_entre_cargas(st.session_state.df)
        st.session_state.historial_cargas = historial_cargas
        st.session_state.historial_cargas_grouped = historial_cargas_grouped


    # Ejemplo de columnas contables y forzadas
    columnas_contables = [
        "Costo Combustible", "Costo Peajes", "Costo Mantenimiento","Costo Total", "CPK Orden"
    ]
    columnas_forzar_fecha = ["Inicio de la Orden", "Cierre de la Orden"]
    columnas_forzar_str = ["Proyecto", "Cliente", "Tracto","No. Orden"]
    columnas_forzar_num = ["kmstotales", "No. Remolques", "Duración Viaje (hrs)"]

    # Título de la aplicación
    st.title("Bienvenido, TDR")
    st.markdown(""" """)

    st.markdown("""
    Esta aplicación te permite buscar y filtrar órdenes de transporte, visualizar datos y generar gráficos para análisis.
    Puedes buscar por columnas específicas, aplicar filtros y explorar los datos de manera interactiva.
    """)

    # Search bar y filtro
    st.subheader("Buscar y filtrar órdenes")

    with st.expander("Información de la sección", expanded=False):

        st.info(
            """
            **¿Cómo funciona la búsqueda y el filtrado?**

            - Selecciona una columna del listado para buscar información específica.
            - Dependiendo del tipo de columna, podrás:
            - Seleccionar un **rango de fechas** para filtrar por periodos.
            - Buscar uno o varios **valores de texto** (por ejemplo, tracto, cliente, proyecto).
            - Después de definir el filtro, haz clic en "Aplicar Filtro" para ver solo las órdenes que cumplen con los criterios seleccionados.
            - Puedes combinar varios filtros para afinar tu búsqueda y analizar subconjuntos de datos de interés.
            - Los resultados filtrados se mostrarán en la tabla inferior y se usarán en los indicadores y gráficos de la aplicación.

            Esta herramienta te permite explorar y analizar la información de manera flexible y personalizada.
            """
        )

    df_filtered = search_and_filter_interface(
        st.session_state.df,
        columnas_contables=columnas_contables,
        columnas_forzar_fecha=columnas_forzar_fecha,
        columnas_forzar_str=columnas_forzar_str,
        columnas_forzar_num=columnas_forzar_num,
        include_numeric=False
    )

    st.subheader("Resumen de las órdenes seleccionadas")

    st.info(
        "A continuación se muestran los indicadores generales y gráficos basados en los datos filtrados. "
        "Puedes explorar los datos de manera interactiva y obtener información valiosa sobre las órdenes de transporte.")

    # Mostrar indicadores generales
    show_info_columns(df_filtered)

    st.subheader("Análisis Desglosado de CPK por Componente")
    with st.expander("Información de la sección", expanded=False):
        st.info("""
            En la siguiente sección se muestra el **Costo por Kilómetro (CPK)** desglosado en dos componentes de costo operacional: **Peajes** y **Combustible**.  
            Realizamos estos cálculos de tres diferentes maneras para observar cómo el método de cálculo afecta el valor del CPK:

            1. **Considerando todas las órdenes:** Se incluyen todas las órdenes, tengan o no costos en cada componente.
            2. **Solo órdenes con algún costo:** Se consideran únicamente las órdenes que presentan algún costo total.
            3. **Solo órdenes con el componente:** Para cada componente, solo se consideran las órdenes que presentan ese componente (por ejemplo, solo las órdenes con costo de peajes para el CPK de peajes).
            4. **Entre Cargas:** Se calcula el CPK considerando los costos y kms recorridos entre carga y carga.

            **Nota:** Los cálculos de CPK "entre carga y carga" **no aplican los filtros seleccionados**, ya que estos podrían excluir órdenes necesarias para este tipo de análisis. Por ello, **siempre se consideran todas las órdenes disponibles** para calcular los indicadores entre cargas, asegurando así la consistencia y precisión de los resultados.

            Esto permite comparar cómo varía el CPK según el criterio de inclusión de órdenes y analizar la importancia de cada componente en el costo total.

            A continuación puedes ver la gráfica comparativa de CPK por periodo y por cada criterio.
            """)

    cpk_desglosado(df_filtered, historial_cargas=st.session_state.historial_cargas)

    with st.expander("Completitud de las órdenes seleccionadas", expanded=False):

        st.subheader("Completitud de las órdenes seleccionadas")

        st.info(
            "A continuación se muestra el porcentaje de órdenes que tienen costos de combustible, peajes y mantenimiento a lo largo del tiempo. "
            "Esto te ayudará a identificar la completitud de los datos y detectar posibles áreas de mejora en la recolección de información.")

        completitud_groupby = df_completitud(df_filtered)
        
        fig_completitud = plot_completitud_y_mediana(
                completitud_groupby,
                columnas_estadistica=[]
            )

        st.plotly_chart(fig_completitud, use_container_width=True)

    with st.expander("Exploración visual de las órdenes seleccionadas", expanded=False):

        st.subheader("Exploración visual de las órdenes seleccionadas")
        st.info(
            "Selecciona una columna numérica y el tipo de gráfico para visualizar la distribución de los datos filtrados. "
            "Puedes elegir entre barras (mediana, mínimo y máximo), boxplot o pastel por rangos. "
            "Esto te ayudará a analizar rápidamente la variabilidad y los valores típicos de la columna seleccionada."
        )

        col1, col2, col3 = st.columns([1,1,1])

        with col1:
            seleccionada1, tipo_grafico1 = streamlit_viz_selector(df_filtered, idx = 5, key = '1g')
            st.markdown(f"#### Gráfico de {tipo_grafico1} para **{seleccionada1}**")
            fig1 = get_viz_figure(df_filtered, seleccionada1, tipo_grafico1, width=700, height=700)

            if fig1 is not None:
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            seleccionada2, tipo_grafico2 = streamlit_viz_selector(df_filtered, idx = 6, key = '2g')
            st.markdown(f"#### Gráfico de {tipo_grafico2} para **{seleccionada2}**")
            fig2 = get_viz_figure(df_filtered, seleccionada2, tipo_grafico2, width=700, height=700)

            if fig2 is not None:
                st.plotly_chart(fig2, use_container_width=True)

        with col3:
            seleccionada3, tipo_grafico3 = streamlit_viz_selector(df_filtered, idx = 7, key = '3g')
            st.markdown(f"#### Gráfico de {tipo_grafico3} para **{seleccionada3}**")
            fig3 = get_viz_figure(df_filtered, seleccionada3, tipo_grafico3, width=700, height=700)

            if fig3 is not None:
                st.plotly_chart(fig3, use_container_width=True)

    with st.expander("Comparativo entre Tractos", expanded=False):

        st.subheader("Comparativo entre Tractos")
        st.info(
            "En esta sección se comparan los tractos que están presentes en los datos filtrados. "
            "Puedes seleccionar los tractos que deseas comparar y ver cómo se desempeñan en términos de costos y rendimiento. "
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            seccion_graficos_tracto(st.session_state.df, historial_cargas=st.session_state.historial_cargas,key="1tracto")
        with col2:
            seccion_graficos_tracto(st.session_state.df, historial_cargas=st.session_state.historial_cargas,key="2tracto")
