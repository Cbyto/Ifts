# Predictor de Precios para la venta de departamentos en CABA

## Scraper de ZonaProp
Es un fork de Sotrosca. El mismo va a sufrir modificaciones que creo necesarias:
1. Refactorizar las constantes.
2. Posibilidad de guardar los datos en un DB. En este caso sera SQLITE, pero a medida que escale puede ser algo mas robusto.
3. Agregar la psibilidad de descargar hasta X pagina, sin necesidad de descargar todas las páginas existentes.
4. Scrapear parciales. Desde tal página hasta tal otra. Guardando esa información.
5. Ante un problema en la descarga, guardar los datos descargados hasta ese momento.
6. Loging en un archivo.

## Creación del archivo visualizaciones.py
Creación de las visualizaciones 

## Creacion de un archivo app.py 
Interfaz de usuario
