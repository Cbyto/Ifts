# Preprocesamiento de imagen

## Objetivo

El objetivo fue mejorar una imagen obtenida con cámara oscura para que la región importante fuera más visible y quedara preparada para análisis posteriores.

## Problema inicial

La imagen original presentaba varios inconvenientes:

- muy baja iluminación general,
- exceso de fondo negro,
- poca visibilidad de la zona importante,
- contraste insuficiente,
- dificultad para distinguir claramente la proyección.

Por ese motivo, antes de segmentar fue necesario realizar una etapa de preprocesamiento.

## 1. Recorte de la región de interés

Primero se definió una **región de interés (ROI)** para eliminar gran parte del fondo negro y concentrar el análisis en la zona proyectada.

### ¿Por qué se recortó?

Se recortó porque gran parte de la imagen era fondo oscuro sin información útil. Al reducir esa zona, la proyección quedó más centrada y más fácil de analizar.

## 2. Pruebas de mejora de imagen

Sobre la imagen recortada se probaron distintas operaciones de preprocesamiento:

### a) Ajuste de brillo y contraste

### b) Mejora local de contraste con CLAHE

### c) Suavizado

## 3. Comparación de resultados

Luego se compararon visualmente las distintas versiones para decidir cuál funcionaba mejor.

La mejora que resultó más útil fue:

- primero ajustar **brillo y contraste**,
- luego aplicar **CLAHE**.

## Conclusión

El preprocesamiento permitió transformar una imagen inicialmente poco visible en una versión más clara y más apta para análisis posterior. El recorte ayudó a concentrarse en la región útil, y la combinación de brillo/contraste con CLAHE fue la estrategia que dio mejores resultados.
