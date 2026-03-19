import py5

'''
Con la librería py5 realizar una pizarra tipo el "Paint" de Windows.
'''

# ─── Configuración general 
CANVAS_W, CANVAS_H = 800, 600
TOOLBAR_H = 70                  # altura de la barra superior
DRAW_Y = TOOLBAR_H              # lo que este por debajo de esta Y es el área de dibujo

# ─── Estado de la aplicación
# Diccionario que guarda la herramienta activa, color, modo de relleno
# y las coordenadas necesarias para saber dónde empezó y dónde va el trazo.
state = {
    "tool": "lapiz",            # lapiz | cuadrado | circulo | elipse | goma
    "color": (0, 0, 0),         # color activo (R, G, B)
    "fill_mode": "contorno",    # contorno | relleno
    "brush_size": 4,            # grosor del lápiz en píxeles
    "eraser_size": 20,          # tamaño del cuadrado borrador en píxeles
    "drawing": False,           # True mientras el botón del mouse está presionado
    "start_x": 0,               # coordenada X donde se presionó el mouse (origen de la figura)
    "start_y": 0,               # coordenada Y donde se presionó el mouse
    "prev_x": 0,                # posición anterior del mouse (se necesita para trazar líneas continuas)
    "prev_y": 0,
    "show_help": False,
}

# Paleta de colores disponibles
PALETTE = [
    (0,   0,   0),    # negro
    (255, 255, 255),  # blanco
    (200,  30,  30),  # rojo
    (220, 120,   0),  # naranja
    (220, 200,   0),  # amarillo
    (30,  160,  30),  # verde
    (0,   100, 210),  # azul
    (130,  0,  200),  # violeta
    (200,   0, 150),  # rosa
    (100, 200, 220),  # celeste
    (139,  90,  43),  # marrón
    (160, 160, 160),  # gris
]

# Definición de botones de herramientas
# Cada herramienta tiene un id interno y una posición X fija en la toolbar
TOOLS = [
    {"id": "lapiz",    "label": "Lapiz",    "x": 10},
    {"id": "goma",     "label": "Goma",     "x": 80},
    {"id": "cuadrado", "label": "Cuadrado", "x": 150},
    {"id": "circulo",  "label": "Circulo",  "x": 240},
    {"id": "elipse",   "label": "Elipse",   "x": 330},
]

# Botones relleno / contorno
FILL_BUTTONS = [
    {"id": "contorno", "label": "Contorno", "x": 430},
    {"id": "relleno",  "label": "Relleno",  "x": 520},
]

# Gráficos off-screen para conservar lo dibujado
canvas_pg = None            # buffer off-screen (PGraphics): guarda de forma permanente

# Coordenadas de la X del overlay (constantes para reutilizar en el hit-test)
HELP_X      = 60            # borde izquierdo del panel de ayuda
HELP_Y      = 80            # borde superior del panel de ayuda
CLOSE_X     = 520           # borde izquierdo del botón X
CLOSE_Y     = 85            # borde superior del botón X
CLOSE_SIZE  = 22            # ancho y alto del botón X


# ─── Setup 
def setup():
    global canvas_pg
    py5.size(CANVAS_W, CANVAS_H)
    py5.window_title("Pizarra Paint - py5")
    # Creamos el buffer con el alto descontando la toolbar
    canvas_pg = py5.create_graphics(CANVAS_W, CANVAS_H - DRAW_Y)
    canvas_pg.begin_draw()
    canvas_pg.background(255)       # fondo blanco inicial
    canvas_pg.end_draw()


# ─── Draw
def draw():
    py5.background(230)
    draw_toolbar()

    # Volcamos el buffer persistente sobre la ventana (en la zona de dibujo)
    py5.image(canvas_pg, 0, DRAW_Y)

    # Mientras el usuario arrastra para crear una figura, mostramos
    # un preview "fantasma" en tiempo real (no se graba en canvas_pg todavía)
    if state["drawing"] and state["tool"] in ("cuadrado", "circulo", "elipse"):
        draw_preview()

    if state["show_help"]:
        draw_help_overlay()


