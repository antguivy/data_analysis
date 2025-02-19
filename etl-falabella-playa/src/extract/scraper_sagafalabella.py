"""
Este módulo contiene un scraper para el sitio web de Saga Falabella, específicamente diseñado
para extraer información de productos para la temporada "lo mejor de la playa".

Utiliza Selenium para recopilar primero las URLs de los productos, las calificaciones y el 
número de reseñas del contenido dinámico de JavaScript de la página de la temporada de verano. 
Luego, utiliza requests y Beautiful Soup para extraer información detallada del producto de cada
página de producto individual. Los datos extraídos incluyen el nombre del producto, código, marca, 
categoría, subcategoría, familia del producto, URL de la imagen, precio CMR, precio de evento, 
precio de internet, precio normal, vendedor, junto con la URL, el número de reseñas y la 
calificación recopilados previamente.

Este scraper está destinado únicamente a fines de investigación y análisis de datos. Debe usarse
de manera responsable y ética, respetando los términos de servicio y la política de privacidad de 
Saga Falabella. Evite sobrecargar sus servidores con solicitudes excesivas. Este scraper implementa 
técnicas para minimizar la carga en los servidores de Saga Falabella, incluida la rotación de 
User-Agents e la introducción de retrasos entre las solicitudes.

Limitaciones:

Los cambios en la estructura del sitio web pueden dañar el scraper. Podrían ser necesarias 
actualizaciones y mantenimiento regulares.
El rendimiento del scraper depende de la capacidad de respuesta del sitio web y de su conexión 
de red.
Respete el archivo robots.txt y los términos de servicio de Saga Falabella. Utilice este scraper
de manera responsable. Evite realizar solicitudes excesivas que puedan ser perjudiciales para sus
servidores.
Autor:
Anthony Villazana
Fecha:
13/02/2025
"""

import time
import random
import os
from typing import TypedDict, List, Optional
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
from bs4 import BeautifulSoup, Tag
import pandas as pd
from src.utils.logger import logger

BASE_URL = "https://www.falabella.com.pe/falabella-pe/collection/lo-mejor-de-playa"
PAGES_TO_SCRAPE = 12
RAW_DATA_FOLDER = "data/raw"
PRODUCTS_LIST_FILE = os.path.join(RAW_DATA_FOLDER, "products_list.csv")
USER_AGENTS_FILE = os.path.join("src", "utils", "user_agents.txt")
LOG_FILE = "scraper.log"
WAIT_TIMEOUT = 10
DELAY_BETWEEN_REQUESTS = 2


class ProductsList(TypedDict):
    """Dictionary structure for storing product information"""

    url: list[str]
    rating: list[float]
    reviews: list[int]


class ProductDetail(TypedDict):
    """Dictionary structure for storing product details"""

    name: Optional[str]
    product_code: Optional[str]
    brand: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    family: Optional[str]
    reviews: Optional[int]
    rating: Optional[float]
    url_image: Optional[str]
    cmr_price: Optional[str]
    event_price: Optional[str]
    internet_price: Optional[str]
    normal_price: Optional[str]
    seller: Optional[str]
    url_product: Optional[str]


def load_user_agents(file_path: str) -> List[str]:
    """Carga la lista de user-agents desde un archivo."""
    try:
        with open(file_path, encoding="utf-8") as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        logger.error("User-Agents file not finded: %s", file_path)
        return []


USER_AGENTS = load_user_agents(USER_AGENTS_FILE)


def setup_selenium_driver() -> webdriver.Edge:
    """Configura y retorna el WebDriver (Edge)."""
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")
    return webdriver.Edge(options=options)


