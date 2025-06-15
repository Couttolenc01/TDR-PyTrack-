
# Este archivo contiene funciones para filtrar y agrupar datos de manera interactiva en Streamlit.

# Función: search_and_filter_interface
# - Proporciona una interfaz para buscar y filtrar el DataFrame por columna, rango numérico, fechas o valores de texto.
# - Usa AgGrid para mostrar los resultados filtrados de manera interactiva.
# - Permite aplicar filtros complejos y ver los resultados en tiempo real.

# Función: groupby_interface
# - Permite al usuario agrupar y resumir los datos por una o más columnas y aplicar funciones de agregación (suma, media, etc.).
# - Muestra el resultado en una tabla interactiva.
# - Es útil para obtener resúmenes personalizados de los datos filtrados.

def search_and_filter_interface(df_search, columnas_contables=[], columnas_forzar_fecha=[], columnas_forzar_str=[], columnas_forzar_num=[]
                            , include_numeric=True):

    import streamlit as st
    import pandas as pd
    from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
    import math
    from turtle import width
    import plotly.graph_objects as go
    import colorsys
    import numpy as np  
    from df_filter_utils import groupby_interface

    # --- formateador en JS -------
    currency_fmt = JsCode("""
    function(params) {
        if (params.value === null || params.value === undefined) {
            return '';
        }
        return '$ ' + Number(params.value)
            .toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    }
    """)

    df = df_search.copy()

    col1, col2, col3, space = st.columns([2, 5, 2, 3])
    with col1:
        st.markdown("Buscar en Columna:")
        if include_numeric:
            # Incluir columnas numéricas en el selectbox
            columnas_disponibles = df.columns.tolist()
        else:
            # Excluir columnas numéricas
            columnas_disponibles = [col for col in df.columns if not pd.api.types.is_numeric_dtype(df[col])]

        column = st.selectbox("", columnas_disponibles, key="col_select", label_visibility="collapsed")
        
    with col2:
        # Determinar tipo de columna (forzado o automático)
        if column in columnas_forzar_fecha:
            tipo = "fecha"
        elif column in columnas_forzar_num:
            tipo = "num"
        elif column in columnas_forzar_str:
            tipo = "str"
        else:
            if pd.api.types.is_numeric_dtype(df[column]):
                tipo = "num"
            elif pd.api.types.is_datetime64_any_dtype(df[column]):
                tipo = "fecha"
            elif pd.api.types.is_timedelta64_dtype(df[column]):
                tipo = "num"
            else:
                tipo = "str"

        if tipo == "num":
            st.markdown("Selecciona rango numérico:")
            min_val = math.floor(df[column].min())
            max_val = math.ceil(df[column].max())
            # Evitar error de rango inválido
            if min_val == max_val:
                valor = (min_val, max_val)
                st.info(f"Solo existe un valor posible: {min_val}")
            else:
                valor = st.slider(
                    "",
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val),
                    step=1,
                    key="num_slider",
                    label_visibility="collapsed"
                )
            # Si es la columna de duración en horas, mostrar conversión
            if column.lower().startswith("duración viaje") and "hrs" in column.lower():
                st.caption(
                    f"Rango seleccionado: "
                    f"{horas_a_dhm(valor[0])} → {horas_a_dhm(valor[1])}"
                )
        elif tipo == "fecha":
            min_date = pd.to_datetime(df[column]).min().date()
            max_date = pd.to_datetime(df[column]).max().date()
            st.markdown("Selecciona rango de fechas:")
            col_fecha1, col_fecha2 = st.columns(2)
            with col_fecha1:
                fecha1 = st.date_input("Fecha inicio", value=min_date, min_value=min_date, max_value=max_date, key="fecha_inicio", label_visibility="collapsed")
            with col_fecha2:
                fecha2 = st.date_input("Fecha fin", value=max_date, min_value=min_date, max_value=max_date, key="fecha_fin", label_visibility="collapsed")
            # Lógica para determinar los valores efectivos
            if fecha1 is None and fecha2 is None:
                fecha1 = min_date
                fecha2 = max_date
            elif fecha1 is None:
                fecha1 = min_date
            elif fecha2 is None:
                fecha2 = max_date
            valor = (fecha1, fecha2)
        else:
            st.markdown("Valor a buscar:")
            unique_options = sorted(df[column].dropna().astype(str).unique().tolist())
            valor = st.multiselect(
                "",
                options=unique_options,
                default=[],
                key="text_input",
                label_visibility="collapsed"
            )
            if not valor:
                st.caption("Opciones: " + ", ".join(unique_options[:20]) + (" ..." if len(unique_options) > 20 else ""))
            else:
                st.caption("Filtrando por: " + ", ".join(valor))

    with col3:
        st.markdown("Confirmar:")
        aplicar = st.button("Aplicar Filtro", key="aplicar_btn")

    # Solo filtra al presionar el botón
    if 'filtro' not in st.session_state or aplicar:
        if tipo == "num":
            filtro = df[(df[column] >= valor[0]) & (df[column] <= valor[1])]
        elif tipo == "fecha":
            filtro = df[
                (pd.to_datetime(df[column]).dt.date >= valor[0])
                & (pd.to_datetime(df[column]).dt.date <= valor[1])
            ]
        else:
            if valor:
                filtro = df[df[column].astype(str).isin(valor)]
            else:
                filtro = df
        st.session_state.filtro = filtro
    else:
        filtro = st.session_state.filtro
        
    #groupby_interface(filtro)

    # Configuración visual contable
    gb = GridOptionsBuilder.from_dataframe(filtro)
    for col in filtro.columns:
        gb.configure_column(col, filter=False, resizable=True, sortable=True, wrapText=True)
        if col in columnas_contables:
            gb.configure_column(
                col,
                type=["numericColumn", "rightAligned"],
                valueFormatter=currency_fmt,
                cellStyle={'text-align': 'right'}
            )
    #gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=30)
    gridOptions = gb.build()

    df_final = AgGrid(
        filtro,
        gridOptions=gridOptions,
        enable_enterprise_modules=True,
        allow_unsafe_jscode=True,
        update_mode='MODEL_CHANGED',
        height=380
    )

    df_filtrado_en_aggrid = pd.DataFrame(df_final['data'])

    return df_filtrado_en_aggrid
        
