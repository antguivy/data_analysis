"""
Este módulo enriquece los datos del producto con información adicional generada mediante IA de 
Google.

Crea tres nuevas columnas: 'relation_batch', 'clarity_flag_batch' y 'suggested_description_batch'.

- 'relation_batch': Indica si el nombre del producto y la familia a la que pertenece
                   concuerdan (Verdadero/Falso).

- 'clarity_flag_batch': Indica si la descripción del producto es clara y no redundante
                      (si/no).

- 'suggested_description_batch': Proporciona una descripción sugerida si la descripción
                                actual no es clara. Si la descripción es adecuada,
                                contendrá el texto 'Descripción adecuada'.
"""
import os
import time
import re
from dotenv import load_dotenv
from google import genai #type: ignore
from src.utils.logger import logger


load_dotenv()
API_KEY = os.getenv("API_GEMINI")

client = genai.Client(api_key=API_KEY)

def relation_check_batch(names, families):
    """
    Verifica si la familia se corresponde con la descripción del producto
    para una lista de productos.
    """
    try:
        prompt_batches = ""
        for i, name in enumerate(names):
            prompt_batches += f"""
            ¿La siguiente familia se corresponde con la descripción del producto?

            Producto: {name}
            Familia: {families[i]}

            Responde solo con "si" o "no".
            """

        chat = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt_batches
        )

        response_ia_batch = chat.text.strip().lower()
        individual_responses = response_ia_batch.strip().split('\n')
        results = []
        affirmative_responses = {"si", "sí"}

        for response in individual_responses:
            response = response.strip().lower()
            if response in affirmative_responses:
                results.append(True)
            elif response == "no":
                results.append(False)
            else:
                logger.warning("Respuesta inesperada de la IA para lote: %s", response)
                results.append(None)

        return results

    except Exception as e:
        logger.error("Error al obtener respuesta de la IA para lote: %s", e)  # Usa logger.error
        return [None] * len(names)


def analyze_description_batch(names):
    """
    Analiza descripciones de productos (contenidas en 'names') por lotes 
    para detectar falta de claridad o redundancia.
    """
    clarity_flags_batch = []
    suggestion_texts_batch = []
    try:
        prompt_batches = ""
        for i, name in enumerate(names, 1):
            prompt_batches += f"""
            Evalúa la siguiente descripción de producto para determinar si es poco clara o redundante, con el objetivo
            de que la descripción muestre el tipo de producto.

            Producto {i}:
            Descripción del Producto: {name}

            Instrucciones:
            1. Responde si la descripción es poco clara o redundante con "si" o "no".
            2. Si respondiste "si", sugiere un texto alternativo. Si respondiste "no", escribe "Descripción adecuada".

            Formato de respuesta:
            1. [si/no]
            2. [texto]
            """

        chat = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt_batches
        )

        response_ia_batch = chat.text
        matches = re.finditer(
            r'(?:\d+\.\s*\[([^\]]+)\]|\d+\.\s*(si|no))[^\n]*\n(?:\d+\.\s*\[([^\]]+)\]|\d+\.\s*([^\n]*))',
            response_ia_batch, re.IGNORECASE | re.MULTILINE)

        results = []
        for match in matches:
            answer = None
            suggestion = None

            for group in match.groups():
                if group and group.lower() in ['si', 'no']:
                    answer = group.lower()
                    break

            for group in match.groups():
                if group and group.lower() not in ['si', 'no']:
                    suggestion = group.strip()
                    break

            if answer and suggestion:
                results.append((answer, suggestion))

        while len(results) < len(names):
            logger.warning("Añadiendo respuesta por defecto para producto %s", len(results) + 1)
            results.append(("no", "Descripción adecuada"))

        for answer, suggestion in results[:len(names)]:
            clarity_flags_batch.append("si" if "si" in answer.lower() else "no")
            suggestion_texts_batch.append(suggestion)

        return clarity_flags_batch, suggestion_texts_batch

    except Exception as e:
        logger.error("Error en analyze_description_batch: %s", str(e))
        return [None] * len(names), [None] * len(names)


def enrichment_data_products(df):
    """
    Enriquece el dataframe con IA.

    Args:
        df (pandas.DataFrame): DataFrame a enriquecer.

    Returns:
        pandas.DataFrame: DataFrame enriquecido.
    """
    batch_size = 30
    df['relation_batch'] = None
    df['clarity_flag_batch'] = None
    df['suggested_description_batch'] = None

    total_batches = (len(df) + batch_size - 1) // batch_size

    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i + batch_size]
        names_batch = batch_df['name'].tolist()
        families_batch = batch_df['family'].tolist()

        batch_results = relation_check_batch(names_batch, families_batch)
        df.loc[batch_df.index, 'relation_batch'] = batch_results
        time.sleep(2)
        names_descriptions_batch = batch_df['name'].tolist()
        clarity_flags_batch, suggestion_texts_batch = (
            analyze_description_batch(names_descriptions_batch)
            )

        if len(clarity_flags_batch) == len(names_descriptions_batch):
            df.loc[batch_df.index, 'clarity_flag_batch'] = clarity_flags_batch
            df.loc[batch_df.index, 'suggested_description_batch'] = suggestion_texts_batch
            logger.info("Batch %s/%s procesado correctamente", i//batch_size + 1, total_batches)
        else:
            logger.error("ERROR: Discrepancia en las longitudes en batch %s", i//batch_size + 1)
            logger.error("Longitud de clarity_flags_batch: %s", len(clarity_flags_batch))
            logger.error("Longitud de names_descriptions_batch: %s", len(names_descriptions_batch))

        time.sleep(3)

    return df
