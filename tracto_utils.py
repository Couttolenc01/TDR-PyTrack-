
# Este archivo contiene funciones para analizar y visualizar información específica de cada tracto.

# Función: monocromatic_color
# - Genera colores monocromáticos derivados de un color base para distinguir visualmente diferentes variables.

# Función: plot_acumulado_vs_kms
# - Grafica la evolución acumulada de costos y kilómetros para uno o varios tractos.
# - Permite comparar el desempeño de los tractos a lo largo del tiempo.

# Función: plot_costos_vs_kms_bars
# - Muestra barras comparativas de los costos y kilómetros totales para un tracto en un periodo dado.

# Función: seccion_graficos_tracto
# - Orquesta la visualización de los gráficos y tablas para un tracto seleccionado en la app Streamlit.
# - Incluye gráficos de acumulados, barras y el historial de cargas.
# - Facilita el análisis detallado y visual de cada tracto.

from turtle import width
import pandas as pd
import plotly.graph_objects as go
import colorsys

def monocromatic_color(base_hex, idx, total):
    base_rgb = tuple(int(base_hex.lstrip('#')[i:i+2], 16)/255. for i in (0, 2, 4))
    h, s, v = colorsys.rgb_to_hsv(*base_rgb)
    if total == 1:
        v2 = v
    else:
        v2 = 0.6 + (0.4 * idx / max(total-1, 1))
        v2 = max(0.2, min(v2, 1.0))
    rgb = colorsys.hsv_to_rgb(h, s, v2)
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

def plot_acumulado_vs_kms(df, tractos, title=None, width=800, height=600):

    TRACTO_BASE_COLORS = [
    "#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd"
    ]
    LINE_STYLES = {
        "kmstotales": "solid",
        "Costo Combustible": "dot",
        "Costo Peajes": "dot",
        "Costo Mantenimiento": "dot",
    }
    MARKERS = {
        "kmstotales": "circle",
        "Costo Combustible": "diamond",
        "Costo Peajes": "square",
        "Costo Mantenimiento": "triangle-up",
    }
    VARIABLES = [
        ("kmstotales", "acum_kms", "kmstotales"),
        ("Costo Combustible", "acum_combustible", "Costo Combustible"),
        ("Costo Peajes", "acum_peajes", "Costo Peajes"),
        ("Costo Mantenimiento", "acum_mantenimiento", "Costo Mantenimiento"),
    ]
    YAXIS_MAP = {
        "Costo Combustible": "y1",
        "Costo Peajes": "y1",
        "Costo Mantenimiento": "y1",
        "kmstotales": "y2"
    }
    MARKER_SIZE = 6

    COMPONENTE_COLORES = {
        "kmstotales": "#F2CD5E",           # Amarillo
        "Costo Combustible": "#233ED9",    # Azul fuerte
        "Costo Peajes": "#B3C8F2",         # Azul medio
        "Costo Mantenimiento": "#5086F2",  # Azul claro
    }

    df = df[df['Tracto'].isin(tractos)].copy()
    df['Inicio de la Orden'] = pd.to_datetime(df['Inicio de la Orden'])
    df = df.sort_values('Inicio de la Orden')

    fig = go.Figure()
    for tracto_idx, tracto in enumerate(tractos):
        base_color = TRACTO_BASE_COLORS[tracto_idx % len(TRACTO_BASE_COLORS)]
        dft = df[df['Tracto'] == tracto].sort_values('Inicio de la Orden').copy()
        dft['acum_combustible'] = dft['Costo Combustible'].cumsum()
        dft['acum_peajes'] = dft['Costo Peajes'].cumsum()
        dft['acum_mantenimiento'] = dft['Costo Mantenimiento'].cumsum()
        dft['acum_kms'] = dft["kmstotales"].cumsum()
        for var_idx, (variable, var_acum, var_single) in enumerate(VARIABLES):
            # Si solo hay un tracto, usa la paleta de componentes
            if len(tractos) == 1:
                color = COMPONENTE_COLORES[variable]
            else:
                color = monocromatic_color(base_color, var_idx, len(VARIABLES))
            vals_acum = dft[var_acum]
            vals_puntual = dft[var_single]
            ordenes = dft.index
            customdata = pd.concat(
                [
                    vals_puntual,
                    pd.Series(ordenes, index=vals_puntual.index, name="No. Orden")
                ],
                axis=1
            ).values
            fig.add_trace(go.Scatter(
                x=dft['Inicio de la Orden'],
                y=vals_acum,
                name=f"Acum. {variable} ({vals_acum.iloc[-1]:,.0f}) | {tracto}",
                mode='lines+markers',
                line=dict(
                    color=color,
                    width=2,
                    dash=LINE_STYLES[variable]
                ),
                marker=dict(
                    size=MARKER_SIZE,
                    color=color,
                    symbol=MARKERS[variable],
                    line=dict(color="black", width=0.6)
                ),
                yaxis=YAXIS_MAP[variable],
                showlegend=True,
                legendgroup=None,
                customdata=customdata,
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Fecha: %{x|%d-%b-%Y}<br>"
                    "Acumulado: <b>%{y:,}</b><br>"
                    "Valor puntual: %{customdata[0]:,.2f}<br>"
                    "No. Orden: %{customdata[1]}<extra></extra>"
                )
            ))

    fig.update_layout(
        title=title if title is not None else None,
        xaxis=dict(title='Fecha de Inicio de la Orden'),
        yaxis=dict(title='Acumulado de Costos ($)', rangemode='tozero'),
        yaxis2=dict(
            title='Acumulado KMs Totales',
            overlaying='y',
            side='right',
            rangemode='tozero',
            showgrid=False
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.6)",
            bordercolor="lightgray",
            borderwidth=1,
            font=dict(size=13),
        ),
        height=height,
        width=width,
        margin=dict(t=150, l=60, b=60, r=60),
        plot_bgcolor="white"
    )
    return fig

