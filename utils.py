
# Este archivo contiene funciones utilitarias generales para la app Streamlit.
# Su objetivo es centralizar lógica común para el análisis y visualización de datos.

# Función: df_completitud
# - Calcula el porcentaje de órdenes que tienen costos de combustible, peajes y mantenimiento por periodo.
# - Devuelve un DataFrame agrupado por periodo con estos indicadores.
# - Útil para evaluar la calidad y completitud de los datos.

# Función: plot_completitud_y_mediana
# - Genera un gráfico de líneas con Plotly mostrando la completitud de los datos por componente y periodo.
# - Permite añadir líneas de promedio para comparar visualmente la completitud a lo largo del tiempo.
# - Facilita la identificación de periodos con baja calidad de datos.

# Función: show_info_columns
# - Calcula y muestra indicadores generales y estadísticos de las órdenes seleccionadas.
# - Incluye totales, promedios, medianas, cuartiles y máximos/mínimos de costos y kilómetros.
# - Presenta la información en un formato visual atractivo usando HTML y CSS embebido en Streamlit.
# - Ayuda a obtener una visión rápida y clara del estado de los datos filtrados.

import streamlit as st
import pandas as pd
import numpy as np

def df_completitud(df):
    df['Orden con Costo de Combustible'] = df['Costo Combustible'] > 0
    df['Orden con Costo de Peajes'] = df['Costo Peajes'] > 0
    df['Orden con Costo de Mantenimiento'] = df['Costo Mantenimiento'] > 0

    completitud_groupby = df.groupby(['Periodo']).agg({
        'No. Viajes':'sum',
        'Orden con Costo de Combustible': 'sum',
        'Orden con Costo de Peajes': 'sum',
        'Orden con Costo de Mantenimiento': 'sum'})

    completitud_groupby['% Órdenes con Costo Combustible'] = (completitud_groupby['Orden con Costo de Combustible'] / completitud_groupby['No. Viajes']) * 100
    completitud_groupby['% Órdenes con Costo Peajes'] = (completitud_groupby['Orden con Costo de Peajes'] / completitud_groupby['No. Viajes']) * 100
    completitud_groupby['% Órdenes con Costo Mantenimiento'] = (completitud_groupby['Orden con Costo de Mantenimiento'] / completitud_groupby['No. Viajes']) * 100

    return completitud_groupby

