"""
Este módulo configura y proporciona un logger para el proyecto ETL.
Permite registrar mensajes informativos, de advertencia y de error en la consola y en un archivo.
"""
import logging
import sys
import os

# Asegurar que el directorio logs exista
LOGS_DIR = 'logs'
os.makedirs(LOGS_DIR, exist_ok=True) # Crea el directorio si no existe

logger = logging.getLogger(__name__)
# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,  # Nivel mínimo de registro (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s', # Formato del log
    handlers=[
        logging.StreamHandler(sys.stdout), # Imprime logs a la consola
        logging.FileHandler(os.path.join(LOGS_DIR, 'proyecto_etl.log')) # Guarda logs en un archivo
    ]
)
