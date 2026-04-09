# Segmentación por color

## Objetivo

El objetivo fue segmentar regiones de interés en imágenes mediante color, probando primero sobre la imagen preprocesada de cámara oscura y luego sobre una imagen alternativa de flores.

## 1. Segmentación sobre la imagen preprocesada

En la imagen de cámara oscura se intentó segmentar la zona iluminada de la proyección, que presentaba tonos cálidos y claros.

### Observación inicial

Al analizar canales e histogramas, se observó que:

- la mayor parte de la imagen correspondía a un fondo muy oscuro,
- la región de interés tenía tonos cálidos,
- los canales rojo y verde daban la pista más útil.

### Primera estrategia en RGB

Se probaron rangos RGB para capturar tonos amarillos, beige y marrones claros.

### Ajuste entre estrategias

La segunda estrategia aumentó la exigencia sobre los canales rojo y verde para intentar reducir el fondo y aislar mejor la parte iluminada.

### Limitaciones encontradas

Este método tuvo algunas limitaciones:

- la proyección no tenía color uniforme,
- había zonas más claras y otras más oscuras,

## 2. Segmentación alternativa en imagen de flores

Como la imagen anterior no ofrecía una segmentación tan limpia, se trabajó también con una imagen de flores, donde el objetivo fue segmentar el color verde de los tallos.

### ¿Por qué esta imagen era mejor?

Porque presentaba:

- mejor iluminación,
- colores más diferenciados,
- mejor contraste entre tallos, pétalos y fondo.

## 3. Segmentación del verde

### Estrategia inicial en RGB

Se intentó segmentar los tallos verdes con rangos RGB.

### Problema encontrado

Aunque visualmente el verde se distinguía, la segmentación en RGB no recuperaba de forma limpia los tallos completos.

## 4. Prueba en HSV

Para mejorar la segmentación, se pasó a HSV.

### ¿Qué significa HSV?

- **H (Hue / tono):** indica qué color es.
- **S (Saturation / saturación):** indica qué tan puro o intenso es el color.
- **V (Value / brillo):** indica qué tan claro u oscuro se ve.

### ¿Por qué usar HSV?

Porque el tono verde se puede aislar mejor separándolo del brillo y de la intensidad, algo que en RGB resulta más difícil.

### Selección del rango

Se probaron píxeles del tallo y se observaron valores de H cercanos a tonos amarillo-verdosos y verdes. A partir de eso, se eligió un rango un poco más amplio para contemplar variaciones dentro del mismo tallo.

### ¿Por qué no usar exactamente los valores medidos?

Porque los píxeles del tallo no tienen un único valor fijo. Cambian según la sombra, el brillo, la textura y pequeñas variaciones del color. Por eso conviene definir un intervalo y no solo un valor puntual.

## Reflexión final

La segmentación por color fue útil como primera aproximación. En la imagen de cámara oscura permitió separar parcialmente la región iluminada, aunque con limitaciones. En la imagen de flores, la segmentación del verde resultó más clara, y el uso de HSV mostró ser una estrategia más adecuada que RGB para este tipo de tarea.
