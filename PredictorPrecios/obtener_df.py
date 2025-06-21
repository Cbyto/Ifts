import sqlite3
import pandas as pd

def obtener_datos_zonaprop():
    """
    Se conecta a la base de datos, ejecuta la consulta principal,
    limpia y transforma los datos, y separa los registros de desarrollos.

    Returns:
        tuple: Una tupla conteniendo dos DataFrames:
               - df_principal (pd.DataFrame): El DataFrame limpio y listo para usar.
               - df_eliminados (pd.DataFrame): El DataFrame con los registros excluidos.
    """
    print("Conectando a zonaprop...")
    with sqlite3.connect("zonaprop_data.db") as conn:
        print("Consultando datos desde la tabla propiedades...")
        query = """
            SELECT 
                postingId AS posting_id,
                "priceOperationTypes[0].operationType.name" AS status,
                "priceOperationTypes[0].prices[0].formattedAmount" AS price,
                "priceOperationTypes[0].prices[0].currency" AS currency_price,
                "expenses.formattedAmount" AS expenses,
                "expenses.currency" AS currency_expenses,
                "mainFeatures.1000019.value" AS disposition,
                "mainFeatures.CFT100.value" AS m2_total,
                "mainFeatures.CFT101.value" AS m2_covered,
                "mainFeatures.CFT1.value" AS room,
                "mainFeatures.CFT2.value" AS bedroom,
                "mainFeatures.CFT3.value" AS bathroom,
                "mainFeatures.CFT4.value" AS toilette,
                "mainFeatures.CFT5.value" AS antiquity,
                "mainFeatures.CFT7.value" AS garage,
                "publisher.publisherId" AS publisher_id,
                "publisher.name" AS publisher_name,
                "realEstateType.name" AS type,
                "postingLocation.location.name" AS barrio,
                "mainFeatures.1000029.value" AS orientation,
                "postingLocation.postingGeolocation.geolocation.latitude" AS geo_latitude,
                "postingLocation.postingGeolocation.geolocation.longitude" AS geo_longitude,
                "visiblePictures.pictures[1].title" AS generateTitle
            FROM propiedades
        """
        df = pd.read_sql_query(query, conn)

    print(f"Cantidad de registros obtenidos: {len(df)}")

    # --- Separación de registros ---
    print("Separando registros con 'Desarrollo vertical' o 'Desarrollo horizontal'...")
    filtro_excluir = df['generateTitle'].str.contains("Desarrollo vertical|Desarrollo horizontal", case=False, na=False)
    df_principal = df[~filtro_excluir].copy()  # Registros que NO son desarrollos
    
    print(f"Registros para procesar: {len(df_principal)}")

    # --- Transformación de datos ---
    print("Transformando datos del DataFrame principal...")

    # Reemplazo de valores nulos
    df_principal['bedroom'] = df_principal['bedroom'].fillna(1)
    df_principal['toilette'] = df_principal['toilette'].fillna(0)
    df_principal['garage'] = df_principal['garage'].fillna(0)
    df_principal['disposition'] = df_principal['disposition'].fillna("Sin Especificar")
    df_principal['orientation'] = df_principal['orientation'].fillna("X")

    # --- Filtrado por 'status' (solo registros que digan 'Venta') ---
    print("Filtrando registros con 'status' igual a 'Venta'...")
    filtro_status = df_principal['status'].str.contains("venta", case=False, na=False)
    df_principal = df_principal[filtro_status]
    print(f"Registros después del filtro 'status': {len(df_principal)}")

    # --- Limpiar y convertir 'price' a numérico antes de filtrar ---
    print("Limpiando y convirtiendo la columna 'price' a numérico...")
    df_principal['price'] = pd.to_numeric(
        df_principal['price'].astype(str).str.replace(r'[^0-9]', '', regex=True),
        errors='coerce'
    )

    # --- Filtrado de 'price' (eliminar valores menores a 9000 o nulos) ---
    print("Filtrando registros con 'price' mayor o igual a 9000...")
    filtro_price = (df_principal['price'] >= 9000) & (df_principal['price'].notna())
    df_principal = df_principal[filtro_price]
    print(f"Registros después del filtro 'price': {len(df_principal)}")

    # --- Filtrado de 'type' (eliminar registros con valores de 'Desarrollo Verticales' y variaciones) ---
    print("Filtrando registros con 'type' no igual a 'Desarrollo Verticales'...")
    filtro_type = ~df_principal['type'].str.contains("Desarrollo Verticales|Desarrollo verticales|Desarrollos verticales", case=False, na=False)
    df_principal = df_principal[filtro_type]
    print(f"Registros después del filtro 'type': {len(df_principal)}")

    # --- Inferencia para la columna 'balcony' ---
    print("Inferiendo valores para la columna 'balcony'...")

    # Aseguramos que las columnas 'm2_total' y 'm2_covered' sean numéricas
    df_principal['m2_total'] = pd.to_numeric(df_principal['m2_total'], errors='coerce')
    df_principal['m2_covered'] = pd.to_numeric(df_principal['m2_covered'], errors='coerce')

    # Creación de la columna 'balcony' con la condición indicada
    df_principal['balcony'] = df_principal.apply(
        lambda row: "Sí" if abs(row['m2_total'] - row['m2_covered']) != 0 and 
                         ("departamento" in str(row['type']).lower()) else "No", axis=1
    )

    print("Proceso de transformación completado.")

    # --- Generar df_eliminados al final basado en posting_id ---
    ids_finales = df_principal['posting_id']
    df_eliminados = df[~df['posting_id'].isin(ids_finales)]

    print(f"Registros descartados (no pasaron algún filtro): {len(df_eliminados)}")

    # Retornamos ambos DataFrames
    return df_principal, df_eliminados


# --- Bloque de Ejecución Principal ---
if __name__ == '__main__':
    print("--- Ejecutando el script de datos de forma autónoma ---")
    
    # 1. Obtenemos los datos llamando a nuestra función
    df_final, df_descartados = obtener_datos_zonaprop()

    # 2. Guardamos los resultados
    print("\nGuardando resultado final en resultado_final.csv...")
    df_final.to_csv("resultado_final.csv", index=False)
    print(f"Registros guardados en resultado_final.csv: {len(df_final)}")

    print("\nGuardando registros eliminados en eliminados.csv...") 
    df_descartados.to_csv("eliminados.csv", index=False)
    print(f"Registros guardados en eliminados.csv: {len(df_descartados)}")
    
    print("\n--- Proceso finalizado ---")