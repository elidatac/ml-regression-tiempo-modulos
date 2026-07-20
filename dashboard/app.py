import pandas as pd
import streamlit as st

from parser_logs import (
    obtener_alertas,
    obtener_evaluaciones_slo,
    obtener_metricas_sli,
)


st.set_page_config(
    page_title="Dashboard Operativo - API con FastAPI Modelo de Regresión lineal",
    page_icon="📊",
    layout="wide",
)


st.title("Dashboard Operativo - API Estimador de Tiempo de desarollo de módulos de Software")
st.caption(
    "Monitoreo PROACTIVO."
)


metricas = obtener_metricas_sli()
evaluaciones = obtener_evaluaciones_slo()
alertas = obtener_alertas()


# ESTADO GENERAL

if evaluaciones.empty:
    estado_servicio = "Sin datos"
else:
    ultima_evaluacion = evaluaciones.iloc[-1]

    slo_cumplidos = (
        ultima_evaluacion["slo_latencia"] == "CUMPLIDO"
        and ultima_evaluacion["slo_calidad"] == "CUMPLIDO"
        and ultima_evaluacion["slo_disponibilidad"] == "CUMPLIDO"
    )

    estado_servicio = (
        "Operativo"
        if slo_cumplidos
        else "Con alertas"
    )


st.subheader("Estado general del servicio")

if estado_servicio == "Operativo":
    st.success("Servicio operativo y SLO actuales cumplidos.")
elif estado_servicio == "Con alertas":
    st.warning("El servicio presenta uno o más SLO incumplidos.")
else:
    st.info("Todavía no existen datos suficientes.")


# MÉTRICAS PRINCIPALES

total_predicciones = len(metricas)
total_alertas = len(alertas)

errores = 0

if not alertas.empty:
    errores = len(
        alertas[
            alertas["nivel"] == "ERROR"
        ]
    )

latencia_promedio = 0.0

if not metricas.empty:
    latencia_promedio = metricas["latencia_ms"].mean()


columna_1, columna_2, columna_3, columna_4 = st.columns(4)

columna_1.metric(
    "Predicciones registradas",
    total_predicciones,
)

columna_2.metric(
    "Alertas registradas",
    total_alertas,
)

columna_3.metric(
    "Errores",
    errores,
)

columna_4.metric(
    "Latencia promedio",
    f"{latencia_promedio:.2f} ms",
)


# CUMPLIMIENTO DE SLO

st.subheader("Cumplimiento histórico de SLO")

if evaluaciones.empty:
    st.info("No existen evaluaciones SLO registradas.")

else:
    total_evaluaciones = len(evaluaciones)

    porcentaje_latencia = (
        evaluaciones["slo_latencia"]
        .eq("CUMPLIDO")
        .mean()
        * 100
    )

    porcentaje_calidad = (
        evaluaciones["slo_calidad"]
        .eq("CUMPLIDO")
        .mean()
        * 100
    )

    porcentaje_disponibilidad = (
        evaluaciones["slo_disponibilidad"]
        .eq("CUMPLIDO")
        .mean()
        * 100
    )

    slo_1, slo_2, slo_3 = st.columns(3)

    slo_1.metric(
    "SLO Latencia",
    f"{porcentaje_latencia:.2f} %",
)

    if porcentaje_latencia >= 95:
        slo_1.success("Objetivo cumplido: 95 %")
    else:
        slo_1.error("Objetivo incumplido: 95 %")
   
    slo_2.metric(
    "SLO Calidad",
    f"{porcentaje_calidad:.2f} %",
    )

    if porcentaje_calidad >= 100:
        slo_2.success("Objetivo cumplido: 100 %")
    else:
        slo_2.error("Objetivo incumplido: 100 %")


    slo_3.metric(
        "SLO Disponibilidad",
        f"{porcentaje_disponibilidad:.2f} %",
    )

    if porcentaje_disponibilidad >= 99:
        slo_3.success("Objetivo cumplido: 99 %")
    else:
        slo_3.error("Objetivo incumplido: 99 %")


# GRÁFICAS

st.subheader("Latencia de las predicciones")

if metricas.empty:
    st.info("No existen métricas de latencia.")
else:
    datos_latencia = metricas[
        [
            "fecha",
            "latencia_ms",
        ]
    ].set_index("fecha")

    st.line_chart(datos_latencia)


st.subheader("Duración estimada por predicción")

if metricas.empty:
    st.info("No existen predicciones registradas.")
else:
    datos_predicciones = metricas[
        [
            "fecha",
            "prediccion_dias",
        ]
    ].set_index("fecha")

    st.line_chart(datos_predicciones)


# ALERTAS POR TIPO

st.subheader("Alertas por tipo")

if alertas.empty:
    st.success("No existen alertas registradas.")
else:
    alertas_por_tipo = (
        alertas["tipo"]
        .value_counts()
        .rename_axis("tipo")
        .reset_index(name="cantidad")
    )

    st.bar_chart(
        alertas_por_tipo.set_index("tipo")
    )


# HISTORIAL DE MÉTRICAS

st.subheader("Historial de predicciones")

if metricas.empty:
    st.info("No existen predicciones registradas.")
else:
    historial = metricas.copy()

    historial["fecha"] = historial["fecha"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    st.dataframe(
        historial.sort_values(
            "fecha",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )


# HISTORIAL DE ALERTAS

st.subheader("Últimas alertas e incidentes")

if alertas.empty:
    st.success("No existen alertas o incidentes.")
else:
    ultimas_alertas = alertas.copy()

    ultimas_alertas["fecha"] = (
        ultimas_alertas["fecha"]
        .dt.strftime("%Y-%m-%d %H:%M:%S")
    )

    st.dataframe(
        ultimas_alertas.sort_values(
            "fecha",
            ascending=False,
        ).head(20),
        use_container_width=True,
        hide_index=True,
    )