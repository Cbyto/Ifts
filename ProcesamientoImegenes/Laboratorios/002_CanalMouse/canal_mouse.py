import py5

img = None


def setup():
    global img
    py5.size(800, 400)

    ruta = "img/photo.jpg"
    print(f"[SETUP] Intentando cargar la imagen desde: {ruta}")

    img = py5.load_image(ruta)
    print("[SETUP] Imagen cargada exitosamente.")
    print("-" * 40)

    img.resize(400, 400)

    print("[SETUP] Imagen redimensionada a 400x400 exitosamente.")
    print("-" * 40)


def draw():
    py5.background(35)
    # Imagen original en la mitad izquierda (sin modificar)
    py5.image(img, 0, 0)

    # Calcular el factor de ajuste según la posición X del mouse
    # remap convierte un valor de un rango a otro
    # Acá: de 0 a 800 píxeles de ancho → de 0 a 2.5 de factor multiplicador
    factor_rojo = py5.remap(py5.mouse_x, 0, py5.width, 0, 2.5)

    # Acceder a la matriz de píxeles del lienzo completo
    img.load_pixels()
    py5.load_pixels()
    for x in range(img.width):
        for y in range(img.height):
            # La imagen es un arreglo lineal. Para acceder al píxel (x, y):
            # índice = x + y * ancho
            indice_img = x + y * img.width
            pixel = img.pixels[indice_img]


            # Separar los canales
            r = py5.red(pixel)
            g = py5.green(pixel)
            b = py5.blue(pixel)

            # Modificar solo el canal rojo según el mouse
            r = r * factor_rojo
            # Limitar el valor para que no supere 255
            # Un valor mayor haría que py5 lo interprete incorrectamente
            if r > 255:
                r = 255
            # Calcular el índice del mismo píxel en el lienzo (desplazado 400px a la derecha)
            indice_canvas = (x + 400) + y * py5.width
            py5.pixels[indice_canvas] = py5.color(r, g, b)

    # Aplicar los cambios al lienzo
    py5.update_pixels()

    # ---------------------------------------------------------
    # PRINTS POR CONSOLA (LOGGING)
    # ---------------------------------------------------------
    if py5.frame_count % 2 == 0:            ## 60
        print(f"[DRAW - Frame {py5.frame_count}]")
        print(f"  -> Mouse X: {py5.mouse_x}px | Factor multiplicador rojo: {factor_rojo:.2f}")
        
        # Una pequeña ayuda visual en consola para entender el factor
        if factor_rojo == 0:
            print("  -> Efecto: Canal rojo anulado por completo (0%).")
        elif factor_rojo > 1:
            print("  -> Efecto: Canal rojo intensificado.")
        elif factor_rojo < 1:
            print("  -> Efecto: Canal rojo atenuado.")
        else:
            print("  -> Efecto: Canal rojo original (factor 1.0).")
        print("-" * 30)

py5.run_sketch()
