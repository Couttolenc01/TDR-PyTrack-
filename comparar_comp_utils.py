
# Este archivo contiene funciones para comparar los componentes de CPK entre diferentes periodos y criterios.

# Función: construir_df_cpk_periodo
# - Construye un DataFrame con los valores de CPK y otros indicadores por periodo y grupo de análisis.
# - Facilita la comparación entre diferentes métodos de cálculo.

# Función: construir_titulo
# - Genera un título legible para los gráficos de comparación, basado en la variable y los periodos seleccionados.

# Función: labels_arriba
# - Calcula la posición vertical para los labels de los gráficos, evitando que se sobrepongan.

# Función: comparar_componentes_cpk
# - Genera un gráfico de barras con error para comparar la media y desviación estándar de los componentes de CPK.
# - El formato de los labels respeta el parámetro es_dinero para mostrar o no el signo $.
# - Es clave para el análisis visual comparativo de los indicadores de rendimiento.

def construir_df_cpk_periodo(df_all, grupos=['todas', 'costo', 'componente', 'cargas']):
    
    """
    Construye un DataFrame de CPK por periodo según los grupos seleccionados.
    Args:
        df_all: DataFrame fuente con columnas de CPK por grupo.
        grupos: lista de grupos a incluir. Opciones:
            'todas'      -> Todas las Órdenes
            'costo'      -> Órdenes con costo
            'componente' -> Órdenes con el Componente
            'cargas'     -> Por Cargas
    Returns:
        df_cpk_periodo: DataFrame con los CPK seleccionados.
    """
    
    import pandas as pd

    columnas = {}
    if 'todas' in grupos:
        columnas.update({
            'CPK Combustible (Todas las Órdenes)': df_all['CPK Combustible (Todas las Órdenes)'],
            'CPK Peajes (Todas las Órdenes)': df_all['CPK Peajes (Todas las Órdenes)'],
            'Total CPK (Todas las Órdenes)': (
                df_all['CPK Combustible (Todas las Órdenes)'] +
                df_all['CPK Peajes (Todas las Órdenes)']
            ),
            'Rendimiento Kms/Litro (Todas las Órdenes)': df_all['Rendimiento Kms/Litro (Todas las Órdenes)'],
            'Costo por Litro (Todas las Órdenes)': df_all['Costo por Litro (Todas las Órdenes)'],
            'No. Órdenes Consideradas (Todas las Órdenes)': df_all['No. Órdenes Consideradas (Todas las Órdenes)'],
        })
    if 'costo' in grupos:
        columnas.update({
            'CPK Combustible (Órdenes con costo)': df_all['CPK Combustible (Órdenes con costo)'],
            'CPK Peajes (Órdenes con costo)': df_all['CPK Peajes (Órdenes con costo)'],
            'Total CPK (Órdenes con costo)': (
                df_all['CPK Combustible (Órdenes con costo)'] +
                df_all['CPK Peajes (Órdenes con costo)']
            ),
            'Rendimiento Kms/Litro (Órdenes con costo)': df_all['Rendimiento Kms/Litro (Órdenes con costo)'],
            'Costo por Litro (Órdenes con costo)': df_all['Costo por Litro (Órdenes con costo)'],
            'No. Órdenes Consideradas (Órdenes con costo)': df_all['No. Órdenes Consideradas (Órdenes con costo)'],
        })
    if 'componente' in grupos:
        columnas.update({
            'CPK Combustible (Órdenes con el Componente)': df_all['CPK Combustible (Órdenes con Componente)'],
            'CPK Peajes (Órdenes con el Componente)': df_all['CPK Peajes (Órdenes con Componente)'],
            'Total CPK (Órdenes con el Componente)': (
                df_all['CPK Combustible (Órdenes con Componente)'] +
                df_all['CPK Peajes (Órdenes con Componente)']
            ),
            'Rendimiento Kms/Litro (Órdenes con el Componente)': df_all['Rendimiento Kms/Litro (Órdenes con Componente)'],
            'Costo por Litro (Órdenes con el Componente)': df_all['Costo por Litro (Órdenes con Componente)'],
            'No. Órdenes Consideradas (Órdenes con Combustible)': df_all['No. Órdenes Consideradas (Órdenes con Combustible)'],
        })
    if 'cargas' in grupos:
        columnas.update({
            'CPK Combustible (Entre Cargas)': df_all['CPK Combustible (Entre Cargas)'],
            'CPK Peajes (Entre Cargas)': df_all['CPK Peajes (Entre Cargas)'],
            'Total CPK (Entre Cargas)': (
                df_all['CPK Combustible (Entre Cargas)'] +
                df_all['CPK Peajes (Entre Cargas)']
            ),
            'Rendimiento Kms/Litro (Entre Cargas)': df_all['Rendimiento Kms/Litro (Entre Cargas)'],
            'Costo por Litro (Entre Cargas)': df_all['Costo por Litro (Entre Cargas)'],
            'No. Cargas con Combustible': df_all['No. Cargas con Combustible'],
            'No. Cargas con Peajes': df_all['No. Cargas con Peajes'],
            'No. Cargas con Mantenimiento': df_all['No. Cargas con Mantenimiento'],
        })
    df_cpk_periodo = pd.DataFrame(columnas)
    df_cpk_periodo.index.name = 'Periodo'
    return df_cpk_periodo

