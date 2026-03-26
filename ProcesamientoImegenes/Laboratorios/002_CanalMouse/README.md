# 🎛️ Mezclador de canales con el mouse

## 🧪 ¿Qué vamos a hacer?

Vamos a recorrer la **matriz de píxeles** de una imagen y modificar matemáticamente sus valores antes de mostrarla.

La posición horizontal del mouse va a controlar la intensidad del **canal rojo**:

* A la izquierda → el rojo se **suprime**
* A la derecha → el rojo se **amplifica**

Este ejercicio introduce el concepto de **filtro**: una operación matemática que transforma los valores de los píxeles de manera sistemática.

👉 Es la base de operaciones como:

* Corrección de color
* Ajuste de contraste
* Efectos visuales
* Visión por computadora

---

## 🎯 ¿Qué hace este programa?

* Carga una imagen y la muestra sin modificar (lado izquierdo).
* Recorre cada píxel manualmente.
* Modifica el canal rojo según la posición del mouse.
* Dibuja la imagen resultante en tiempo real (lado derecho).

---

## 🧠 Conceptos clave

### 📌 Acceso a píxeles

Una imagen es un **arreglo lineal** de píxeles:

```
indice = x + y * ancho
```

Esto permite recorrerla con dos bucles (`for x` y `for y`).

---

### 📌 Filtros

Un filtro es simplemente:

> Aplicar una operación matemática a cada píxel.

En este caso:

```
r = r * factor
```

---

### 📌 Remap (reescalado de valores)

```python
factor_rojo = py5.remap(py5.mouse_x, 0, py5.width, 0, 2.5)
```

Convierte la posición del mouse en un rango útil:

* Mouse en 0 → factor 0 (sin rojo)
* Mouse en 800 → factor 2.5 (rojo intensificado)

---

## 🔬 Para experimentar

### 1. 🚫 Suprimir el canal rojo por completo

Reemplazá:

```python
r = r * factor_rojo
```

por:

```python
r = 0
```

#### ✅ ¿Qué ocurre?

* La imagen muestra solo **verde + azul** (lo que forma tonos **cian**).
* Las zonas que eran originalmente **rojas**:

  * Pierden completamente su intensidad
  * Se ven **negras o muy oscuras**

👉 Porque el rojo era su componente principal y ahora vale 0.

---

### 2. 🔄 Intercambiar canales

Cambiá:

```python
py5.color(r, g, b)
```

por:

```python
py5.color(b, g, r)
```

#### ✅ ¿Qué ocurre?

* El canal rojo y azul se intercambian.
* Los colores cambian drásticamente:

  * El cielo azul → se vuelve **rojizo**
  * Zonas rojizas → se vuelven **azuladas**

#### 🧠 Interpretación

Esto demuestra algo clave:

> Los colores son datos numéricos.

Cambiar su posición produce una imagen "extraña", pero completamente válida desde el punto de vista matemático.

---

### 3. 🎚️ Controlar un canal distinto

En lugar de modificar el rojo (r), aplicamos el factor al canal verde:

```python
g = g * factor_rojo
```

#### ✅ ¿Qué ocurre?

* Ahora estás afectando el **canal verde**.
* La imagen cambia de forma diferente:

  * Aumenta o disminuye la presencia de tonos verdes.

---

### ➕ Extensión sugerida

Poder agregar un segundo control usando el eje vertical, la posición Y del mouse para controlar el azul

```python
factor_azul = py5.remap(py5.mouse_y, 0, py5.height, 0, 2.5)
b = b * factor_azul
```

#### 🎯 Resultado:

* Mouse en X → controla rojo
* Mouse en Y → controla azul
* Verde queda fijo (o también podrías controlarlo)

👉 Esto básicamente convierte el sketch en un **mezclador de color interactivo en tiempo real** donde cada posición del mouse define una combinación distinta de canales.

---

## ⚠️ Detalle importante

Después de modificar los valores:

```python
if r > 255:
    r = 255
```

Este recorte o clipping evita que el valor desborde el rango de 8 bits. Evitamos errores visuales, ya que los valores RGB deben estar entre **0 y 255**.

---

## 📌 Conclusión

Este ejercicio muestra un concepto fundamental:

👉 **Una imagen no es más que una matriz de números.**

Al modificar esos números:

* Cambiamos colores
* Generamos efectos
* Creamos nuevas imágenes

Es la base de:

* Edición digital
* Gráficos por computadora

---

## 📄 Licencia

Este proyecto es de uso educativo — materia Procesamiento de Imágenes Digitales.

