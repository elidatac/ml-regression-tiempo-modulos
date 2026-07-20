from app.logger_config import logger

SLO_LATENCIA_MS = 500
SLO_PREDICCION_MINIMA = 0


def evaluar_slos(latencia_ms, prediccion, http_status):
    """
    Evalúa el cumplimiento de los SLO del servicio.
    """

    resultado = {
        "slo_latencia": latencia_ms < SLO_LATENCIA_MS,
        "slo_calidad": prediccion > SLO_PREDICCION_MINIMA,
        "slo_disponibilidad": http_status == 200,
    }

    logger.info(
        "Evaluación SLO -> "
        "LATENCIA=%s, "
        "CALIDAD=%s, "
        "DISPONIBILIDAD=%s",
        "CUMPLIDO" if resultado["slo_latencia"] else "INCUMPLIDO",
        "CUMPLIDO" if resultado["slo_calidad"] else "INCUMPLIDO",
        "CUMPLIDO" if resultado["slo_disponibilidad"] else "INCUMPLIDO",
    )

    return resultado