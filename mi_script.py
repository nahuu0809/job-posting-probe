# mi_script.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from loguru import logger
import pandas as pd
from fake_useragent import UserAgent
import os
import random
import time

# Configura logging (salida a consola y archivo)
logger.add("scraper.log", rotation="500 MB")  # Guarda logs en un archivo

# Plantilla de URL del portal a revisar. Se define por variable de entorno, por ejemplo:
#   TARGET_URL_TEMPLATE=https://portal.ejemplo.com/aplicar/{id}
TARGET_URL_TEMPLATE = os.getenv("TARGET_URL_TEMPLATE", "https://example.com/apply/{id}")

# Configura el rango de IDs a probar (ajusta según necesites)
start_id = 700  # Ejemplo: empieza en 700
end_id = 750    # Ejemplo: termina en 750
base_delay = 2  # Segundos base de espera entre requests (se añade random para variabilidad)

# Inicializa Fake User Agent
ua = UserAgent()

# Configura Selenium (headless para no abrir ventana)
options = Options()
options.add_argument("--headless")  # Ejecuta sin interfaz gráfica
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Inicializa el driver
driver = webdriver.Chrome(options=options)

results = []  # Lista para recopilar resultados y exportar a Excel

for id_num in range(start_id, end_id + 1):
    # Rota User-Agent en cada iteración
    options.add_argument(f"user-agent={ua.random}")
    
    url = TARGET_URL_TEMPLATE.format(id=id_num)
    
    try:
        driver.get(url)
        
        # Espera inteligente hasta que el body cargue (máx 10 seg)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        page_source = driver.page_source
        
        # Usa BeautifulSoup para parsear
        soup = BeautifulSoup(page_source, 'html.parser')
        page_text = soup.get_text()  # Extrae todo el texto visible
        
        if "Posición:" in page_text:
            try:
                # Extrae el nombre de la posición
                start = page_text.find("Posición:") + len("Posición:")
                end = page_text.find("Descripción:", start)
                if end == -1:
                    end = page_text.find("\n", start)
                title = page_text[start:end].strip()
                logger.info(f"{id_num}: Sí - {title if title else 'Título no extraído'}")
                results.append({"ID": id_num, "Estado": "Sí", "Título": title if title else "No extraído"})
            except Exception as e:
                logger.error(f"{id_num}: Sí (pero no se pudo extraer el título) - Error: {e}")
                results.append({"ID": id_num, "Estado": "Sí", "Título": "No extraído"})
        else:
            logger.info(f"{id_num}: No")
            results.append({"ID": id_num, "Estado": "No", "Título": ""})
        
        # Delay random entre requests para evitar bloqueos
        time.sleep(base_delay + random.uniform(1, 3))
    
    except Exception as e:
        logger.error(f"{id_num}: Error al cargar o procesar la página ({e})")
        results.append({"ID": id_num, "Estado": "Error", "Título": str(e)})

# Cierra el driver al final
driver.quit()

# Exporta a Excel usando Pandas
if results:
    df = pd.DataFrame(results)
    df.to_excel("resultados.xlsx", index=False)
    logger.info("Resultados exportados a resultados.xlsx")
else:
    logger.warning("No hay resultados para exportar")