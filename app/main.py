from time import perf_counter

from datetime import datetime, timezone
import json
from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.logger_config import logger

from app.monitoring import evaluar_slos
from app.alert_manager import generar_alertas

from time import perf_counter, sleep

BASE_DIR = Path(__file__).resolve().parent
RUTA_MODELO = BASE_DIR / "modelo.pkl"
RUTA_METADATA = BASE_DIR / "metadata_modelo.json"

try:
    modelo = joblib.load(RUTA_MODELO)

    logger.info(
        "Modelo cargado correctamente desde %s",
        RUTA_MODELO
    )

except Exception as error:
    logger.exception(
        "No fue posible cargar el modelo desde %s: %s",
        RUTA_MODELO,
        error
    )

    raise RuntimeError(
        "No fue posible cargar el modelo de Machine Learning."
    ) from error

try:
    with open(RUTA_METADATA, "r", encoding="utf-8") as archivo:
        metadata_modelo = json.load(archivo)

    logger.info(
        "Metadatos del modelo cargados correctamente desde %s",
        RUTA_METADATA
    )

except Exception as error:
    logger.exception(
        "No fue posible cargar los metadatos desde %s: %s",
        RUTA_METADATA,
        error
    )

    raise RuntimeError(
        "No fue posible cargar los metadatos del modelo."
    ) from error


# Crear aplicación FastAPI
app = FastAPI(
    title="API Estimador de Tiempo de Desarrollo",
    description=(
        "Predice la duración estimada en días para desarrollar "
        "un módulo de software e incluye trazabilidad del modelo."
    ),
    version="1.1.0"
)

# Modelo de entrada
class ModuloInput(BaseModel):
    interfaces_usuario: int = Field(..., ge=1, le=15, description="Número de interfaces de usuario")
    funcionalidades_backend: int = Field(..., ge=1, le=20, description="Cantidad de funcionalidades del backend")
    complejidad: int = Field(..., ge=1, le=5, description="Nivel de complejidad del módulo")
    horas_disponibles_dia: int = Field(..., ge=4, le=8, description="Horas efectivas disponibles por día")
    simular_latencia: bool = Field(
        default=False,
        description="Simula una respuesta lenta para probar el SLO de latencia"
    )

    simular_error: bool = Field(
        default=False,
        description="Simula un error interno para probar disponibilidad"
    )


# Endpoint raíz
@app.get(
    "/",
    summary="Verificar estado de la API",
    description="Permite comprobar que la API se encuentra en ejecución."
)
def inicio():
    logger.info("Consulta realizada al endpoint raíz")

    return {
        "proyecto": "Estimador de Tiempo de Desarrollo",
        "version_api": "1.1.0",
        "estado": "API activa",
        "modelo": metadata_modelo.get("modelo"),
        "version_modelo": metadata_modelo.get("version_modelo"),
        "mlflow_run_id": metadata_modelo.get("mlflow_run_id")
    }

# Endpoint de predicción
@app.post(
    "/predict",
    summary="Realizar predicción",
    description="Predice la duración estimada en días para desarrollar un módulo de software."
)
def predecir(datos: ModuloInput):
    """
    Realiza una predicción y evalúa los SLO de latencia
    y calidad del resultado.
    """
    inicio_medicion = perf_counter()

    logger.info("Nueva solicitud de predicción recibida")

    logger.info(
        "Entradas recibidas -> "
        "interfaces_usuario=%s, "
        "funcionalidades_backend=%s, "
        "complejidad=%s, "
        "horas_disponibles_dia=%s",
        datos.interfaces_usuario,
        datos.funcionalidades_backend,
        datos.complejidad,
        datos.horas_disponibles_dia
    )

    try:
        if datos.simular_error:
            logger.error(
                "INCIDENTE_SIMULADO -> Error interno solicitado para prueba"
            )
            raise RuntimeError("Error interno simulado")

        if datos.simular_latencia:
            logger.warning(
                "INCIDENTE_SIMULADO -> Latencia artificial de 0.7 segundos"
            )
            sleep(0.7)
            
        entrada = pd.DataFrame([
            {
                "interfaces_usuario": datos.interfaces_usuario,
                "funcionalidades_backend": (
                    datos.funcionalidades_backend
                ),
                "complejidad": datos.complejidad,
                "horas_disponibles_dia": (
                    datos.horas_disponibles_dia
                )
            }
        ])

        prediccion = modelo.predict(entrada)[0]

        duracion_estimada = round(
            float(prediccion),
            2
        )

        latencia_segundos = perf_counter() - inicio_medicion
        latencia_ms = round(latencia_segundos * 1000, 2)

        # SLO: SLO de latencia: respuesta menor a 500 ms.
        slo_latencia_cumplido = latencia_ms < 500

        # SLO: SLO de calidad: predicción mayor que 0 días.
        slo_calidad_cumplido = duracion_estimada > 0

        estado_slo_latencia = (
            "CUMPLIDO"
            if slo_latencia_cumplido
            else "INCUMPLIDO"
        )

        estado_slo_calidad = (
            "CUMPLIDO"
            if slo_calidad_cumplido
            else "INCUMPLIDO"
        )

        logger.info(
            "Métricas SLI -> "
            "latencia_ms=%.2f, "
            "prediccion_dias=%.2f, "
            "http_status=200",
            latencia_ms,
            duracion_estimada
        )

        slos = evaluar_slos(
            latencia_ms=latencia_ms,
            prediccion=duracion_estimada,
            http_status=200
        )

        generar_alertas(
            slos=slos,
            latencia_ms=latencia_ms,
            prediccion=duracion_estimada
        )

        logger.info(
            "Predicción procesada correctamente -> %.2f días",
            duracion_estimada
        )

        return {
            "mensaje": "Predicción realizada correctamente.",
            "duracion_estimada_dias": duracion_estimada,
            "unidad": "días",
            "monitoreo": {
                "latencia_ms": latencia_ms,
                "http_status": 200,
                "slo_latencia": {
                    "objetivo": "Respuesta menor a 500 ms",
                    "cumplido": slos["slo_latencia"]
                },
                "slo_calidad": {
                    "objetivo": "Predicción mayor a 0 días",
                    "cumplido": slos["slo_calidad"]
                }
            },
            "trazabilidad": {
                "modelo": metadata_modelo.get("modelo"),
                "version_modelo": metadata_modelo.get(
                    "version_modelo"
                ),
                "mlflow_run_id": metadata_modelo.get(
                    "mlflow_run_id"
                ),
                "mlflow_experiment_id": metadata_modelo.get(
                    "mlflow_experiment_id"
                ),
                "fecha_entrenamiento": metadata_modelo.get(
                    "fecha_entrenamiento"
                ),
                "timestamp_prediccion": datetime.now(
                    timezone.utc
                ).isoformat()
            }
        }

    except Exception as error:
        latencia_segundos = perf_counter() - inicio_medicion
        latencia_ms = round(latencia_segundos * 1000, 2)

        logger.exception(
            "ALERTA SLO_DISPONIBILIDAD_INCUMPLIDO -> "
            "Error al realizar la predicción | "
            "latencia_ms=%.2f | http_status=500 | error=%s",
            latencia_ms,
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error al realizar la predicción."
        ) from error