def groupby_interface(df):
    
    import streamlit as st
    import pandas as pd
    import numpy as np
    from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
    from turtle import width
    import math

    with st.expander("Agrupar y resumir información (opcional)", expanded=False):

        opciones_agrupado = [col for col in ["Periodo", "Tracto"] if col in df.columns]
        opciones_resumen = [col for col in ["kmstotales"] if col in df.columns]

        agrupado = st.multiselect(
            "¿Por qué quieres agrupar la información?",
            options=df.columns.tolist(),
            default=opciones_agrupado,
            key="agrupado"
        )

        opciones_para_resumir = [col for col in df.columns if col not in agrupado]
        resumen = st.multiselect(
            "¿Qué datos quieres resumir? (por ejemplo, kilómetros, costos, etc)",
            options=opciones_para_resumir,
            default=opciones_resumen,
            key="resumen"
        )

        funciones = {}
        opciones_funcion = ["Suma", "Promedio", "Mínimo", "Máximo", "Cantidad", "Valores únicos", "Mediana", "Desviación estándar"]
        equivalencias = {
            "Suma": "sum",
            "Promedio": "mean",
            "Mínimo": "min",
            "Máximo": "max",
            "Cantidad": "count",
            "Valores únicos": "nunique",
            "Mediana": "median",
            "Desviación estándar": "std"
        }
        for dato in resumen:
            funcion = st.selectbox(
                f"¿Cómo quieres resumir {dato}?",
                options=opciones_funcion,
                index=0 if dato == "kmstotales" else 1,
                key=f"funcion_{dato}"
            )
            funciones[dato] = equivalencias[funcion]

        if agrupado and funciones and resumen:
            # Solo aplica funciones numéricas a columnas numéricas
            funciones_validas = {}
            for col, func in funciones.items():
                if func in ["sum", "mean", "min", "max", "median", "std"]:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        funciones_validas[col] = func
                else:
                    funciones_validas[col] = func
            if funciones_validas:
                resultado = df.groupby(agrupado).agg(funciones_validas).reset_index()
                st.dataframe(resultado)
            else:
                st.warning("No hay columnas numéricas seleccionadas para las funciones de agregación numérica.")
        else:
            st.info("Selecciona al menos una opción para agrupar y una para resumir para ver el resultado.")