def get_product_links_from_page(driver: webdriver.Edge, url: str) -> ProductsList:
    """
    Args:
        driver: Selenium Driver.
        url: Url a escrapear.
    Return:
        products_lis: Lista de productos con url, rating y reviews.
    """
    products_list: ProductsList = {"url": [], "rating": [], "reviews": []}
    try:
        driver.get(url)
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "testId-searchResults-products"))
        )

        product_containers = driver.find_elements(
            By.XPATH, '//a[@data-pod="catalyst-pod"]'
        )
        logger.info("%s productos encontrados", len(product_containers))
        for container in product_containers:
            # URL del producto
            link = container.get_attribute('href')
            products_list['url'].append(link if link else "")

            # Rating
            try:
                rating = container.find_element(
                    By.XPATH, './/div[contains(@class, "jsx-1982392636 ratings")]'
                    ).get_attribute('data-rating')
                products_list['rating'].append(float(rating) if rating else 0)
            except NoSuchElementException:
                logger.debug("No se encontró el elemento rating para el producto.")
                products_list['rating'].append(0)

            # Reseñas
            try:
                reviews = container.find_element(
                    By.XPATH, './/span[contains(@class, "reviewCount")]'
                    ).get_attribute('data-rating')
                products_list['reviews'].append(int(reviews) if reviews else 0)
            except NoSuchElementException:
                logger.debug("No se encontró el elemento reviews para el producto.")
                products_list['reviews'].append(0)
        logger.info("%s productos procesados", len(product_containers))

    except TimeoutException:
        logger.warning("Timeout al cargar página")
    except WebDriverException as e_webdriver:
        logger.error("Error de WebDriver %s en página %s", e_webdriver, url)
    except Exception as e_general:
        logger.error("Error inesperado: %s", e_general)

    return products_list


def scrape_product_links(base_url: str, pages: int) -> ProductsList:
    """
    Scrapea los links de productos de múltiples páginas de categoría.

    Args:
        base_url: URL base de la categoría.
        pages: Número de páginas a scrapear.

    Returns:
        ProductsList: Diccionario con listas de URLs, ratings y reviews
        combinadas de todas las páginas.
    """
    all_products: ProductsList = {"url": [], "rating": [], "reviews": []}
    driver = setup_selenium_driver()
    try:
        for page in range(1, pages + 1):
            current_url = f"{base_url}?page={page}"
            logger.info("Scrapeando página: %s", current_url)
            page_products = get_product_links_from_page(driver, current_url)
            all_products["url"].extend(page_products["url"])
            all_products["rating"].extend(page_products["rating"])
            all_products["reviews"].extend(page_products["reviews"])
            time.sleep(DELAY_BETWEEN_REQUESTS)  # Delay entre páginas
    finally:
        driver.quit()
    return all_products