def plot_costos_vs_kms_bars(df, fecha_inicio, fecha_fin, tracto, width=800, height=600):
    # Filtrado y suma
    data = df[(df['Inicio de la Orden'] >= fecha_inicio) & (df['Cierre de la Orden'] < fecha_fin) & (df['Tracto'] == tracto)].copy()
    total = data[['Costo Combustible', 'Costo Peajes', 'Costo Mantenimiento', 'kmstotales']].sum()

    colores = {
        'Costo Combustible': "#233ED9",    # Azul fuerte
        'Costo Peajes': "#B3C8F2",         # Azul medio
        'Costo Mantenimiento': "#5086F2",  # Azul claro
        'kmstotales': "#F2CD5E",           # Amarillo
    }

    fig = go.Figure()
    # Barras de costos
    for var in ['Costo Combustible', 'Costo Peajes', 'Costo Mantenimiento']:
        fig.add_trace(go.Bar(
            x=[var],
            y=[total[var]],
            name=var,
            marker_color=colores[var],
            yaxis='y1',
            hovertemplate=f"Tipo: {var}<br>Monto: $%{{y:,.2f}}<extra></extra>",
            text=[f"${total[var]:,.0f}"],  # Texto arriba de la barra
            textposition='outside'
        ))
    # Barra de kms (eje derecho)
    fig.add_trace(go.Bar(
        x=['kmstotales'],
        y=[total['kmstotales']],
        name='Kms Totales',
        marker_color=colores['kmstotales'],
        yaxis='y2',
        hovertemplate="Tipo: kmstotales<br>Kms: %{y:,.0f}<extra></extra>",
        text=[f"{total['kmstotales']:,.0f}"],
        textposition='outside'
    ))



    fig.update_layout(
        barmode='group',
        title=f"Acumulados de Costos y Kms | Tracto {tracto} | {fecha_inicio.strftime('%d-%b-%Y')} al {fecha_fin.strftime('%d-%b-%Y')}",
        xaxis_title='Variable',
        yaxis=dict(
            title='Costo ($)',
            rangemode='tozero'
        ),
        yaxis2=dict(
            title='Kms Totales',
            overlaying='y',
            side='right',
            rangemode='tozero',
            showgrid=False
        ),
        bargap=0.3,
        legend=dict(
            orientation="h",
            y=1.13,
            x=0.01
        ),
        template='plotly_white',
        height=height,
        width=width,
        margin=dict(t=150, l=60, b=60, r=60),
    )
    return fig

