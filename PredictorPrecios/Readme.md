# Predictor de Precios para la venta de departamentos en CABA

## Scraper de ZonaProp
Es un fork de Sotrosca. El mismo va a sufrir modificaciones que creo necesarias:
1. Refactorizar las constantes.
2. Posibilidad de guardar los datos en un DB. En este caso sera SQLITE, pero a medida que escale puede ser algo mas robusto.
3. Agregar la psibilidad de descargar hasta X pagina, sin necesidad de descargar todas las páginas existentes.
4. Scrapear parciales. Desde tal página hasta tal otra. Guardando esa información.
5. Ante un problema en la descarga, guardar los datos descargados hasta ese momento.
6. Loging en un archivo.

## Datos y entrenamiento
Partiendo de los datos scrapeados y guardados en la DB, tomamos los datos que nos interesan y los guardamos en un csv, para
un posterior entrenamiento. Ojo porque tambien esta abierta la posibilidad de tomar directamente el df en cuestion.

## Interfaz 
Interfaz de usuario creada con streamlit.
