# Manual de Despliegue en Azure Container Apps

## 0. Generales

Para realizar el despliegue es necesario haber construido previamente la imagen Docker del proyecto y contar con una suscripción activa en Microsoft Azure.

---

## 1. Objetivo

El presente documento describe el procedimiento para desplegar en la nube la API del modelo de Regresión Lineal desarrollada con FastAPI y contenerizada mediante Docker. La nube seleccionada es **Azure Container Apps**, un servicio PaaS de Microsoft Azure diseñado para ejecutar aplicaciones basadas en contenedores de forma escalable y administrada.

---

## 2. Arquitectura de despligue

La arquitectura de despliegue propuesta se basa en un contenedor Docker y servicios administrados de Azure.

```text
                   Usuario
                       │
                       ▼
             Azure Container Apps
                       │
                       ▼
                FastAPI + Uvicorn
                       │
                       ▼
          Modelo de Regresión Lineal
                       │
                       ▼
                  modelo.pkl
```

---

## 3. Requerimientos técnicos

### Software requerido

- Docker Desktop
- Azure CLI
- Git
- Navegador Web

### Cuenta de servicios

- Suscripción activa de Microsoft Azure
- Azure Container Registry (ACR)

### Recursos necesarios

- Imagen Docker previamente construida.
- Código fuente del proyecto (Github).
- Archivo Dockerfile.
- Archivo requirements.txt.

---

## 4. Procedimiento de despliegue

### Paso 1. Crear un Resource Group

Ingresar al Portal de Azure y crear un **Resource Group**, el cual permitirá organizar todos los recursos relacionados con el proyecto.

**Resultado esperado**

Al finalizar este paso deberá existir un **Resource Group** activo que agrupe todos los recursos utilizados durante el despliegue de la aplicación.

---

### Paso 2. Crear un Azure Container Registry (ACR)

Crear un registro de contenedores donde se almacenará la imagen Docker que será utilizada durante el despliegue.

**Resultado esperado**

El Azure Container Registry deberá encontrarse creado y disponible para almacenar la imagen Docker que será utilizada por Azure Container Apps.

---

### Paso 3. Construir la imagen Docker

Desde la carpeta raíz del proyecto ejecutar:

```bash
docker build -t ml-tiempo-modulos .
```

Una vez finalizada la construcción, verificar que la imagen se encuentre disponible mediante el siguiente comando:

```bash
docker images
```

**Resultado esperado**

La imagen Docker deberá construirse correctamente y quedar registrada en el repositorio local con el nombre `ml-tiempo-modulos`.

---

### Paso 4. Etiquetar la imagen Docker

Asignar una etiqueta compatible con Azure Container Registry.

```bash
docker tag ml-tiempo-modulos estimadoracr.azurecr.io/ml-tiempo-modulos:v1
```

Sustituir **estimadoracr** por el nombre del Azure Container Registry creado previamente.

---

### Paso 5. Autenticarse en Azure

Iniciar sesión mediante Azure CLI.

```bash
az login
```

Posteriormente autenticar el registro de contenedores.

```bash
az acr login --name estimadoracr
```

---

### Paso 6. Publicar la imagen

Enviar la imagen Docker hacia Azure Container Registry.

```bash
docker push estimadoracr.azurecr.io/ml-tiempo-modulos:v1
```

**Resultado esperado**

La imagen Docker deberá publicarse correctamente dentro del Azure Container Registry para que pueda ser utilizada durante la creación del servicio Azure Container Apps.

---

### Paso 7. Crear Azure Container Apps

Desde el Portal de Azure crear una nueva instancia de **Azure Container Apps**.

Durante la configuración seleccionar:

- Azure Container Registry creado previamente.
- Imagen Docker publicada.
- Puerto 8000.
- Configurar el Ingress como External, permitiendo el acceso público a la API.
- CPU y memoria.
- Escalado automático.

**Resultado esperado**

La aplicación deberá quedar configurada utilizando la imagen Docker publicada, exponiendo el puerto 8000 y permitiendo el acceso mediante una dirección pública.

---

### Paso 8. Obtener la URL pública

Una vez finalizado el despliegue, Azure asignará una dirección pública similar a:

```text
https://ml-tiempo-modulos.azurecontainerapps.io
```

**Resultado esperado**

Azure generará una URL pública que permitirá acceder a la aplicación desplegada desde cualquier navegador autorizado.


## 5. Estrategia de despliegue

La estrategia propuesta se basa en la contenerización de la aplicación mediante Docker y su publicación en un servicio **Platform as a Service (PaaS)**. Esta estrategia permite reutilizar la misma imagen Docker construida durante el desarrollo, simplificando el proceso de despliegue y garantizando un entorno de ejecución consistente entre desarrollo y producción.

---

## 6. Conclusiones

Este procedimiento permite desplegar la aplicación desarrollada con FastAPI mediante un contenedor Docker utilizando Azure Container Apps como plataforma PaaS. Aunque el alcance del proyecto contempló únicamente la validación local de la solución, la arquitectura desarrollada permite su implementación en un entorno de nube siguiendo los pasos descritos en este manual.
