# Proyecto: Estimador de Tiempo de Desarrollo de Módulos de Software

## Descripción

Este proyecto implementa un modelo de Regresión Lineal para estimar el tiempo de desarrollo (en días) de módulos de software a partir de sus características principales. El modelo fue entrenado con datos sintéticos y posteriormente desplegado mediante una API REST desarrollada con FastAPI y empaquetada en un contenedor Docker para validar su funcionamiento en un entorno local.


## Objetivo

Desarrollar un modelo de regresión lineal capaz de estimar el tiempo requerido para desarrollar módulos de software considerando las siguientes entradas:

- Número de interfaces de usuario.
- Cantidad de funcionalidades del backend.
- Nivel de complejidad del módulo.
- Horas disponibles de trabajo por día.

Posteriormente, desplegar el modelo mediante una API desarrollada con FastAPI y contenerizar la solución utilizando Docker.



## Tecnologías utilizadas

- Python 3.11
- Scikit-learn 1.6.1
- Pandas 2.2.2
- FastAPI 0.138.0
- Pydantic 2.13.4
- Uvicorn 0.49.0
- Docker Desktop



## Estructura del proyecto


```text
ml-tiempo-modulos/
│
├── app/
│   ├── main.py
│   ├── modelo.pkl
│   └── metadata_modelo.json
│
├── datos/
│   └── dataset_sintetico.csv
│
├── docs/
│   ├── Manual_Despliegue_Nube.md
│   └── Validacion_Pruebas.md
│
├── evidencias/
│
├── Dockerfile
├── requirements.txt
├── README.md
├── entrenamiento_modelo_regresion.ipynb
└── .gitignore
```

## Conjunto de datos

El modelo fue entrenado utilizando un conjunto de **1,000 registros sintéticos**, donde cada registro representa un módulo de software con diferentes niveles de complejidad y características de desarrollo.

### Variables de entrada (X)

- Interfaces de usuario.
- Funcionalidades del backend.
- Complejidad.
- Horas disponibles por día.

### Variable objetivo (y)

- Duración estimada del desarrollo (días).

---

## Resultados obtenidos

| Métrica | Valor |
|---------|-------:|
| MAE | 2.39 días |
| RMSE | 3.15 días |
| R² | 0.9323 |

---

##Interpretación:

El modelo alcanzó un coeficiente de determinación (R²) de 93.23 %, lo que indica una buena capacidad para estimar la duración del desarrollo sobre el conjunto de datos sintéticos generado.

---

## API REST

La API desarrollada con FastAPI permite verificar el estado del servicio y realizar predicciones del tiempo estimado de desarrollo mediante solicitudes HTTP.

### Endpoints

| Método | Endpoint | Descripción |
|---------|----------|-------------|
| GET | `/` | Verifica que la API se encuentra disponible. |
| POST | `/predict` | Realiza la predicción estimando la duración del desarrollo de un módulo de software. |

### Ejemplo de solicitud

```json
{
  "interfaces_usuario": 6,
  "funcionalidades_backend": 12,
  "complejidad": 4,
  "horas_disponibles_dia": 8
}
```

### Ejemplo de respuesta

```json
{
  "mensaje": "Predicción realizada correctamente.",
  "duracion_estimada_dias": 18.42,
  "unidad": "días"
}
```

---

## Ejecución con Docker

Construir la imagen:

```bash
docker build -t ml-tiempo-modulos .
```

Ejecutar el contenedor:

```bash
docker run -p 8000:8000 ml-tiempo-modulos
```

Acceder a la documentación interactiva de la API:

```
http://localhost:8000/docs
```

---

## Autor

**Carmen Elizabeth Juárez Mortera**

Proyecto para la fase II de ejecución de modelos de Machine Learning mediante FastAPI y Docker.
