# mi_script_playwright.py
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from loguru import logger
import pandas as pd
from fake_useragent import UserAgent
import os
import random
import time

# Configura logging
logger.add("scraper_playwright.log", rotation="500 MB")

# Plantilla de URL del portal a revisar. Se define por variable de entorno, por ejemplo:
#   TARGET_URL_TEMPLATE=https://portal.ejemplo.com/aplicar/{id}
TARGET_URL_TEMPLATE = os.getenv("TARGET_URL_TEMPLATE", "https://example.com/apply/{id}")

# Configura el rango de IDs a probar
start_id = 500
end_id = 699
base_delay = 2  # Segundos base de espera

# Inicializa Fake User Agent
ua = UserAgent()

results = []

with sync_playwright() as p:
    # Lanzar navegador headless
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent=ua.random)  # Rota User-Agent inicial
    
    for id_num in range(start_id, end_id + 1):
        # Rota User-Agent en cada iteración (crea nueva página)
        page = context.new_page()
        page.set_extra_http_headers({"User-Agent": ua.random})
        
        url = TARGET_URL_TEMPLATE.format(id=id_num)
        
        try:
            page.goto(url, wait_until="domcontentloaded")  # Espera a que el DOM cargue
            
            # Espera inteligente hasta que el body esté presente (equivalente a WebDriverWait)
            page.wait_for_selector("body", timeout=10000)  # Máx 10 seg
            
            page_source = page.content()
            
            # Parsear con BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            page_text = soup.get_text()
            
            if "Posición:" in page_text:
                try:
                    start = page_text.find("Posición:") + len("Posición:")
                    end = page_text.find("Descripción:", start)
                    if end == -1:
                        end = page_text.find("\n", start)
                    title = page_text[start:end].strip()
                    logger.info(f"{id_num}: Sí - {title if title else 'Título no extraído'}")
                    results.append({"ID": id_num, "Estado": "Sí", "Título": title if title else "No extraído"})
                except Exception as e:
                    logger.error(f"{id_num}: Sí (pero no se pudo extraer el título) - Error: {e}")
                    results.append({"ID": id_num, "Estado": "No", "Título": "No extraído"})
            else:
                logger.info(f"{id_num}: No")
                results.append({"ID": id_num, "Estado": "No", "Título": ""})
            
            # Delay random
            time.sleep(base_delay + random.uniform(1, 3))
            
            page.close()
        
        except Exception as e:
            logger.error(f"{id_num}: Error al cargar o procesar la página ({e})")
            results.append({"ID": id_num, "Estado": "Error", "Título": str(e)})
    
    browser.close()

# Exporta a Excel
if results:
    df = pd.DataFrame(results)
    df.to_excel("resultados_playwright.xlsx", index=False)
    logger.info("Resultados exportados a resultados_playwright.xlsx")
else:
    logger.warning("No hay resultados para exportar")