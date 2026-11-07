# Job Posting Probe

Scripts en Python que recorren un rango de identificadores numéricos en el portal de postulación de una empresa y registran cuáles corresponden a una búsqueda activa, con su título. Sirve para detectar posiciones que no aparecen en el listado principal.

## Cómo funciona

1. Arma la URL de cada ID a partir de una plantilla (`TARGET_URL_TEMPLATE`, con `{id}` como marcador).
2. Abre la página, espera a que cargue y busca el texto `Posición:` en el contenido. Si está, extrae el título hasta `Descripción:`.
3. Espera una pausa aleatoria entre pedidos para no sobrecargar el sitio.
4. Al terminar, exporta los resultados (ID, estado y título) a un Excel.

Hay dos versiones del mismo script:

| Script | Navegador | Salida |
| --- | --- | --- |
| `mi_script.py` | Selenium + Chrome | `resultados.xlsx` |
| `mi_script_playwright.py` | Playwright + Chromium | `resultados_playwright.xlsx` |

## Uso

```bash
pip install -r requirements.txt
playwright install chromium

# la plantilla apunta al portal que quieras revisar
export TARGET_URL_TEMPLATE="https://portal.ejemplo.com/aplicar/{id}"
python mi_script_playwright.py
```

En PowerShell: `$env:TARGET_URL_TEMPLATE = "https://portal.ejemplo.com/aplicar/{id}"`.

El rango de IDs (`start_id`, `end_id`) y la pausa base (`base_delay`) se cambian al comienzo de cada script.

Con Docker, el `Dockerfile` instala Chrome, Chromedriver y Chromium de Playwright y copia los dos scripts.

## Uso responsable

- Revisá los términos de uso del portal y mantené rangos chicos y pausas largas.
- El texto buscado (`Posición:`, `Descripción:`) depende del portal original. Para otro sitio hay que adaptarlo.

## Notas

- Los resultados (`*.xlsx`) y los logs no se suben al repositorio.
- Proyecto de práctica de scraping. El script de Selenium es el más viejo y el de Playwright es el que conviene usar.

## Créditos

Bibliotecas de código abierto que usa (no están incluidas):
[Selenium](https://www.selenium.dev), [Playwright](https://playwright.dev/python/), [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/), [pandas](https://pandas.pydata.org), [Loguru](https://github.com/Delgan/loguru) y [fake-useragent](https://github.com/fake-useragent/fake-useragent).

## Licencia

Código bajo [licencia MIT](LICENSE). © 2026 Nahuel Emiliano Diaz.
