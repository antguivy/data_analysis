# PROYECTO ETL PARA ANÁLISIS DE DESCRIPCIONES DE PRODUCTOS DE FALABELLA (TEMPORADA PLAYA)

Este proyecto implementa un proceso ETL (Extracción, Transformación y Carga) para analizar datos de productos de la sección de "Temporada Playa" del sitio web de Falabella, obtenidos mediante web scraping.
Se realizaron los siguientes análisis:

1. **Análisis de relación entre la descripción de un producto y su categoría:** Se utilizó la inteligencia artificial de Gemini, a través de la API `google-genai`, para evaluar la relación entre la descripción de un producto y su categoría asignada. Esto permitió identificar posibles errores en la categorización de productos.
[Análisis de Relación](data/output/analysis/products_family_analysis.md)


2. **Análisis de duplicación de productos:** Se identificaron y analizaron productos duplicados dentro del conjunto de datos, con el objetivo de determinar posibles causas de duplicación y evaluar su impacto en la calidad de los datos.
[Análisis de Duplicación](data/output/analysis/duplicated_products_family.md)

Si bien se exploraron superficialmente otros aspectos como el análisis descripciones redundantes o poco claras, reviews y ratings, incluyendo el cálculo de un rating ponderado basado en la metodología de IMDb, estos no se profundizaron ni se presentan resultados concretos en este documento.