# ─── Toolbar
def draw_toolbar():
    # Fondo de barra
    py5.no_stroke()
    py5.fill(50, 50, 60)
    py5.rect(0, 0, CANVAS_W, TOOLBAR_H)

    # Dibuja cada botón de herramienta; el activo resaltado en azul
    for btn in TOOLS:
        active = state["tool"] == btn["id"]
        draw_button(btn["x"], 8, 65, 26, btn["label"], active)

    # Botones relleno/contorno (solo activos para figuras sin sentido para lápiz o goma)
    fig_active = state["tool"] in ("cuadrado", "circulo", "elipse")
    for btn in FILL_BUTTONS:
        active = fig_active and state["fill_mode"] == btn["id"]
        draw_button(btn["x"], 8, 82, 26, btn["label"], active, dim=not fig_active)

    # Dibuja los cuadraditos de color de la paleta en una grilla de 6 columnas
    px = 620
    for i, col in enumerate(PALETTE):
        cx = px + (i % 6) * 24   # columna
        cy = 8 + (i // 6) * 24   # fila
        py5.stroke(180)
        py5.stroke_weight(1)
        # Resalta con borde amarillo el color actualmente seleccionado
        if col == state["color"]:
            py5.stroke(255, 230, 0)
            py5.stroke_weight(2)
        py5.fill(*col)
        py5.rect(cx, cy, 20, 20, 2)

    # Cuadrado grande al final que muestra el color activo
    py5.no_stroke()
    py5.fill(*state["color"])
    py5.rect(CANVAS_W - 34, 8, 26, 26, 3)
    py5.stroke(180)
    py5.stroke_weight(1)
    py5.no_fill()
    py5.rect(CANVAS_W - 34, 8, 26, 26, 3)

    # Línea separadora
    py5.stroke(80, 80, 100)
    py5.stroke_weight(1)
    py5.line(0, TOOLBAR_H, CANVAS_W, TOOLBAR_H)

    # Botón Ayuda — debajo de Lápiz y Goma, del mismo ancho combinado
    draw_button_green(10, 38, 135, 26, "? Ayuda")


def draw_button(x, y, w, h, label, active, dim=False):
    # Cambia el color del botón según su estado: activo, atenuado o normal
    py5.stroke_weight(1)
    if active:
        py5.fill(90, 160, 255)
        py5.stroke(150, 200, 255)
    elif dim:
        py5.fill(60, 60, 70)
        py5.stroke(90, 90, 100)
    else:
        py5.fill(75, 80, 95)
        py5.stroke(110, 115, 130)
    py5.rect(x, y, w, h, 4)         # el 4 es el radio de las esquinas redondeadas

    py5.no_stroke()
    if active:
        py5.fill(255)
    elif dim:
        py5.fill(100, 100, 110)
    else:
        py5.fill(210)
    py5.text_size(11)
    py5.text_align(py5.CENTER, py5.CENTER)
    py5.text(label, x + w / 2, y + h / 2)


def draw_button_green(x, y, w, h, label):
    py5.stroke_weight(1)
    py5.fill(40, 140, 70)       # verde oscuro de fondo
    py5.stroke(80, 200, 110)    # borde verde claro
    py5.rect(x, y, w, h, 4)

    py5.no_stroke()
    py5.fill(220, 255, 220)     # texto verde muy claro
    py5.text_size(11)
    py5.text_align(py5.CENTER, py5.CENTER)
    py5.text(label, x + w / 2, y + h / 2)


# ─── Preview de figura 
def draw_preview():
    mx, my = py5.mouse_x, py5.mouse_y
    sx, sy = state["start_x"], state["start_y"]
    r, g, b = state["color"]

    py5.push_style()
    if state["fill_mode"] == "relleno":
        py5.fill(r, g, b, 160)          # alpha 160: semi-transparente para el preview
    else:
        py5.no_fill()
    py5.stroke(r, g, b)
    py5.stroke_weight(2)

    if state["tool"] == "cuadrado":
        py5.rect(sx, sy, mx - sx, my - sy)
    elif state["tool"] == "circulo":
        # Forzamos que ancho == alto tomando el menor de los dos desplazamientos
        d = min(abs(mx - sx), abs(my - sy))
        sign_x = 1 if mx >= sx else -1
        sign_y = 1 if my >= sy else -1
        # ellipse() toma el CENTRO y los diámetros (no la esquina como los dema's)
        py5.ellipse(sx + sign_x * d / 2, sy + sign_y * d / 2, d, d)
    elif state["tool"] == "elipse":
        # Centro = punto medio entre origen y posición actual del mouse
        py5.ellipse(sx + (mx - sx) / 2, sy + (my - sy) / 2,
                    abs(mx - sx), abs(my - sy))
    py5.pop_style()


# ─── Overlay de ayuda
def draw_help_overlay():
    # push_style / pop_style para que los estilos del overlay no afecten al resto
    py5.push_style()

    # Fondo semi-transparente oscuro
    py5.no_stroke()
    py5.fill(20, 20, 20, 210)
    py5.rect(HELP_X, HELP_Y, 500, 320, 10)

    # ── Botón X para cerrar (se dibuja primero para que quede debajo del título) ──
    py5.fill(180, 50, 50)
    py5.rect(CLOSE_X, CLOSE_Y, CLOSE_SIZE, CLOSE_SIZE, 4)
    py5.fill(255)
    py5.text_size(13)
    py5.text_align(py5.CENTER, py5.CENTER)
    py5.text("X", CLOSE_X + CLOSE_SIZE / 2, CLOSE_Y + CLOSE_SIZE / 2)

    # ── Título ──
    py5.fill(255)
    py5.text_size(15)
    py5.text_align(py5.LEFT, py5.TOP)           # alineación izquierda para título y contenido
    py5.text("Ayuda — Pizarra Paint", HELP_X + 20, HELP_Y + 15)

    # Línea separadora
    py5.stroke(150)
    py5.stroke_weight(1)
    py5.line(HELP_X + 20, HELP_Y + 38, HELP_X + 480, HELP_Y + 38)

    # ── Contenido ──
    # text_align LEFT evita que el texto quede corrido
    py5.no_stroke()
    py5.fill(220)
    py5.text_size(12)
    py5.text_align(py5.LEFT, py5.TOP)
    ayuda = [
        "Lapiz        — Dibuja libremente arrastrando el mouse",
        "Goma         — Borra lo que pases por encima",
        "Cuadrado     — Click y arrastra para definir el tamaño",
        "Circulo      — Igual que cuadrado, proporciones 1:1",
        "Elipse       — Click y arrastra en cualquier proporcion",
        "",
        "Contorno / Relleno — Solo activos al usar una figura",
        "Paleta       — Click en cualquier color para seleccionar",
        "",
        "Scroll       — Cambia el grosor del lapiz o la goma",
        "Tecla C      — Limpia el canvas completo",
        "",
        "[ Click en '? Ayuda' o en la X para cerrar ]",
    ]
    for i, linea in enumerate(ayuda):
        py5.text(linea, HELP_X + 20, HELP_Y + 50 + i * 20)

    py5.pop_style()


# ─── Eventos del mouse
def mouse_pressed():
    mx, my = py5.mouse_x, py5.mouse_y

    # Si la ayuda está abierta, solo procesamos el cierre (X o botón Ayuda)
    # y bloqueamos cualquier otra acción
    if state["show_help"]:
        # Click en la X roja
        if CLOSE_X <= mx <= CLOSE_X + CLOSE_SIZE and CLOSE_Y <= my <= CLOSE_Y + CLOSE_SIZE:
            state["show_help"] = False
        # Click en el botón Ayuda (toggle)
        elif my < TOOLBAR_H and 10 <= mx <= 145 and 38 <= my <= 64:
            state["show_help"] = False
        return                      # bloqueamos el dibujo mientras la ayuda está abierta

    # Click en toolbar → cambiar herramienta o color
    if my < TOOLBAR_H:
        handle_toolbar_click(mx, my)
        return

    # Click en área de dibujo
    state["drawing"] = True
    state["start_x"] = mx
    state["start_y"] = my
    state["prev_x"] = mx
    state["prev_y"] = my

    # Para lápiz y goma, el primer click ya debe dejar marca
    if state["tool"] in ("lapiz", "goma"):
        paint_point(mx, my - DRAW_Y)   


def mouse_dragged():
    if not state["drawing"]:
        return
    mx, my = py5.mouse_x, py5.mouse_y
    if my < DRAW_Y:                     # evita dibujar encima de la toolbar al arrastrar
        return

    if state["tool"] == "lapiz":
        # Conectamos la posición anterior con la actual para trazar una línea suave
        # sin esto aparecerían puntos sueltos al mover el mouse rápido
        paint_line(state["prev_x"], state["prev_y"] - DRAW_Y,
                   mx, my - DRAW_Y)
        state["prev_x"], state["prev_y"] = mx, my

    elif state["tool"] == "goma":
        erase_point(mx, my - DRAW_Y)
        state["prev_x"], state["prev_y"] = mx, my


def mouse_released():
    if not state["drawing"]:
        return
    mx, my = py5.mouse_x, py5.mouse_y
    state["drawing"] = False

    if my < DRAW_Y:
        return

    tool = state["tool"]
    # Convertimos coordenadas de ventana a coordenadas del buffer (sin toolbar)
    sx, sy = state["start_x"], state["start_y"] - DRAW_Y
    ex, ey = mx, my - DRAW_Y

    # Al soltar el mouse grabamos la figura definitiva en el buffer persistente
    if tool == "cuadrado":
        commit_rect(sx, sy, ex - sx, ey - sy)
    elif tool == "circulo":
        d = min(abs(ex - sx), abs(ey - sy))
        sign_x = 1 if ex >= sx else -1
        sign_y = 1 if ey >= sy else -1
        commit_ellipse(sx + sign_x * d / 2, sy + sign_y * d / 2, d, d)
    elif tool == "elipse":
        commit_ellipse(sx + (ex - sx) / 2, sy + (ey - sy) / 2,
                       abs(ex - sx), abs(ey - sy))


# ─── Helpers de dibujo sobre canvas_pg
def paint_point(x, y):
    r, g, b = state["color"]
    canvas_pg.begin_draw()
    canvas_pg.stroke(r, g, b)
    canvas_pg.stroke_weight(state["brush_size"])
    canvas_pg.point(x, y)
    canvas_pg.end_draw()


def paint_line(x1, y1, x2, y2):
    # Dibuja un segmento entre el frame anterior y el actual del mouse
    r, g, b = state["color"]
    canvas_pg.begin_draw()
    canvas_pg.stroke(r, g, b)
    canvas_pg.stroke_weight(state["brush_size"])
    canvas_pg.line(x1, y1, x2, y2)
    canvas_pg.end_draw()


def erase_point(x, y):
    # "Borrar" es pintar un rectángulo blanco sobre el buffer
    sz = state["eraser_size"]
    canvas_pg.begin_draw()
    canvas_pg.no_stroke()
    canvas_pg.fill(255)
    canvas_pg.rect(x - sz / 2, y - sz / 2, sz, sz)
    canvas_pg.end_draw()


def commit_rect(x, y, w, h):
    r, g, b = state["color"]
    canvas_pg.begin_draw()
    canvas_pg.stroke(r, g, b)
    canvas_pg.stroke_weight(2)
    if state["fill_mode"] == "relleno":
        canvas_pg.fill(r, g, b)
    else:
        canvas_pg.no_fill()
    canvas_pg.rect(x, y, w, h)
    canvas_pg.end_draw()


def commit_ellipse(cx, cy, w, h):
    r, g, b = state["color"]
    canvas_pg.begin_draw()
    canvas_pg.stroke(r, g, b)
    canvas_pg.stroke_weight(2)
    if state["fill_mode"] == "relleno":
        canvas_pg.fill(r, g, b)
    else:
        canvas_pg.no_fill()
    canvas_pg.ellipse(cx, cy, w, h)
    canvas_pg.end_draw()


# ─── Manejo de clicks en toolbar
def handle_toolbar_click(mx, my):
    # Comprueba si el click cayó dentro del área de algún botón (hit-test manual)
    for btn in TOOLS:
        if btn["x"] <= mx <= btn["x"] + 65 and 8 <= my <= 34:
            state["tool"] = btn["id"]
            return

    # Relleno / Contorno
    for btn in FILL_BUTTONS:
        if btn["x"] <= mx <= btn["x"] + 82 and 8 <= my <= 34:
            state["fill_mode"] = btn["id"]
            return

    # Mismo hit-test para cada cuadradito de color de la paleta
    px = 620
    for i, col in enumerate(PALETTE):
        cx = px + (i % 6) * 24
        cy = 8 + (i // 6) * 24
        if cx <= mx <= cx + 20 and cy <= my <= cy + 20:
            state["color"] = col
            return

    # Botón Ayuda — toggle: abre y cierra
    if 10 <= mx <= 145 and 38 <= my <= 64:
        state["show_help"] = not state["show_help"]


# ─── Scroll → cambiar tamaño de pincel
def mouse_wheel(event):
    # get_count() > 0 significa scroll hacia abajo (achica), < 0 hacia arriba (agranda)
    delta = -1 if event.get_count() > 0 else 1
    if state["tool"] == "goma":
        state["eraser_size"] = max(5, min(80, state["eraser_size"] + delta * 3))
    elif state["tool"] == "lapiz":
        state["brush_size"] = max(1, min(30, state["brush_size"] + delta))


# ─── Teclado: C limpia el canvas
def key_pressed():
    if py5.key == 'c' or py5.key == 'C':
        # Limpiar = repintar el buffer entero de blanco
        canvas_pg.begin_draw()
        canvas_pg.background(255)
        canvas_pg.end_draw()


py5.run_sketch()