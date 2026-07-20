import logging
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
RUTA_LOG = LOGS_DIR / "api.log"

LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("estimador_api")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    manejador_archivo = logging.FileHandler(
        RUTA_LOG,
        encoding="utf-8"
    )
    manejador_archivo.setLevel(logging.INFO)
    manejador_archivo.setFormatter(formato)

    manejador_consola = logging.StreamHandler()
    manejador_consola.setLevel(logging.INFO)
    manejador_consola.setFormatter(formato)

    logger.addHandler(manejador_archivo)
    logger.addHandler(manejador_consola)