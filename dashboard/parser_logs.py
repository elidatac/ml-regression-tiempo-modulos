import re
from pathlib import Path

import pandas as pd


# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_LOG = BASE_DIR / "logs" / "api.log"


PATRON_LINEA = re.compile(
    r"^(?P<fecha>\d{4}-\d{2}-\d{2} "
    r"\d{2}:\d{2}:\d{2},\d{3})"
    r" \| (?P<nivel>[A-Z]+)"
    r" \| (?P<logger>[^|]+)"
    r" \| (?P<mensaje>.*)$"
)

PATRON_METRICAS = re.compile(
    r"latencia_ms=(?P<latencia>-?\d+(?:\.\d+)?), "
    r"prediccion_dias=(?P<prediccion>-?\d+(?:\.\d+)?), "
    r"http_status=(?P<http_status>\d+)"
)

PATRON_SLO = re.compile(
    r"LATENCIA=(?P<slo_latencia>[A-Z]+), "
    r"CALIDAD=(?P<slo_calidad>[A-Z]+), "
    r"DISPONIBILIDAD=(?P<slo_disponibilidad>[A-Z]+)"
)


def leer_lineas_log():
    """
    Lee el archivo api.log 
    """

    if not RUTA_LOG.exists():
        return []

    lineas_validas = []

    with open(RUTA_LOG, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            coincidencia = PATRON_LINEA.match(linea.strip())

            if coincidencia:
                registro = coincidencia.groupdict()
                registro["mensaje"] = registro["mensaje"].strip()
                registro["logger"] = registro["logger"].strip()
                lineas_validas.append(registro)

    return lineas_validas


def obtener_eventos():
    """
    Convierte todas las líneas válidas en un DataFrame.
    """

    registros = leer_lineas_log()

    if not registros:
        return pd.DataFrame(
            columns=[
                "fecha",
                "nivel",
                "logger",
                "mensaje",
            ]
        )

    dataframe = pd.DataFrame(registros)

    dataframe["fecha"] = pd.to_datetime(
        dataframe["fecha"],
        format="%Y-%m-%d %H:%M:%S,%f",
        errors="coerce",
    )

    dataframe = dataframe.dropna(subset=["fecha"])

    return dataframe.sort_values("fecha").reset_index(drop=True)


def obtener_metricas_sli():
    """
    Extrae del log las métricas SLI de cada predicción.
    """

    eventos = obtener_eventos()
    metricas = []

    if eventos.empty:
        return pd.DataFrame(
            columns=[
                "fecha",
                "latencia_ms",
                "prediccion_dias",
                "http_status",
            ]
        )

    for _, evento in eventos.iterrows():
        mensaje = evento["mensaje"]

        if not mensaje.startswith("Métricas SLI"):
            continue

        coincidencia = PATRON_METRICAS.search(mensaje)

        if coincidencia:
            datos = coincidencia.groupdict()

            metricas.append(
                {
                    "fecha": evento["fecha"],
                    "latencia_ms": float(datos["latencia"]),
                    "prediccion_dias": float(datos["prediccion"]),
                    "http_status": int(datos["http_status"]),
                }
            )

    return pd.DataFrame(metricas)


def obtener_evaluaciones_slo():
    """
    Extrae el resultado de las evaluaciones SLO.
    """

    eventos = obtener_eventos()
    evaluaciones = []

    if eventos.empty:
        return pd.DataFrame(
            columns=[
                "fecha",
                "slo_latencia",
                "slo_calidad",
                "slo_disponibilidad",
            ]
        )

    for _, evento in eventos.iterrows():
        mensaje = evento["mensaje"]

        if not mensaje.startswith("Evaluación SLO"):
            continue

        coincidencia = PATRON_SLO.search(mensaje)

        if coincidencia:
            datos = coincidencia.groupdict()

            evaluaciones.append(
                {
                    "fecha": evento["fecha"],
                    "slo_latencia": datos["slo_latencia"],
                    "slo_calidad": datos["slo_calidad"],
                    "slo_disponibilidad": (
                        datos["slo_disponibilidad"]
                    ),
                }
            )

    return pd.DataFrame(evaluaciones)


def obtener_alertas():
    """
    Extrae todas las alertas e incidentes simulados registrados.
    """

    eventos = obtener_eventos()

    if eventos.empty:
        return pd.DataFrame(
            columns=[
                "fecha",
                "nivel",
                "tipo",
                "mensaje",
            ]
        )

    alertas = eventos[
        eventos["nivel"].isin(["WARNING", "ERROR"])
    ].copy()

    if alertas.empty:
        return pd.DataFrame(
            columns=[
                "fecha",
                "nivel",
                "tipo",
                "mensaje",
            ]
        )

    alertas["tipo"] = alertas["mensaje"].apply(
        clasificar_alerta
    )

    return alertas[
        [
            "fecha",
            "nivel",
            "tipo",
            "mensaje",
        ]
    ].reset_index(drop=True)


def clasificar_alerta(mensaje):
    """
    Clasifica una alerta según el texto del log.
    """

    if "SLO_LATENCIA" in mensaje:
        return "Latencia"

    if "SLO_CALIDAD" in mensaje:
        return "Calidad"

    if "SLO_DISPONIBILIDAD" in mensaje:
        return "Disponibilidad"

    if "INCIDENTE_SIMULADO" in mensaje:
        return "Incidente simulado"

    return "Otro"