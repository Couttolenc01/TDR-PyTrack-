
# Este archivo contiene funciones para calcular y visualizar el Costo Por Kilómetro (CPK) desglosado por componentes.

# Función: agrupar_componentes_cpk
# - Agrupa y calcula el CPK de combustible, peajes y mantenimiento bajo diferentes criterios (todas las órdenes, solo con costo, solo con componente, entre cargas).
# - Devuelve un DataFrame con todos los indicadores necesarios para el análisis comparativo.

# Función: plot_cpk_barras_comparativo
# - Genera un gráfico de barras apiladas con Plotly para comparar el CPK por periodo y por criterio de agrupación.
# - Usa colores y posiciones diferenciadas para cada grupo y componente.
# - Permite visualizar rápidamente cómo varía el CPK según el método de cálculo.

# Función: cpk_desglosado
# - Orquesta el cálculo y visualización del CPK desglosado.
# - Llama a las funciones anteriores y muestra los resultados en la app Streamlit.
# - Permite al usuario comparar visualmente los componentes de costo y su evolución.

def agrupar_componentes_cpk(df,historial_cargas):

    import pandas as pd

    df_agg_all = df.groupby('Periodo').agg({'Costo Combustible':'sum', 'Costo Peajes':'sum', 'Costo Mantenimiento':'sum', 'kmstotales':'sum','Litros':'sum'}).sort_values('Periodo', ascending=True)
    df_agg_all['CPK Combustible (Todas las Órdenes)'] = df_agg_all['Costo Combustible'] / df_agg_all['kmstotales']
    df_agg_all['CPK Peajes (Todas las Órdenes)'] = df_agg_all['Costo Peajes'] / df_agg_all['kmstotales']
    df_agg_all['CPK Mantenimiento (Todas las Órdenes)'] = df_agg_all['Costo Mantenimiento'] / df_agg_all['kmstotales']
    df_agg_all['Rendimiento Kms/Litro (Todas las Órdenes)'] = df_agg_all['kmstotales'] / df_agg_all['Litros']
    df_agg_all['No. Órdenes Consideradas (Todas las Órdenes)'] = df.groupby('Periodo').size()
    df_agg_all['Costo por Litro (Todas las Órdenes)'] = df_agg_all['Costo Combustible'] / df_agg_all['Litros']



    df_agg_all['Costo Combustible (Todas las Órdenes)'] = df_agg_all['Costo Combustible'].fillna(0)
    df_agg_all['Litros (Todas las Órdenes)'] = df_agg_all['Litros'].fillna(0)

    df_filtered = df[df['Costo Total'] > 0].copy()
    df_agg_filtered = df_filtered.groupby('Periodo').agg({'Costo Combustible':'sum', 'Costo Peajes':'sum', 'Costo Mantenimiento':'sum', 'kmstotales':'sum','Litros':'sum'}).sort_values('Periodo', ascending=True)
    df_agg_filtered['CPK Combustible (Órdenes con costo)'] = df_agg_filtered['Costo Combustible'] / df_agg_filtered['kmstotales']
    df_agg_filtered['CPK Peajes (Órdenes con costo)'] = df_agg_filtered['Costo Peajes'] / df_agg_filtered['kmstotales']
    df_agg_filtered['CPK Mantenimiento (Órdenes con costo)'] = df_agg_filtered['Costo Mantenimiento'] / df_agg_filtered['kmstotales']
    df_agg_filtered['Rendimiento Kms/Litro (Órdenes con costo)'] = df_agg_filtered['kmstotales'] / df_agg_filtered['Litros']
    df_agg_filtered['No. Órdenes Consideradas (Órdenes con costo)'] = df_filtered.groupby('Periodo').size()
    df_agg_filtered['Costo por Litro (Órdenes con costo)'] = df_agg_filtered['Costo Combustible'] / df_agg_filtered['Litros']

    df_componente_comb = df[df['Orden con Costo de Combustible'] == True].copy()
    df_componente_peajes = df[df['Orden con Costo de Peajes'] == True].copy()
    df_componente_mant = df[df['Orden con Costo de Mantenimiento'] == True].copy()

    df_agg_componente_comb = df_componente_comb.groupby('Periodo').agg({'Costo Combustible':'sum', 'kmstotales':'sum','Litros':'sum'}).sort_values('Periodo', ascending=True)
    df_agg_componente_comb['CPK Combustible (Órdenes con Componente)'] = df_agg_componente_comb['Costo Combustible'] / df_agg_componente_comb['kmstotales']
    df_agg_componente_comb['Rendimiento Kms/Litro (Órdenes con Componente)'] = df_agg_componente_comb['kmstotales'] / df_agg_componente_comb['Litros']
    df_agg_componente_comb['No. Órdenes Consideradas (Órdenes con Combustible)'] = df_componente_comb.groupby('Periodo').size()
    df_agg_componente_comb['Costo por Litro (Órdenes con Componente)'] = df_agg_componente_comb['Costo Combustible'] / df_agg_componente_comb['Litros']

    df_agg_componente_peajes = df_componente_peajes.groupby('Periodo')[['Costo Peajes', 'kmstotales']].sum().sort_values('Periodo', ascending=True)
    df_agg_componente_peajes['CPK Peajes (Órdenes con Componente)'] = df_agg_componente_peajes['Costo Peajes'] / df_agg_componente_peajes['kmstotales']
    df_agg_componente_peajes['No. Órdenes Consideradas (Órdenes con Peaje)'] = df_componente_peajes.groupby('Periodo').size()

    df_agg_componente_mant = df_componente_mant.groupby('Periodo')[['Costo Mantenimiento', 'kmstotales']].sum().sort_values('Periodo', ascending=True)
    df_agg_componente_mant['CPK Mantenimiento (Órdenes con Componente)'] = df_agg_componente_mant['Costo Mantenimiento'] / df_agg_componente_mant['kmstotales']
    df_agg_componente_mant['No. Órdenes Consideradas (Órdenes con Mantenimiento)'] = df_componente_mant.groupby('Periodo').size()

    hist_cargas = historial_cargas[historial_cargas['Periodo'].isin(df['Periodo'].unique())].copy()
    df_cargaxcarga = hist_cargas.groupby('Periodo').agg({'Costo de Combustible': 'sum','KMs Recorridos desde Última Carga': 'sum','Litros Combustible Cargados': 'sum'})
    df_cargaxcarga['CPK Combustible (Entre Cargas)'] = df_cargaxcarga['Costo de Combustible'] / df_cargaxcarga['KMs Recorridos desde Última Carga']
    df_cargaxcarga['Rendimiento Kms/Litro (Entre Cargas)'] = df_cargaxcarga['KMs Recorridos desde Última Carga'] / df_cargaxcarga['Litros Combustible Cargados']
    df_cargaxcarga['No. Cargas con Combustible'] = hist_cargas.groupby('Periodo').size()
    df_cargaxcarga['Costo por Litro (Entre Cargas)'] = df_cargaxcarga['Costo de Combustible'] / df_cargaxcarga['Litros Combustible Cargados']

    df_cargaxcarga['CPK Peajes (Entre Cargas)'] = hist_cargas.groupby('Periodo')['Costo de Peajes'].sum() / df_cargaxcarga['KMs Recorridos desde Última Carga']
    df_cargaxcarga['No. Cargas con Peajes'] = hist_cargas.groupby('Periodo')['Costo de Peajes'].apply(lambda x: (x > 0).sum())

    df_cargaxcarga['CPK Mantenimiento (Entre Cargas)'] = hist_cargas.groupby('Periodo')['Costo de Mantenimiento'].sum() / df_cargaxcarga['KMs Recorridos desde Última Carga']    
    df_cargaxcarga['No. Cargas con Mantenimiento'] = hist_cargas.groupby('Periodo')['Costo de Mantenimiento'].apply(lambda x: (x > 0).sum())
   

    df_all = pd.concat([df_agg_all[['CPK Combustible (Todas las Órdenes)', 'CPK Peajes (Todas las Órdenes)', 'CPK Mantenimiento (Todas las Órdenes)',
                        'Rendimiento Kms/Litro (Todas las Órdenes)', 'No. Órdenes Consideradas (Todas las Órdenes)','Costo por Litro (Todas las Órdenes)']],
                        
                        df_agg_filtered[['CPK Combustible (Órdenes con costo)', 'CPK Peajes (Órdenes con costo)', 'CPK Mantenimiento (Órdenes con costo)',
                        'Rendimiento Kms/Litro (Órdenes con costo)', 'No. Órdenes Consideradas (Órdenes con costo)', 'Costo por Litro (Órdenes con costo)']],
                        
                        df_agg_componente_comb[['CPK Combustible (Órdenes con Componente)', 'Rendimiento Kms/Litro (Órdenes con Componente)',
                         'No. Órdenes Consideradas (Órdenes con Combustible)', 'Costo por Litro (Órdenes con Componente)']],

                        df_agg_componente_peajes[['CPK Peajes (Órdenes con Componente)', 'No. Órdenes Consideradas (Órdenes con Peaje)']],
                        df_agg_componente_mant[['CPK Mantenimiento (Órdenes con Componente)', 'No. Órdenes Consideradas (Órdenes con Mantenimiento)']], 
                        
                        df_cargaxcarga[['CPK Combustible (Entre Cargas)', 'Rendimiento Kms/Litro (Entre Cargas)', 'No. Cargas con Combustible','Costo por Litro (Entre Cargas)',
                        'CPK Peajes (Entre Cargas)', 'No. Cargas con Peajes', 'CPK Mantenimiento (Entre Cargas)', 'No. Cargas con Mantenimiento']]
                        ], axis=1)

    df_all.fillna(0, inplace=True)

    return df_all

