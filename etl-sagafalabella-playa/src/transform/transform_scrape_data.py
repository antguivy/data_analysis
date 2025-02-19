"""
Este módulo transforma los datos brutos obtenidos del scraping.
Realiza las siguientes operaciones:

1. Limpieza de datos:
   - Elimina columnas con más del 95% de valores nulos.
   - Completa los valores faltantes (imputación).
   - Transforma los tipos de datos de las columnas a los tipos adecuados.

2. Ingeniería de características:
   - Calcula un nuevo campo llamado 'price_diff_%' (diferencia de precio porcentual).

3. Manejo de duplicados:
   - Identifica y separa las filas duplicadas.

Los datos limpios y las filas duplicadas se guardan en el directorio 'data/transform/'.
"""
import pandas as pd
from src.utils.logger import logger  # Importa el logger desde utils

def clean_prices(df):
    """
    Limpia los datos de precios del DataFrame.
    Elimina las columnas 'cmr_price' y 'event_price', ya que no se utilizarán.
    Luego, completa los valores faltantes en la columna 'normal_price' utilizando los 
    valores correspondientes de la columna 'internet_price'. Además, convierte a
    valores numéricos las columnas de 'internet_price' y 'normal_price'. Por último,
    crea una nueva columna calculada 'price_diff_%'.

    Args:
        df (pandas.DataFrame): DataFrame que contiene los datos scrapeados.

    Returns:
        pandas.DataFrame: El DataFrame con las columnas eliminadas y los valores 
                         faltantes de 'normal_price' completados.
    """
    columns = ["cmr_price","event_price","normal_price","internet_price"]
    logger.info("Eliminando columnas %s y %s...", columns[0], columns[1])
    df = df.drop(columns=columns[:2], axis=1)

    logger.info("Completando valores faltantes de %s", columns[2])
    df['normal_price'] =df['normal_price'].fillna(df['internet_price'])

    logger.info("Convirtiendo a decimales los valores de %s y %s", columns[2], columns[3])
    df[['normal_price', 'internet_price']] = df[['normal_price', 'internet_price']]\
    .apply(lambda row: pd.Series({col: float(row[col].replace(',', ''))
                                  if isinstance(row[col], str)
                                  else row[col] for col in row.index}),
                                axis=1
           )
    logger.info("Agregando columna calculada 'price_diff_%'")
    df['price_diff_%'] = (df['normal_price'] - df['internet_price'])/df['normal_price'] *100
    return df

def handle_duplicates(df, transformed_path="data/transformed"):
    """
    Maneja los datos duplicados en el DataFrame.

    Identifica, separa y guarda los registros duplicados en un archivo CSV.
    Luego, elimina los duplicados del DataFrame original y guarda el DataFrame 
    limpio en otro archivo CSV.

    Args:
        df (pandas.DataFrame): El DataFrame con los datos.
        transformed_path (str, opcional): La ruta al directorio donde se guardarán 
                                    los archivos CSV. Por defecto, "data/transformed".

    Returns:
        pandas.DataFrame: El DataFrame sin duplicados.
    """
    df_duplicates = df[df.duplicated(keep=False)]
    df_cleaned = df.drop_duplicates(keep='first')

    df_duplicates.to_csv(f"{transformed_path}/duplicates/duplicated_products.csv", index=False)

    df_cleaned.to_csv(f"{transformed_path}/cleaning/deduplicated_products.csv", index=False)
    return df_cleaned

def transform_scrape_data(raw_file_path):
    """
    Aplica todas las transformaciones a los datos de scraping.

    Args:
        raw_file_path: Ruta de datos extraídos crudos.

    Returns:
        pandas.DataFrame: DataFrame con datos de ventas transformados.
    """
    logger.info("Iniciando transformaciones de datos scrapeados...")
    df = pd.read_csv(raw_file_path).copy()
    df_cleaning_prices = clean_prices(df)
    df_cleaned = handle_duplicates(df_cleaning_prices)
    logger.info("Transformaciones de datos escrapeados completado.")
    return df_cleaned