# --- Construcción automática del título ---
def construir_titulo(variable, periodos):
    # Variable legible
    var_legible = variable.replace('CPK', 'CPK').replace('Total', 'Total').replace('(', '').replace(')', '')
    # Periodos legibles
    if len(periodos) == 1:
        periodo_str = f"{periodos[0]}"
    else:
        periodo_str = f"{periodos[0]} a {periodos[-1]}"
    return f"{var_legible}"

# --- Cálculo de posiciones para los labels (por encima del error) ---
def labels_arriba(media, std, decimales=3, sep=1):
    return [m + s + sep*max(media+std) for m, s in zip(media, std)]

def comparar_componentes_cpk(df_cpk_periodo, variable='CPK Combustible', periodos=None, width=800, height=900, es_dinero=False):
    import plotly.graph_objects as go
    import pandas as pd
    import numpy as np

    if periodos is None:
        periodos = df_cpk_periodo.index.tolist()


    cols = df_cpk_periodo.filter(like=variable).columns

    # Limpia NaN e inf antes de calcular media y std
    datos = df_cpk_periodo.loc[periodos, cols].replace([np.inf, -np.inf], np.nan).dropna()

    if datos.empty:
        import streamlit as st
        st.warning(f"No hay datos válidos para la variable '{variable}' en los periodos seleccionados.")
        return go.Figure()  # Devuelve una figura vacía para evitar el error

    media = datos.mean().round(2)
    std = datos.std().round(2).fillna(0)  # <-- Esto pone 0 donde std es NaN

    # Decide el formato del label según es_dinero
    if es_dinero:
        labels = [
            f"${m:.2f} ± ${s:.2f}" if not np.isnan(s) else f"${m:.2f} ± N/A"
            for m, s in zip(media.values, std.values)
        ]
    else:
        labels = [
            f"{m:.2f} ± {s:.2f}" if not np.isnan(s) else f"{m:.2f} ± N/A"
            for m, s in zip(media.values, std.values)
        ]

    PALETA = ['#4361EE', '#5086F2', '#F9C74F', '#222']

    # Mapeo de nombres de columna a nombres cortos de grupo
    grupo_map = {
        "Todas las Órdenes": "Todas las Órdenes",
        "Órdenes con costo": "Órdenes con costo",
        "Órdenes con el Componente": "Órdenes con el Componente",
        "Entre Cargas": "Entre Cargas"
    }
    # Busca el grupo en el nombre de la columna
    def extraer_grupo(col):
        for k in grupo_map:
            if k in col:
                return grupo_map[k]
        return col  # fallback

    labels_x = [extraer_grupo(col) for col in media.index]

    y_label_pos = labels_arriba(media.values, std.values, decimales=3, sep=0.08)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=labels_x,
        y=media.values,
        error_y=dict(
            type='data',
            array=std.values,
            color='black',
            thickness=2.5,
            width=10
        ),
        marker_color=PALETA[:len(media)],
        opacity=0.92,
        name='Media ± Desv. Estándar'
    ))

    # Calcula el rango de y para definir un umbral de separación mínima
    y_range = max(y_label_pos) - min(y_label_pos)
    min_sep = y_range * 0.07  # 7% del rango, ajusta según lo que veas visualmente

    # Guarda las posiciones ya usadas para comparar
    used_y = []

    for xi, yi, label in zip(labels_x, y_label_pos, labels):
        # Busca cuántos labels ya están cerca de este yi
        shift_count = 0
        for y_prev in used_y:
            if abs(yi - y_prev) < min_sep:
                shift_count += 1
        used_y.append(yi)
        fig.add_annotation(
            x=xi,
            y=yi + shift_count * min_sep,  # Sube el label si está muy cerca de otro
            text=label,
            showarrow=False,
            font=dict(size=13, color="#222", family="Arial"),
            yanchor="bottom"
        )

    fig.update_layout(
        title=construir_titulo(variable, periodos),
        xaxis_title='Grupo',
        yaxis_title='Valor',
        template='plotly_white',
        width=width,
        height=height,
        margin=dict(t=200, l=100, b=70, r=40),
        font=dict(size=16, family='Arial'),
        xaxis=dict(
        tickangle=-30)  
    )

    return fig
