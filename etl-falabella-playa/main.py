"""
Este módulo contiene el pipeline ETL para procesar datos de ventas.
"""
from src.extract.scraper_falabella import main as scraper_sf
from src.transform.transform_scrape_data import transform_scrape_data
from src.load.load_csv import load_data_csv
from src.enrichment_ia.enrichment_data import enrichment_data_products
from src.utils.logger import logger
def ejecutar_pipeline_etl():
    """
    Ejecuta el pipeline ETL completo: Extracción, Transformación y Carga.
    """
    logger.info("Iniciando pipeline ETL...")

    try:
        # 1. Extracción
        logger.info("Fase de Extracción...")
        raw_file_path = scraper_sf()
        if raw_file_path:
            # 2. Transformación
            logger.info("Fase de Transformación...")
            transform_data = transform_scrape_data(raw_file_path)
            # 3. Enriquecimiento con IA
            logger.info("Enriquecimiento de datos con IA...")
            df_enrichment = enrichment_data_products(transform_data)
            # # 4. Carga
            logger.info("Fase de Carga...")
            csv_output_path = "data/transformed/enrichment/enrichment_products.csv"
            load_data_csv(df_enrichment, csv_output_path)
            logger.info("Pipeline ETL completado con éxito. Guardados en: %s", csv_output_path)
        else:
            logger.info("Error: El archivo falló al generarse. Revisa el scraper.")
    except FileNotFoundError:
        logger.error("Archivo no encontrado.")
    except IOError:
        logger.error("Error de entrada/salida.")
    except Exception as e:
        logger.critical("Error inesperado en el pipeline ETL: %s - %s", type(e).__name__, e)
        logger.exception(e)

if __name__ == '__main__':
    ejecutar_pipeline_etl()
    