from fastapi import FastAPI
from pydantic import BaseModel, Field
import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
modelo = joblib.load(BASE_DIR / "modelo.pkl")

# Crear aplicación FastAPI
app = FastAPI(
    title="API Estimador de Tiempo de Desarrollo",
    description="Predice la duración estimada en días para desarrollar un módulo de software.",
    version="1.0.0"
)

# Modelo de entrada
class ModuloInput(BaseModel):
    interfaces_usuario: int = Field(..., ge=1, le=15, description="Número de interfaces de usuario")
    funcionalidades_backend: int = Field(..., ge=1, le=20, description="Cantidad de funcionalidades del backend")
    complejidad: int = Field(..., ge=1, le=5, description="Nivel de complejidad del módulo")
    horas_disponibles_dia: int = Field(..., ge=4, le=8, description="Horas efectivas disponibles por día")


# Endpoint raíz
@app.get(
    "/",
    summary="Verificar estado de la API",
    description="Permite comprobar que la API se encuentra en ejecución."
)
def inicio():
    return {
        "proyecto": "Estimador de Tiempo de Desarrollo",
        "version": "1.0.0",
        "estado": "API activa"
    }

# Endpoint de predicción
@app.post(
    "/predict",
    summary="Realizar predicción",
    description="Predice la duración estimada en días para desarrollar un módulo de software."
)
def predecir(datos: ModuloInput):
    """
    Predice la duración estimada en días para desarrollar un módulo de software.
    """

    entrada = pd.DataFrame([{
        "interfaces_usuario": datos.interfaces_usuario,
        "funcionalidades_backend": datos.funcionalidades_backend,
        "complejidad": datos.complejidad,
        "horas_disponibles_dia": datos.horas_disponibles_dia
    }])

    prediccion = modelo.predict(entrada)[0]

    return {
        "mensaje": "Predicción realizada correctamente.",
        "duracion_estimada_dias": round(float(prediccion), 2),
        "unidad": "días"
    }