def plot_cpk_barras_comparativo(
    df_all, 
    componentes=['Combustible', 'Peajes', 'Mantenimiento'], 
    grupos=['Todas las Órdenes', 'Órdenes con costo', 'Órdenes con Componente', 'Entre Cargas'],
    width=1200, 
    height=600
):
    import plotly.graph_objects as go
    import numpy as np

    # Colores sólidos únicos para cada grupo+componente
    COLOR_MAP = {
        ('Todas las Órdenes', 'Combustible'): "#A3BFFA",   # Azul pastel (más claro)
        ('Órdenes con costo', 'Combustible'): "#5086F2",   # Azul claro
        ('Órdenes con Componente', 'Combustible'): "#4361EE", # Azul medio
        ('Entre Cargas', 'Combustible'): "#233ED9",        # Azul fuerte (más oscuro)
        ('Todas las Órdenes', 'Peajes'): "#FFF9DB",        # Amarillo pastel (más claro)
        ('Órdenes con costo', 'Peajes'): "#FFF3BF",        # Amarillo claro
        ('Órdenes con Componente', 'Peajes'): "#F9E79F",   # Amarillo medio
        ('Entre Cargas', 'Peajes'): "#F2CD5E",             # Amarillo fuerte (más oscuro)
        ('Todas las Órdenes', 'Mantenimiento'): "#C9ADA7", # Gris pastel (más claro)
        ('Órdenes con costo', 'Mantenimiento'): "#9A8C98", # Gris claro
        ('Órdenes con Componente', 'Mantenimiento'): "#4A4E69", # Gris medio
        ('Entre Cargas', 'Mantenimiento'): "#22223B",      # Gris oscuro (más oscuro)
    }

    col_map = {
        'Todas las Órdenes': lambda comp: f'CPK {comp} (Todas las Órdenes)',
        'Órdenes con costo': lambda comp: f'CPK {comp} (Órdenes con costo)',
        'Órdenes con Componente': lambda comp: f'CPK {comp} (Órdenes con Componente)',
        'Entre Cargas': lambda comp: f'CPK {comp} (Entre Cargas)',
    }
    pos_map = {
        'Todas las Órdenes': -0.3,
        'Órdenes con costo': -0.1,
        'Órdenes con Componente': 0.1,
        'Entre Cargas': 0.3,
    }

    periodos = df_all.index.astype(str)
    n = len(periodos)
    ind = np.arange(n)
    bar_width = 0.18

    fig = go.Figure()

    ordenes_col_map = {
        'Todas las Órdenes': 'No. Órdenes Consideradas (Todas las Órdenes)',
        'Órdenes con costo': 'No. Órdenes Consideradas (Órdenes con costo)',
        'Órdenes con Componente': {
            'Combustible': 'No. Órdenes Consideradas (Órdenes con Combustible)',
            'Peajes': 'No. Órdenes Consideradas (Órdenes con Peaje)',
            'Mantenimiento': 'No. Órdenes Consideradas (Órdenes con Mantenimiento)'
        },
        'Entre Cargas': {
            'Combustible': 'No. Cargas con Combustible',
            'Peajes': 'No. Cargas con Peajes',
            'Mantenimiento': 'No. Cargas con Mantenimiento'
        }
    }

    for grupo in grupos:
        comps_presentes = []
        custom_cols = []
        for comp in componentes:
            colname = col_map[grupo](comp)
            if colname in df_all.columns:
                comps_presentes.append(comp)
                custom_cols.append(df_all[colname])
        for comp in comps_presentes:
            col = col_map[grupo](comp)
            y_vals = df_all[col]
            base = 0
            if comp == 'Peajes' and f'CPK Combustible ({grupo})' in df_all.columns:
                base = df_all[col_map[grupo]('Combustible')]
            elif comp == 'Mantenimiento' and all(f'CPK {c} ({grupo})' in df_all.columns for c in ['Combustible', 'Peajes']):
                base = df_all[col_map[grupo]('Combustible')] + df_all[col_map[grupo]('Peajes')]

            suma_total = np.sum(custom_cols, axis=0) if custom_cols else np.zeros_like(y_vals)
            if isinstance(ordenes_col_map[grupo], dict):
                ordenes_col_name = ordenes_col_map[grupo].get(comp)
            else:
                ordenes_col_name = ordenes_col_map[grupo]
            n_ordenes_col = df_all[ordenes_col_name] if ordenes_col_name in df_all.columns else np.full_like(y_vals, np.nan)
            
            customdata = np.stack(
                [periodos] + [c.values for c in custom_cols] + [suma_total, n_ordenes_col.values],
                axis=-1
            )
            hover_lines = [f"<b>{grupo}</b><br>", "Periodo: %{customdata[0]}<br>"]
            for idx, c_label in enumerate(comps_presentes):
                if c_label == comp:
                    hover_lines.append(f"<b>{c_label}: $%{{customdata[{idx+1}]:,.4f}}</b><br>")
                else:
                    hover_lines.append(f"{c_label}: $%{{customdata[{idx+1}]:,.4f}}<br>")
            hover_lines.append(f"Acumulado total: $%{{customdata[{len(comps_presentes)+1}]:,.4f}}<br>")
            hover_lines.append(f"Órdenes consideradas: %{{customdata[{len(comps_presentes)+2}]}}<br>")
            hover_lines.append("<extra></extra>")
            hovertemplate = ''.join(hover_lines)

            # Color sólido único para cada grupo+componente
            color = COLOR_MAP.get((grupo, comp), "#888888")

            fig.add_trace(go.Bar(
                x=ind + pos_map[grupo],
                y=y_vals,
                name=f'{comp} ({grupo})',
                marker_color=color,
                width=bar_width,
                offsetgroup=grupo,
                legendgroup=f"{grupo}-{comp}",
                showlegend=True,
                base=base if comp != 'Combustible' else None,
                opacity=1.0,  # Sin opacidad
                customdata=customdata,
                hovertemplate=hovertemplate
            ))

            for i, val in enumerate(suma_total):
                if comp == comps_presentes[-1]:
                    fig.add_annotation(
                        x=ind[i] + pos_map[grupo],
                        y=val,
                        text=f" ${val:.2f}",
                        showarrow=False,
                        yshift=12.5,
                        font=dict(size=13, color="#222"),
                        bgcolor="rgba(255,255,255,0.85)",
                        align="center"
                    )

    fig.update_layout(
        barmode='stack',
        title='CPK por Periodo y Componentes',
        xaxis=dict(
            title='Periodo',
            tickvals=ind,
            ticktext=periodos
        ),
        yaxis_title='CPK ($/km)',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.08,
            xanchor="center",
            x=0.5,
            font=dict(size=13)
        ),
        legend_itemclick=False,
        legend_itemdoubleclick=False,
        margin=dict(l=50, r=30, t=200, b=50),
        width=width,
        height=height
    )
    
    return fig

