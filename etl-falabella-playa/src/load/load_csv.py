"""
Este módulo guarda el DataFrame procesado y enriquecido en un archivo, según la ruta especificada.

Recibe el DataFrame transformado y enriquecido con información de IA, junto con la ruta
donde se guardará el archivo. El módulo se encarga de escribir el DataFrame en el
formato y ubicación deseados.
"""
from src.utils.logger import logger

def load_data_csv(df, csv_path):
    """
    Carga un DataFrame a un archivo CSV.

    Args:
        df (pandas.DataFrame): DataFrame a cargar.
        csv_path (str): Ruta donde guardar el archivo CSV.
    """
    logger.info("Cargando datos a CSV: %s", csv_path)
    try:
        df.to_csv(csv_path, index=False)
        logger.info("Carga a CSV exitosa. Archivo guardado en: %s", csv_path)
    except Exception as e:
        logger.error("Error al cargar datos a CSV: %s", e)
        raise
