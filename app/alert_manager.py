from app.logger_config import logger


def generar_alertas(slos, latencia_ms, prediccion):
    """
    Genera alertas únicamente cuando un SLO no se cumple.
    """

    if not slos["slo_latencia"]:
        logger.warning(
            "ALERTA SLO_LATENCIA_INCUMPLIDO -> "
            "latencia_ms=%.2f, objetivo_ms=<500",
            latencia_ms
        )

    if not slos["slo_calidad"]:
        logger.warning(
            "ALERTA SLO_CALIDAD_INCUMPLIDO -> "
            "prediccion_dias=%.2f, objetivo=>0",
            prediccion
        )

    if not slos["slo_disponibilidad"]:
        logger.warning(
            "ALERTA SLO_DISPONIBILIDAD_INCUMPLIDO"
        )