def cpk_desglosado(df,historial_cargas):

    from calculos_cpk import agrupar_componentes_cpk, plot_cpk_barras_comparativo
    from comparar_comp_utils import comparar_componentes_cpk, construir_df_cpk_periodo
    import streamlit as st
    import pandas as pd

    df_all = agrupar_componentes_cpk(df, historial_cargas)
    fig = plot_cpk_barras_comparativo(
        df_all,
        componentes=['Combustible', 'Peajes'],
        grupos=['Todas las Órdenes', 'Órdenes con costo', 'Órdenes con Componente', 'Entre Cargas'],
        width=1200,
        height=800
    )
    st.plotly_chart(fig, use_container_width=True)
    
    df_cpk_periodo = construir_df_cpk_periodo(df_all, grupos=['todas', 'costo', 'componente', 'cargas'])

    st.subheader("Comparación de Componentes e Indicadores de Rendimiento por Periodo")

    st.info(""" Selecciona un periodo para comparar los indicadores de rendimiento (CPK, Rendimiento Kms/Litro, Costo por Litro) entre los componentes (Combustible, Peajes).""")

    df['Periodo'] = pd.PeriodIndex(df['Periodo'], freq='M')

    # selecciona rango de periodos
    periodo_inicio = df['Periodo'].min()
    periodo_fin = df['Periodo'].max()

    periodos_opciones = sorted(df['Periodo'].unique())

    col1, col2 = st.columns([2, 3])

    with col1:
        periodo_seleccionado = st.select_slider(
            "Selecciona el periodo para comparar CPK",
            options=periodos_opciones,
            value=(periodos_opciones[0], periodos_opciones[-1]),
            format_func=lambda x: x.strftime('%b %Y')
        )

    periodo_strs = [str(p) for p in periodo_seleccionado]

    st.markdown(
        f"""
        <h4 style='text-align: center;'>
            Comparación de CPK por Componente entre Periodos e Indicadores de Rendimiento: {periodo_strs[0]} y {periodo_strs[1]}
        </h4>
        """,
        unsafe_allow_html=True
    )

    # Lista de variables disponibles
    variables_cpk = [
        'CPK Peajes',
        'CPK Combustible',
        'Rendimiento Kms/Litro',
        'Costo por Litro',
    ]

    # Multiselect con máximo 4 opciones

    col1, col2 = st.columns([2,3])

    with col1:

        seleccionadas = st.multiselect(
            "Selecciona hasta 4 variables para comparar",
            options=variables_cpk,
            default=variables_cpk[:2],
            max_selections=3  # Streamlit >= 1.27
        )

    if len(seleccionadas) == 0:
        st.info("Selecciona al menos una variable para mostrar los gráficos.")
    else:
        cols = st.columns(len(seleccionadas))
        for i, variable in enumerate(seleccionadas):
            with cols[i]:
                fig = comparar_componentes_cpk(
                    df_cpk_periodo,
                    variable=variable,
                    periodos=periodo_strs,
                    width=600,
                    height=800,
                    es_dinero = variable in ['CPK Peajes', 'CPK Combustible', 'Costo por Litro']
 
                )
                st.plotly_chart(fig, use_container_width=True)
        
