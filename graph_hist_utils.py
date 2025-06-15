
# Este archivo contiene utilidades para seleccionar y graficar columnas numéricas en Streamlit.

# Función: streamlit_viz_selector
# - Permite al usuario seleccionar una columna numérica y el tipo de gráfico (barras, boxplot, pastel) desde la interfaz Streamlit.
# - Devuelve la columna y el tipo de gráfico seleccionados.

# Función: get_viz_figure
# - Genera el gráfico correspondiente (barras, boxplot o pastel) para la columna seleccionada.
# - Calcula y muestra estadísticas descriptivas (media, mediana, cuartiles, etc.) en el gráfico.
# - Facilita la exploración visual de la distribución de los datos.

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

def streamlit_viz_selector(df,idx = 0, key=""):
    # Detecta columnas numéricas completas (sin strings ni NaN), omite 'Tracto'
    num_cols = [
        col for col in df.columns
        if pd.api.types.is_numeric_dtype(df[col]) and df[col].notna().all() and col not in ["Tracto", "No. Orden", "No. Viajes","Orden con Costo de Combustible"
                                                                                            , "Orden con Costo de Peajes", "Orden con Costo de Mantenimiento"]
    ]

    if not num_cols:
        st.warning("No hay columnas numéricas completas en el DataFrame.")
        return None, None, None

    # Dropdown para elegir UNA columna numérica
    seleccionada = st.selectbox(
        "Selecciona una columna numérica para analizar:",
        options=num_cols,
        index=idx if num_cols else None
        , key=f"col_select_{key}"
    )

    if not seleccionada:
        st.info("Selecciona una columna para continuar.")
        return None, None, None

    # Dropdown para tipo de gráfico
    tipo_grafico = st.selectbox(
        "Selecciona el tipo de gráfico:",
        options=["Barras", "Boxplot", "Pastel"]
        , key=f"tipo_grafico_{key}"
    )

    return seleccionada,tipo_grafico

def get_viz_figure(df, seleccionada, tipo_grafico, width=600, height=500, bar_width=0.25):
    import numpy as np
    import plotly.graph_objects as go
    import pandas as pd
    from plotly.subplots import make_subplots
    import streamlit as st

    col = seleccionada
    data = df[col].dropna()
    if data.empty:
        return None

    def fmt_num(n):
        return f"{n:,.2f}"

    mediana = np.median(data)
    minimo = np.min(data)
    maximo = np.max(data)
    promedio = np.mean(data)
    std = np.std(data)
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)

    stats_text = (
        f"<span style='font-size:22px;'><b>{col}</b></span><br><br>"
        f"<span style='font-size:17px;'>"
        f"<b>Promedio:</b> {fmt_num(promedio)}<br>"
        f"<b>Desv. estándar:</b> {fmt_num(std)}<br>"
        f"<b>Q1:</b> {fmt_num(q1)}<br>"
        f"<b>Mediana:</b> {fmt_num(mediana)}<br>"
        f"<b>Q3:</b> {fmt_num(q3)}<br>"
        f"<b>Mínimo:</b> {fmt_num(minimo)}<br>"
        f"<b>Máximo:</b> {fmt_num(maximo)}</span>"
    )

    if tipo_grafico == "Barras":
        fig = go.Figure()
        x_labels = ["", col, ""]
        y_vals = [None, mediana, None]
        bar_widths = [0, bar_width, 0]
        fig.add_trace(go.Bar(
            x=x_labels,
            y=y_vals,
            name="Mediana",
            marker_color="#4361EE",
            width=bar_widths,
            error_y=dict(
                type='data',
                symmetric=False,
                array=[0, maximo - mediana, 0],
                arrayminus=[0, mediana - minimo, 0],
                color="black",
                thickness=2.5,
                width=10
            ),
        ))
        fig.update_layout(
            yaxis_title=col,
            xaxis_title="",
            template="plotly_white",
            width=width,
            height=height,
            margin=dict(l=20, t=80, r=20, b=40),
            xaxis=dict(
                tickmode='array',
                tickvals=[0, 1, 2],
                ticktext=["", col, ""],
                showgrid=False,
                showticklabels=False
            ),
        )
        fig.add_annotation(
            text=stats_text,
            xref="paper", yref="paper",
            x=0.25, y=0.5,
            showarrow=False,
            align="center",
            bordercolor="#ccc",
            borderwidth=1,
            borderpad=16,
            bgcolor="rgba(255,255,255,0.97)",
            font=dict(size=20, color="#222"),
            xanchor="center", yanchor="middle"
        )
        return fig

    elif tipo_grafico == "Boxplot":
        # El boxplot debe estar en el centro del espacio 2 y 3 (x=1.5)
        fig = go.Figure()
        fig.add_trace(go.Box(
            x=[1.5] * len(data),  # posición central entre 1 y 2
            y=data,
            boxpoints="outliers",
            marker_color="#4361EE",
            width=bar_width,
            name=col,
            fillcolor="rgba(67,97,238,0.15)",
            line=dict(width=2, color="#4361EE"),
            showlegend=False
        ))
        fig.update_layout(
            margin=dict(l=20, t=80, r=20, b=40),
            width=width,
            height=height,
            xaxis=dict(
                range=[-0.2, 2.2],
                tickmode='array',
                tickvals=[0, 1, 1.5, 2],
                ticktext=["", "", col, ""],
                showgrid=False,
                showticklabels=True
            ),
            yaxis_title=col,
            template="plotly_white"
        )
        fig.add_annotation(
            text=stats_text,
            xref="paper", yref="paper",
            x=0.25, y=0.5,
            showarrow=False,
            align="center",
            bordercolor="#ccc",
            borderwidth=1,
            borderpad=16,
            bgcolor="rgba(255,255,255,0.97)",
            font=dict(size=20, color="#222"),
            xanchor="center", yanchor="middle"
        )
        return fig

    elif tipo_grafico == "Pastel":
        if minimo == maximo:
            # Todos los valores son iguales, no se puede hacer bins
            st.warning("No se puede graficar pastel: todos los valores son iguales.")
            return None
        bins = np.linspace(minimo, maximo, 11)
        labels = [f"{fmt_num(bins[i])} - {fmt_num(bins[i+1])}" for i in range(len(bins)-1)]
        categorias = pd.cut(data, bins=bins, labels=labels, include_lowest=True)
        conteo = categorias.value_counts().sort_index()
        legend_labels = [l for l, v in zip(labels, conteo.values) if v > 0]
        legend_vals = [v for v in conteo.values if v > 0]

        fig = make_subplots(
            rows=1, cols=2,
            column_widths=[0.75, 0.25],
            specs=[[{"type": "domain"}, {"type": "domain"}]]
        )
        fig.add_trace(
            go.Pie(
                labels=legend_labels,
                values=legend_vals,
                hole=0.2,
                textinfo='percent',
                showlegend=True,
                marker=dict(line=dict(color='#fff', width=1.5)),
            ),
            row=1, col=1
        )
        fig.update_layout(
            width=width,
            height=height,
            margin=dict(l=20, t=80, r=20, b=40),
            legend=dict(
                x=0.8,         # fuera del área de la gráfica
                y=0.8,            # arriba
                xanchor="left", # ancla a la izquierda de la caja de leyenda
                yanchor="top",  # ancla arriba
                font=dict(size=15),
                bgcolor="rgba(255,255,255,0.95)",
                bordercolor="#ccc",
                borderwidth=1
            )
        )
        return fig
    return None