def plot_completitud_y_mediana(
    completitud_groupby, 
    columnas_estadistica,  # Lista de columnas para líneas de mediana
    dash_estadistica='dot',
    width = 1000,
    height = 700
    ):

    import plotly.graph_objects as go
    import numpy as np

    periodos = completitud_groupby.index.astype(str)
    componentes = [
        ('% Órdenes con Costo Combustible', 'Orden con Costo de Combustible', '#233ED9'),   # Azul fuerte
        ('% Órdenes con Costo Peajes', 'Orden con Costo de Peajes', '#F2CD5E'),             # Amarillo
        ('% Órdenes con Costo Mantenimiento', 'Orden con Costo de Mantenimiento', '#5086F2') # Azul claro
    ]

    fig = go.Figure()

    for i, (porcentaje, conteo_col, color) in enumerate(componentes):
        y = completitud_groupby[porcentaje]
        n = completitud_groupby[conteo_col]
        total = completitud_groupby['No. Viajes']
        # Asigna manualmente la posición para cada componente
        if i == 0:
            text_positions = ["top center"] * len(y)
        elif i == 1:
            text_positions = ["top center"] * len(y)
        else:
            text_positions = ["bottom center"] * len(y)
        fig.add_trace(go.Scatter(
            x=periodos,
            y=y,
            mode='lines+markers+text',
            name=porcentaje,
            text=[f"{v:.2f}%" for v in y],
            textposition=text_positions,
            textfont=dict(size=13, color='black'),
            marker=dict(color=color),
            line=dict(color=color),
            customdata=np.stack([n, total, y], axis=-1),
            hovertemplate=(
                'Periodo: %{x}<br>' +
                porcentaje + ': %{y:.2f}%<br>' +
                'Órdenes con costo: %{customdata[0]}<br>' +
                'Órdenes totales: %{customdata[1]}'
            )
        ))

    # Promedio como línea con hover general (toda la línea muestra el mismo hover)
    for porcentaje, _, color in componentes:
        if porcentaje in columnas_estadistica and porcentaje in completitud_groupby.columns:
            valores = completitud_groupby[porcentaje]
            promedio = np.mean(valores)  # <-- Cambia mediana por promedio
            q1 = np.percentile(valores, 25)
            q3 = np.percentile(valores, 75)
            fig.add_trace(go.Scatter(
                x=periodos,
                y=[promedio]*len(periodos),
                mode='lines+text',
                name=f'Promedio ({porcentaje}) - {promedio:.2f}%',
                line=dict(color=color, dash=dash_estadistica, width=2),
                opacity=1,
                showlegend=True,
                hovertemplate=(
                    f"Promedio {porcentaje}: {promedio:.2f}%<br>"
                    f"IQR: [{q1:.2f}%, {q3:.2f}%]<br>"
                ),
            ))

    fig.update_layout(
        title='Porcentaje de Órdenes con Costo por Componente',
        xaxis_title='Periodo',
        yaxis_title='Porcentaje (%)',
        template='plotly_white',
        height=700,
        width=1000,
        margin=dict(l=20, r=20, t=100, b=20),
    )

    return fig