def seccion_graficos_tracto(df, historial_cargas, key=""):
    import streamlit as st
    from tracto_utils import plot_acumulado_vs_kms, plot_costos_vs_kms_bars
    import numpy as np
    from graph_hist_utils import streamlit_viz_selector,get_viz_figure
    from st_aggrid import AgGrid, GridOptionsBuilder

    st.markdown("""
    **Indicadores gráficos por tracto**

    Selecciona un tracto para visualizar la evolución acumulada de costos y kilómetros, así como el resumen total de cada componente para el periodo disponible.
    """)

    tractos = df['Tracto'].unique()
    tracto_default = tractos[0] if len(tractos) > 0 else None
    tracto_sel = st.selectbox("Selecciona un tracto", options=tractos, index=0, key=f"tracto_selector_{key}")

    fecha_inicio = df[df['Tracto'] == tracto_sel]['Inicio de la Orden'].min()
    fecha_fin = df[df['Tracto'] == tracto_sel]['Cierre de la Orden'].max()

    hist_cargas = historial_cargas[(historial_cargas['Tracto'] == tracto_sel) & (historial_cargas['Fecha Orden de Carga'] >= fecha_inicio) & (historial_cargas['Fecha Orden de Carga'] <= fecha_fin)]

    
    title = f"Acumulados de Costos y Kms | Tracto {tracto_sel} | {fecha_inicio.strftime('%d-%b-%Y')} al {fecha_fin.strftime('%d-%b-%Y')}"
    fig1 = plot_acumulado_vs_kms(df[(df['Inicio de la Orden']>=fecha_inicio) & (df['Cierre de la Orden']<fecha_fin)], [tracto_sel], title=title, width=400, height=700)
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = plot_costos_vs_kms_bars(
        df,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        tracto=tracto_sel,
        width=400, 
        height=500
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Historial de Cargas")
    st.info(
        """
        **¿Qué muestra esta tabla?**

        Aquí puedes ver el historial de cargas del tracto seleccionado.  
        Cada fila representa el periodo entre una carga de combustible y la siguiente.  

        Esta información te permite analizar en detalle el desempeño operativo y los costos de cada tracto entre cada abastecimiento.
        """
    )

    st.dataframe(
                hist_cargas.sort_values('Fecha Orden de Carga', ascending=True).reset_index(drop=True),
                use_container_width=True,
                height=420  # Cambia el valor según lo que necesites
            )

    st.markdown("### Visualización de Datos")
    st.info(
        "Selecciona una columna numérica y el tipo de gráfico para visualizar la distribución de los datos del historial de cargas. "
        "Puedes elegir entre barras (mediana, mínimo y máximo), boxplot o pastel por rangos. "
        "Esto te ayudará a analizar rápidamente la variabilidad y los valores típicos de la columna seleccionada."
    )
    
    seleccionada1, tipo_grafico1 = streamlit_viz_selector(hist_cargas, key=f"viz_tracto1{key}")
    if seleccionada1 and tipo_grafico1:
        fig1 = get_viz_figure(hist_cargas, seleccionada1, tipo_grafico1, width=400, height=500)
        if fig1:
            st.markdown(
                f"""
                <h4 style='text-align: center;'>
                    Gráfico de {tipo_grafico1} y {seleccionada1}
                </h4>
                """,
                unsafe_allow_html=True
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("No se pudo generar el gráfico con los datos seleccionados.")
        
