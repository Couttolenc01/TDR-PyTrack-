
# Este archivo define funciones para analizar el historial de cargas de combustible entre eventos para cada tracto.
# Permite calcular métricas operativas entre recargas de combustible.

# Función: historial_entre_cargas
# - Procesa el DataFrame de órdenes para cada tracto, identificando los periodos entre cargas de combustible.
# - Calcula métricas como kms recorridos, costos, rendimiento, CPK y otros indicadores entre cargas.
# - Devuelve dos DataFrames: uno detallado por evento de carga y otro agrupado por tracto.
# - Es fundamental para analizar el desempeño operativo y los costos entre recargas.


def historial_entre_cargas(df):

    import pandas as pd
    import numpy as np
    from numpy import mean


    unidades = df['Tracto'].unique()

    df_p = df[(df['Periodo'] >= '2025-01') & (df['Periodo'] < '2025-03')]
    df_p = df.copy()

    historial_cargas = []

    for ud in unidades:
        df_ud = df_p[df_p['Tracto'] == ud].sort_values('Inicio de la Orden', ascending=True)
        cont_kms = 0
        cont_cargas = 0
        viajes = 0
        fecha_ant_carga = np.nan
        no_rutas_distintas = set()
        no_proyectos_distintos = set()
        mean_kms_l = []

        costo_peajes_entre_cargas = 0
        costo_mant_entre_cargas = 0

        for i in range(len(df_ud)):
            if df_ud['Orden con Costo de Combustible'].iloc[i]:
                no_rutas_distintas.add(df_ud['Ruta Ciudades'].iloc[i])
                no_proyectos_distintos.add(df_ud['Proyecto'].iloc[i])
                mean_kms_l.append(df_ud['kmstotales'].iloc[i])
                cont_kms += df_ud['kmstotales'].iloc[i]
                cont_cargas += 1
                fecha_carga = df_ud['Cierre de la Orden'].iloc[i]
                rutas = len(no_rutas_distintas)
                proyectos = len(no_proyectos_distintos)
                mean_kms = sum(mean_kms_l) / len(mean_kms_l) if mean_kms_l else 0
                litros_carga = df_ud['Litros'].iloc[i]
                costo_plitro = df_ud['Costo por litro'].iloc[i]
                costo_carga = df_ud['Costo Combustible'].iloc[i]

                costo_peajes_entre_cargas += df_ud['Costo Peajes'].iloc[i]
                costo_mant_entre_cargas += df_ud['Costo Mantenimiento'].iloc[i] 

                costo_total = costo_carga + costo_peajes_entre_cargas + costo_mant_entre_cargas
                
                # --- Corrección para evitar división por cero ---
                if litros_carga != 0:
                    rendimiento = cont_kms / litros_carga
                else:
                    rendimiento = np.nan
                if cont_kms != 0:
                    cpk = costo_carga / cont_kms
                    cpk_peajes = costo_peajes_entre_cargas / cont_kms
                    cpk_mant = costo_mant_entre_cargas / cont_kms
                else:
                    cpk = np.nan
                    cpk_peajes = np.nan
                    cpk_mant = np.nan

                periodo = df_ud['Periodo'].iloc[i]
                kms_por_dia = cont_kms / (fecha_carga - fecha_ant_carga).days if pd.notna(fecha_ant_carga) and (fecha_carga - fecha_ant_carga).days != 0 else 0
                historial_cargas.append([
                    periodo, ud, cont_cargas, fecha_carga, fecha_ant_carga, litros_carga,costo_plitro,rendimiento, costo_carga, costo_peajes_entre_cargas, costo_mant_entre_cargas,
                    costo_total, cpk,cpk_peajes,cpk_mant, cont_kms, viajes, rutas, proyectos, mean_kms, kms_por_dia
                ])
                fecha_ant_carga = fecha_carga
                cont_kms = 0
                viajes = 0
                no_rutas_distintas = set()
                no_proyectos_distintos = set()
                mean_kms_l = []

                costo_peajes_entre_cargas = 0
                costo_mant_entre_cargas = 0
            else:
                cont_kms += df_ud['kmstotales'].iloc[i]
                no_rutas_distintas.add(df_ud['Ruta Ciudades'].iloc[i])
                no_proyectos_distintos.add(df_ud['Proyecto'].iloc[i])
                mean_kms_l.append(df_ud['kmstotales'].iloc[i])

                costo_peajes_entre_cargas += df_ud['Costo Peajes'].iloc[i]
                costo_mant_entre_cargas += df_ud['Costo Mantenimiento'].iloc[i]

            viajes += 1

    historial_cargas = pd.DataFrame(
        historial_cargas, 
        columns=[
            'Periodo',
            'Tracto',
            'No. de Carga Combustible',
            'Fecha Orden de Ant. Carga',
            'Fecha Orden de Carga',
            'Litros Combustible Cargados',
            'Costo por Litro',
            'Rendimiento Kms/Litro',
            'Costo de Combustible',
            'Costo de Peajes',
            'Costo de Mantenimiento',
            'Costo Total',            
            'CPK Combustible',
            'CPK Peajes',
            'CPK Mantenimiento',
            'KMs Recorridos desde Última Carga',
            'Viajes entre Cargas',
            'Rutas Distintas',
            'Proyectos Distintos',
            'Promedio Kms por Viaje',
            'Kms Recorridos por Día'
        ]
    )

    historial_cargas['Tiempo entre Cargas'] = (
        historial_cargas['Fecha Orden de Carga'] - historial_cargas['Fecha Orden de Ant. Carga']
    ).dt.total_seconds() / (24 * 3600)

    # Limpiar inf y NaN en filas
    historial_cargas = historial_cargas[
        ~historial_cargas['Tiempo entre Cargas'].isin([np.inf, -np.inf]) &
        ~historial_cargas['Tiempo entre Cargas'].isna()
    ]

    historial_cargas['Kms Totales'] = historial_cargas['KMs Recorridos desde Última Carga'].fillna(0)
    historial_cargas['No. Viajes'] = historial_cargas['Viajes entre Cargas'].fillna(0)

    hist_cargas_grouped = historial_cargas.groupby(['Tracto']).agg({
        'No. de Carga Combustible': 'median',
        'Tiempo entre Cargas': 'mean',
        'KMs Recorridos desde Última Carga': 'mean',
        'Litros Combustible Cargados': 'mean',
        'Costo por Litro': 'mean',
        'Rendimiento Kms/Litro': 'mean',
        'Costo de Combustible': 'mean',
        'Costo de Peajes': 'mean',
        'Costo de Mantenimiento': 'mean',
        'Costo Total': 'mean',
        'CPK Combustible': 'mean',
        'CPK Peajes': 'mean',
        'CPK Mantenimiento': 'mean',
        'Viajes entre Cargas': 'median',
        'Rutas Distintas': 'median',
        'Proyectos Distintos': 'median',
        'Promedio Kms por Viaje': 'mean',
        'Kms Recorridos por Día': 'mean',
        'Kms Totales': 'sum',
        'No. Viajes': 'sum'
    }).reset_index()

    hist_cargas_grouped.set_index('Tracto', inplace=True)

    return historial_cargas, hist_cargas_grouped