def get_product_detail(product_url: str) -> Optional[ProductDetail]:
    """
    Extrae los detalles de un producto desde su página individual.
    Función refactorizada para incluir toda la lógica de extracción.

    Args:
        product_url: URL de la página del producto.

    Returns:
        Optional[ProductDetail]: Diccionario con los detalles del producto o None en caso de error.
    """
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    logger.info("Scrapeando detalles del producto: %s", product_url)
    product_data: ProductDetail = {
        "name": None,
        "product_code": None,
        "brand": None,
        "category": None,
        "subcategory": None,
        "family": None,
        "reviews": None,
        "rating": None,
        "url_image": None,
        "cmr_price": None,
        "event_price": None,
        "internet_price": None,
        "normal_price": None,
        "seller": None,
        "url_product": product_url,
    }

    try:
        response = requests.get(
            product_url, headers=headers, timeout=15
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # 1. Get product name
        name_element = soup.find(
            "h1", class_="jsx-783883818 product-name fa--product-name false"
        )
        product_data["name"] = name_element.text if name_element else None

        # 2. Get product code
        product_code_element = soup.find("span", class_="jsx-3410277752")
        product_data["product_code"] = (
            product_code_element.text.split(":")[1].strip()
            if product_code_element and ":" in product_code_element.text
            else None
        )

        # 3. Get brand
        brand_element = soup.find("a", id="pdp-product-brand-link")
        product_data["brand"] = brand_element.text if brand_element else None

        # 4. Get category, subcategory and family
        breadcrumb = soup.find("ol", class_="Breadcrumbs-module_breadcrumb__3lLwJ")
        if breadcrumb and isinstance(breadcrumb, Tag):
            breadcrumb_elements = [
                element.text.strip() for element in breadcrumb.find_all("a")
            ]
            if len(breadcrumb_elements) >= 3:
                if len(breadcrumb_elements[1].split("-")) >= 2:
                    product_data["category"] = (
                        breadcrumb_elements[1].split("-")[0].strip()
                    )
                    product_data["subcategory"] = (
                        breadcrumb_elements[1].split("-")[1].strip()
                    )
                product_data["family"] = breadcrumb_elements[2].strip()

        # 5. Get url_image
        url_image_element = soup.find("img", class_="jsx-2487856160")
        product_data["url_image"] = (
            url_image_element.get("src") if url_image_element else None  # type: ignore
        )

        # 6. Get prices (cmr, event, internet, normal)
        cmr_price_element = soup.find("li", attrs={"data-cmr-price": True})
        event_price_element = soup.find("li", attrs={"data-event-price": True})
        internet_price_element = soup.find("li", attrs={"data-internet-price": True})
        normal_price_element = soup.find("li", attrs={"data-normal-price": True})

        def get_price(element, price_type):
            return element.get(f"data-{price_type}-price") if element else None  # type: ignore

        product_data["cmr_price"] = get_price(cmr_price_element, "cmr")
        product_data["event_price"] = get_price(event_price_element, "event")
        product_data["internet_price"] = get_price(internet_price_element, "internet")
        product_data["normal_price"] = get_price(normal_price_element, "normal")
        # 7. Get seller
        seller_element = soup.find("a", id="testId-SellerInfo-sellerName")
        product_data["seller"] = (
            seller_element.find("span").text if seller_element else None  # type: ignore
        )

        logger.info("Producto scrapeado con éxito: %s", product_url)
        time.sleep(DELAY_BETWEEN_REQUESTS)  # Delay entre productos
        return product_data

    except requests.exceptions.RequestException as e:
        logger.error("Error al acceder a %s: %s", product_url, e)
        return None
    except (
        AttributeError
    ) as e:
        logger.error("Error al parsear %s: %s", product_url, e)
        return None
    except Exception as e:
        logger.error("Error inesperado en %s: %s", product_url, e)
        return None


def main():
    """Función principal para ejecutar el scraper."""
    logger.info("Iniciando el scraper de Falabella - Lo Mejor de Playa")

    # 1. Scrapear lista de productos (URLs, ratings, reviews)
    logger.info("Obteniendo lista de productos...")
    product_list_data = scrape_product_links(BASE_URL, PAGES_TO_SCRAPE)
    if product_list_data["url"]:
        pd.DataFrame(product_list_data).to_csv(PRODUCTS_LIST_FILE, index=False)
        logger.info("Lista de productos guardada en: %s", PRODUCTS_LIST_FILE)
    else:
        logger.warning("No se encontraron URLs de productos. Revise el scraper de lista.")
        return

    # 2. Scrapear detalles de cada producto
    logger.info("Obteniendo detalles de los productos...")
    products_df = pd.read_csv(PRODUCTS_LIST_FILE)
    all_product_details: List[ProductDetail] = []

    for _, row in products_df.iterrows():
        product_info = {
            "url": row["url"],
            "rating": row["rating"],
            "reviews": row["reviews"],
        }
        product_detail = get_product_detail(product_info["url"])
        if product_detail:
            product_detail["rating"] = product_info["rating"]
            product_detail["reviews"] = product_info["reviews"]
            all_product_details.append(product_detail)
        else:
            logger.warning("Error al obtener detalles del producto: %s", product_info['url'])

    # 3. Guardar todos los detalles en un DataFrame y CSV
    if all_product_details:
        details_df = pd.DataFrame(all_product_details)
        output_file = os.path.join(RAW_DATA_FOLDER, "products_details.csv")
        details_df.to_csv(output_file, index=False)
        logger.info("Detalles de productos guardados en: %s", output_file)
        logger.info("Scraper finalizado exitosamente.")
        return output_file

    logger.warning("No se obtuvieron detalles de productos. Revise el scraper de detalles.")
    logger.warning("Scraper finalizado con advertencias.")
    return None


if __name__ == "__main__":
    file_path = main()