def show_info_columns(df):
    from graph_hist_utils import streamlit_viz_selector, get_viz_figure
    import numpy as np
    
    # --- Calcula los indicadores ---
    info_df = {}

    # Generales
    info_df['EC'] = len(df['EC'].unique())
    info_df['Proyectos'] = len(df['Proyecto'].unique())
    info_df['Clientes'] = len(df['Cliente'].unique())
    info_df['Unidades'] = len(df['Tracto'].unique())
    info_df['Conductores'] = len(df['Conductor'].unique())
    info_df['No. Rutas'] = len(df['Ruta Ciudades'].unique())
    info_df['No. de Órdenes'] = len(df)
    info_df['Periodo'] = len(df['Periodo'].unique())

    # Costos, CPK y Kms Recorridos
    info_df['Costo Combustible'] = df['Costo Combustible'].sum()
    info_df['Costo Peajes'] = df['Costo Peajes'].sum()
    info_df['Costo Mantenimiento'] = df['Costo Mantenimiento'].sum()
    info_df['Costo Total'] = info_df['Costo Combustible'] + info_df['Costo Peajes'] + info_df['Costo Mantenimiento']
    info_df['kms Totales Recorridos'] = df['kmstotales'].sum()
    info_df['Costo Por Km (CPK)'] = info_df['Costo Total'] / info_df['kms Totales Recorridos'] if info_df['kms Totales Recorridos'] > 0 else 0
    info_df['Costo por Litro'] = df['Costo por litro'].fillna(0).mean() if not df['Costo por litro'].empty else 0


    # Variaciones
    df_for_desc = df.copy()
    df_for_desc = df_for_desc.replace([np.inf, -np.inf], np.nan)

    def q1(series):
        return series.quantile(0.25)
    def q3(series):
        return series.quantile(0.75)

    # Para cada variable, calcula los stats
    def get_stats(col, money=False):
        if col in df_for_desc.columns:
            s = df_for_desc[col].dropna()
            return [
                ("Q1", f"<b>${s.quantile(0.25):,.2f}</b>" if money else f"<b>{s.quantile(0.25):,.2f}</b>"),
                ("Mediana", f"<b>${s.median():,.2f}</b>" if money else f"<b>{s.median():,.2f}</b>"),
                ("Q3", f"<b>${s.quantile(0.75):,.2f}</b>" if money else f"<b>{s.quantile(0.75):,.2f}</b>"),
                ("Mínimo", f"<b>${s.min():,.2f}</b>" if money else f"<b>{s.min():,.2f}</b>"),
                ("Máximo", f"<b>${s.max():,.2f}</b>" if money else f"<b>{s.max():,.2f}</b>"),
            ]
        else:
            return [
                ("Q1", "<b>No disponible</b>"),
                ("Mediana", "<b>No disponible</b>"),
                ("Q3", "<b>No disponible</b>"),
                ("Mínimo", "<b>No disponible</b>"),
                ("Máximo", "<b>No disponible</b>"),
            ]

    # Estructura agrupada en 4 columnas/secciones
    columns_structure = [
        {
            "title": "Generales",
            "content": [
                ("EC distintos", f"<b>{info_df['EC']}</b>"),
                ("Proyectos distintos", f"<b>{info_df['Proyectos']}</b>"),
                ("Clientes distintos", f"<b>{info_df['Clientes']}</b>"),
                ("Unidades distintas", f"<b>{info_df['Unidades']}</b>"),
                ("Conductores distintos", f"<b>{info_df['Conductores']}</b>"),
                ("Rutas distintas", f"<b>{info_df['No. Rutas']}</b>"),
                ("Órdenes totales", f"<b>{info_df['No. de Órdenes']}</b>"),
                ("Periodos distintos", f"<b>{info_df['Periodo']}</b>"),
            ],
        },
        {
            "title": "Costos Kms Totales",
            "content": [
                ("Costo Combustible", f"<b>${info_df['Costo Combustible']:,.2f}</b>"),
                ("Costo Peajes", f"<b>${info_df['Costo Peajes']:,.2f}</b>"),
                ("Costo Mantenimiento", f"<b>${info_df['Costo Mantenimiento']:,.2f}</b>"),
                ("Costo Total", f"<b>${info_df['Costo Total']:,.2f}</b>"),
                ("KMs Totales Recorridos", f"<b>{info_df['kms Totales Recorridos']:,.2f}</b>"),
                ("Media Costo por Litro Orden", f"<b>${info_df['Costo por Litro']:.2f}</b>"),
            ],
        },
        {
            "title": "Costo de Combustible p/ Orden",
            "content": [
                ("Promedio", f"<b>${df_for_desc['Costo Combustible'].mean():,.2f}</b>"),
                ("Desviación Estándar", f"<b>${df_for_desc['Costo Combustible'].std():,.2f}</b>"),
                ("Q1", f"<b>${df_for_desc['Costo Combustible'].quantile(0.25):,.2f}</b>"),
                ("Mediana", f"<b>${df_for_desc['Costo Combustible'].median():,.2f}</b>"),
                ("Q3", f"<b>${df_for_desc['Costo Combustible'].quantile(0.75):,.2f}</b>"),
                ("Mínimo", f"<b>${df_for_desc['Costo Combustible'].min():,.2f}</b>"),
                ("Máximo", f"<b>${df_for_desc['Costo Combustible'].max():,.2f}</b>"),
            ],
        },
        {
            "title": "Costo de Peajes p/ Orden",
            "content": [
                ("Promedio", f"<b>${df_for_desc['Costo Peajes'].mean():,.2f}</b>"),
                ("Desviación Estándar", f"<b>${df_for_desc['Costo Peajes'].std():,.2f}</b>"),
                ("Q1", f"<b>${df_for_desc['Costo Peajes'].quantile(0.25):,.2f}</b>"),
                ("Mediana", f"<b>${df_for_desc['Costo Peajes'].median():,.2f}</b>"),
                ("Q3", f"<b>${df_for_desc['Costo Peajes'].quantile(0.75):,.2f}</b>"),
                ("Mínimo", f"<b>${df_for_desc['Costo Peajes'].min():,.2f}</b>"),
                ("Máximo", f"<b>${df_for_desc['Costo Peajes'].max():,.2f}</b>"),
            ],
        },
        {
            "title": "Costo de Mantenimiento p/ Orden",
            "content": [
                ("Promedio", f"<b>${df_for_desc['Costo Mantenimiento'].mean():,.2f}</b>"),
                ("Desviación Estándar", f"<b>${df_for_desc['Costo Mantenimiento'].std():,.2f}</b>"),
                ("Q1", f"<b>${df_for_desc['Costo Mantenimiento'].quantile(0.25):,.2f}</b>"),
                ("Mediana", f"<b>${df_for_desc['Costo Mantenimiento'].median():,.2f}</b>"),
                ("Q3", f"<b>${df_for_desc['Costo Mantenimiento'].quantile(0.75):,.2f}</b>"),
                ("Mínimo", f"<b>${df_for_desc['Costo Mantenimiento'].min():,.2f}</b>"),
                ("Máximo", f"<b>${df_for_desc['Costo Mantenimiento'].max():,.2f}</b>"),
            ],
        },
        {
            "title": "Kms Recorridos p/ Orden", 
            "content": [
                ("Promedio", f"<b>{df_for_desc['kmstotales'].mean():,.2f}</b> km"),
                ("Desviación Estándar", f"<b>{df_for_desc['kmstotales'].std():,.2f}</b> km"),
                ("Q1", f"<b>{df_for_desc['kmstotales'].quantile(0.25):,.2f}</b> km"),
                ("Mediana", f"<b>{df_for_desc['kmstotales'].median():,.2f}</b> km"),
                ("Q3", f"<b>{df_for_desc['kmstotales'].quantile(0.75):,.2f}</b> km"),
                ("Mínimo", f"<b>{df_for_desc['kmstotales'].min():,.2f}</b> km"),
                ("Máximo", f"<b>{df_for_desc['kmstotales'].max():,.2f}</b> km"),
            ],
        }
        ]

    # Calcula el máximo de filas para dar el mismo min-height
    max_items = max(len(col["content"]) for col in columns_structure)
    row_height = 28  # px, ajusta si quieres más separacion vertical
    min_height = row_height * (max_items + 2) + 40  # +2 por título y buffer

    st.markdown(f"""
    <style>
    .mega-flex {{
        display: flex;
        flex-direction: row;
        gap: 0px;
        margin-bottom: 50px;
        margin-top: 10px;
        min-height: {min_height}px;
    }}
    .mega-flex-col {{
        flex: 1 1 0%;
        padding: 10px 18px 30px 18px;
        box-sizing: border-box;
        min-height: {min_height}px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }}
    .mega-flex-col:not(:last-child) {{
        border-right: 2px solid #e3e3e3;
    }}
    .mega-title {{
        font-weight: bold;
        font-size: 15px;
        margin-bottom: 12px;
        margin-top: 2px;
    }}
    .mega-item {{
        margin-bottom: 6px;
        font-size: 15px;
        display: block;
    }}
    .mega-item-label {{
        font-weight: bold;
        margin-top: 12px;
        display: block;
    }}
    .mega-item-value {{
        font-weight: bold;
        margin-left: 8px;
        color: #173A5E;
    }}
    @media (max-width: 950px) {{
        .mega-flex {{ flex-direction: column; }}
        .mega-flex-col {{ border-right: none !important; border-bottom: 2px solid #e3e3e3; }}
        .mega-flex-col:last-child {{ border-bottom: none !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

    
    html = '<div class="mega-flex">'
    for col in columns_structure:
        html += '<div class="mega-flex-col">'
        html += f'<div class="mega-title">{col["title"]}</div>'
        last_label = None
        for k, v in col["content"]:
            if v == "":
                html += f'<span class="mega-item-label">{k}:</span>'
            else:
                html += f'<span class="mega-item">{k}: <span class="mega-item-value">{v}</span></span>'
        html += '</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
        
