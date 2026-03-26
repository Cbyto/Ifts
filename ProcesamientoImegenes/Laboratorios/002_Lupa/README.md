# 🧪 La lupa en píxeles

Vamos a construir un **inspector visual**: al mover el mouse sobre la imagen, el programa va a leer el color exacto del píxel que está bajo el cursor, mostrarlo ampliado en un cuadrado a la derecha y desplegar sus valores RGB en pantalla.

El concepto clave es que cada coordenada `(x, y)` de la imagen corresponde a un píxel que almacena tres números: **Rojo (R), Verde (G) y Azul (B)**.
Ese es el fundamento de toda operación de **procesamiento digital de imágenes**.

---

## 🎯 ¿Qué hace este programa?

* Carga una imagen.
* Detecta la posición del mouse sobre la imagen.
* Lee el color del píxel en esa posición.
* Muestra:

  * El color ampliado (como una "lupa").
  * Los valores numéricos RGB.
* Evita errores limitando el mouse al área de la imagen.

---

## 🧠 Conceptos importantes

* **Píxel:** unidad mínima de una imagen digital.
* **RGB:** modelo de color basado en tres canales:

  * Rojo (Red)
  * Verde (Green)
  * Azul (Blue)
* Cada canal tiene valores entre **0 y 255**.

---

## 🔬 Experimentos

### 1. 🎨 Color negativo

Reemplazá esta línea:

```python
py5.fill(color_pixel)
```

por:

```python
py5.fill(255 - r, 255 - g, 255 - b)
```

Esto genera el **color complementario**.

#### ✅ Respuestas:

* Sobre un **rojo puro (255, 0, 0)** → aparece **cian (0, 255, 255)**.
* Sobre el **blanco (255, 255, 255)** → aparece **negro (0, 0, 0)**.

👉 Esto ocurre porque estás invirtiendo cada canal respecto a 255.

---

### 2. 🔴 Aislamiento de canal

Usá:

```python
py5.fill(r, 0, 0)
```

Esto elimina verde y azul, dejando solo el canal rojo.

#### ✅ Observación:

* En zonas **verdes o azules**, el valor de `r` suele ser bajo → el color se ve oscuro o negro.
* Esto demuestra que los colores "puros" no contienen contribución significativa de otros canales.

👉 Aprendizaje clave:
Los colores en una imagen suelen ser combinaciones, no valores aislados.

---

### 3. ⚠️ Sin protección (errores)

Comentá:

```python
mx = py5.constrain(py5.mouse_x, 0, 399)
my = py5.constrain(py5.mouse_y, 0, 399)
```

y reemplazalo por:

```python
mx = py5.mouse_x
my = py5.mouse_y
```

Luego mové el mouse fuera de la imagen.

#### ❗ ¿Qué pasa?

Aparece un error en la terminal, típicamente algo como:

```
IndexError: image index out of range
```

o similar.

#### ✅ Tipo de error:

* Es un **error de índice fuera de rango** (*IndexError*).
* Ocurre porque estás intentando acceder a un píxel que **no existe dentro de la imagen**.

#### 🧠 Conclusión:

Siempre hay que validar o limitar coordenadas cuando trabajamos con arrays o imágenes.

---

## 📌 Conclusión

Este ejercicio introduce una idea fundamental:
👉 **Las imágenes son datos.**

Cada píxel contiene información numérica que podemos leer, modificar y visualizar.
Esto es la base de áreas como:

* Visión por computadora
* Edición de imágenes

---

## 📄 Licencia

Este proyecto es de uso educativo — materia Procesamiento de Imágenes Digitales.

