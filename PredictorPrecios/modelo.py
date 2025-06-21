import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import warnings
import re
warnings.filterwarnings('ignore')

class PredictorPreciosInmuebles:
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.feature_names = []
        self.is_trained = False
        
    def limpiar_precio(self, precio_str):
        """
        Limpia y convierte valores de precio a numérico
        """
        if pd.isna(precio_str):
            return np.nan
        
        # Convertir a string si no lo es
        precio_str = str(precio_str)
        
        # Remover caracteres no numéricos excepto puntos y comas
        precio_limpio = re.sub(r'[^\d.,]', '', precio_str)
        
        # Manejar casos con múltiples puntos o comas
        if precio_limpio.count('.') > 1 or precio_limpio.count(',') > 1:
            # Tomar solo la primera parte numérica válida
            match = re.search(r'^\d+[.,]?\d*', precio_limpio)
            if match:
                precio_limpio = match.group()
        
        # Convertir punto/coma decimal
        if ',' in precio_limpio and '.' in precio_limpio:
            # Si hay ambos, asumir que el último es decimal
            if precio_limpio.rfind(',') > precio_limpio.rfind('.'):
                precio_limpio = precio_limpio.replace('.', '').replace(',', '.')
            else:
                precio_limpio = precio_limpio.replace(',', '')
        elif ',' in precio_limpio:
            # Si solo hay comas, la última es decimal si tiene 1-2 dígitos después
            partes = precio_limpio.split(',')
            if len(partes[-1]) <= 2:
                precio_limpio = precio_limpio.replace(',', '.')
            else:
                precio_limpio = precio_limpio.replace(',', '')
        
        try:
            return float(precio_limpio)
        except (ValueError, TypeError):
            return np.nan
    
    def limpiar_antiguedad(self, antiguedad_str):
        """
        Limpia y convierte valores de antigüedad a numérico
        """
        if pd.isna(antiguedad_str):
            return np.nan
        
        # Convertir a string si no lo es
        antiguedad_str = str(antiguedad_str).lower().strip()
        
        # Casos especiales
        if 'construcción' in antiguedad_str or 'construc' in antiguedad_str:
            return 0  # En construcción = 0 años
        
        if 'estrenar' in antiguedad_str or 'nuevo' in antiguedad_str:
            return 0  # A estrenar = 0 años
        
        # Extraer números de la string
        numeros = re.findall(r'\d+', antiguedad_str)
        
        if numeros:
            # Tomar el primer número encontrado
            return int(numeros[0])
        
        # Si no se puede procesar, devolver NaN
        return np.nan
    
    def preprocessar_datos(self, df):
        """
        Preprocesa los datos para el modelo
        """
        # Crear una copia para no modificar el original
        df_clean = df.copy()
        
        # Limpiar y convertir precio a numérico de forma más robusta
        if 'price' in df_clean.columns:
            df_clean['price'] = df_clean['price'].apply(self.limpiar_precio)
            # Filtrar valores inválidos
            df_clean = df_clean[df_clean['price'] > 0].copy()
        
        # Limpiar datos numéricos (excepto antiquity)
        numeric_cols = ['m2_total', 'm2_covered', 'room', 'bedroom', 'bathroom', 
                       'toilette', 'garage', 'expenses']
        
        for col in numeric_cols:
            if col in df_clean.columns:
                if col == 'expenses':
                    # Para expenses, limpiar de la misma manera que precio
                    df_clean[col] = df_clean[col].apply(self.limpiar_precio)
                else:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Limpiar antiguedad por separado
        if 'antiquity' in df_clean.columns:
            df_clean['antiquity'] = df_clean['antiquity'].apply(self.limpiar_antiguedad)
        
        # Llenar valores faltantes con valores más inteligentes
        df_clean['m2_total'] = df_clean['m2_total'].fillna(df_clean['m2_covered'])
        df_clean['m2_covered'] = df_clean['m2_covered'].fillna(df_clean['m2_total'])
        
        # Si ambos son NaN, usar valores promedio por barrio/tipo
        for col in ['m2_total', 'm2_covered']:
            mask = df_clean[col].isna()
            if mask.any():
                # Llenar con promedio por barrio y tipo
                df_clean[col] = df_clean.groupby(['barrio', 'type'])[col].transform(
                    lambda x: x.fillna(x.median())
                )
                # Si aún hay NaN, llenar con promedio general
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
        
        # Valores faltantes para otras columnas
        df_clean['toilette'] = df_clean['toilette'].fillna(0)
        df_clean['garage'] = df_clean['garage'].fillna(0)
        df_clean['expenses'] = df_clean['expenses'].fillna(0)
        
        # Para antiquity, llenar NaN con mediana (ahora que están limpios)
        if 'antiquity' in df_clean.columns:
            df_clean['antiquity'] = df_clean['antiquity'].fillna(df_clean['antiquity'].median())
            # Si la mediana también es NaN (todos los valores eran inválidos), usar 15 años como default
            if df_clean['antiquity'].isna().all():
                df_clean['antiquity'] = df_clean['antiquity'].fillna(15)
        
        # Para room, bedroom, bathroom usar valores lógicos
        # Si 'room' está vacío pero 'bedroom' tiene dato, imputar como bedroom + 1
        mask_room_na = df_clean['room'].isna() & df_clean['bedroom'].notna()
        df_clean.loc[mask_room_na, 'room'] = df_clean.loc[mask_room_na, 'bedroom'] + 1

        # Ahora, si todavía quedan NaN, imputar con 2 por defecto
        df_clean['room'] = df_clean['room'].fillna(2)

        df_clean['bedroom'] = df_clean['bedroom'].fillna(1)
        df_clean['bathroom'] = df_clean['bathroom'].fillna(1)
        
        # Variables categóricas
        categorical_cols = ['barrio', 'type', 'disposition', 'orientation']
        for col in categorical_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].fillna('No especificado')
        
        # Crear features adicionales
        if 'bathroom' in df_clean.columns and 'toilette' in df_clean.columns:
            df_clean['total_bathrooms'] = df_clean['bathroom'] + df_clean['toilette']
        
        if 'm2_total' in df_clean.columns and 'room' in df_clean.columns:
            df_clean['m2_per_room'] = df_clean['m2_total'] / (df_clean['room'] + 1)
        
        # Validaciones finales
        df_clean = df_clean[df_clean['m2_total'] > 0].copy()
        df_clean = df_clean[df_clean['room'] > 0].copy()
        
        return df_clean
    
    def preparar_features(self, df, is_training=True):
        """
        Prepara las features para el modelo
        """
        features = []
        
        # Features numéricas
        numeric_features = ['m2_total', 'm2_covered', 'room', 'bedroom', 'bathroom', 
                           'toilette', 'antiquity', 'garage', 'expenses', 'total_bathrooms', 'm2_per_room']
        
        for col in numeric_features:
            if col in df.columns:
                feature_data = df[col].fillna(0).astype(float)
                features.append(feature_data)
        
        # Features categóricas
        categorical_features = ['barrio', 'type', 'disposition', 'orientation']
        
        for col in categorical_features:
            if col in df.columns:
                if is_training:
                    # Crear y ajustar encoder durante entrenamiento
                    if col not in self.label_encoders:
                        self.label_encoders[col] = LabelEncoder()
                    # Agregar 'No especificado' a las clases si no existe
                    unique_vals = list(df[col].astype(str).unique())
                    if 'No especificado' not in unique_vals:
                        unique_vals.append('No especificado')
                    self.label_encoders[col].fit(unique_vals)
                    encoded = self.label_encoders[col].transform(df[col].astype(str))
                else:
                    # Usar encoder existente durante predicción
                    if col in self.label_encoders:
                        # Manejar categorías no vistas
                        unique_values = set(self.label_encoders[col].classes_)
                        df_col = df[col].astype(str)
                        df_col = df_col.apply(lambda x: x if x in unique_values else 'No especificado')
                        encoded = self.label_encoders[col].transform(df_col)
                    else:
                        encoded = np.zeros(len(df))
                features.append(encoded)
        
        # Convertir a matriz numpy
        if features:
            feature_matrix = np.column_stack(features)
        else:
            feature_matrix = np.array([]).reshape(len(df), 0)
        
        if is_training:
            self.feature_names = [col for col in numeric_features if col in df.columns] + \
                               [col for col in categorical_features if col in df.columns]
        
        return feature_matrix
    
    def entrenar(self, df):
        """
        Entrena el modelo Random Forest
        """
        print("Iniciando entrenamiento del modelo...")
        
        # Preprocesar datos
        df_clean = self.preprocessar_datos(df)
        print(f"Datos válidos después de limpieza: {len(df_clean)}")
        
        if len(df_clean) < 10:
            raise ValueError("No hay suficientes datos válidos para entrenar el modelo")
        
        # Preparar features y target
        X = self.preparar_features(df_clean, is_training=True)
        y = df_clean['price'].values
        
        print(f"Forma de features: {X.shape}")
        print(f"Cantidad de precios: {len(y)}")
        
        # División train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Configurar Random Forest con Grid Search más simple
        rf = RandomForestRegressor(random_state=42, n_jobs=-1)
        
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2]
        }
        
        print("Realizando búsqueda de hiperparámetros...")
        grid_search = GridSearchCV(
            estimator=rf,
            param_grid=param_grid,
            cv=3,
            scoring='neg_mean_absolute_error',
            n_jobs=-1
        )
        
        grid_search.fit(X_train, y_train)
        
        # Mejor modelo
        self.model = grid_search.best_estimator_
        
        # Evaluación
        y_pred = self.model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print(f"Mejor configuración: {grid_search.best_params_}")
        print(f"MAE: ${mae:,.2f}")
        print(f"RMSE: ${rmse:,.2f}")
        print(f"R²: {r2:.3f}")
        
        self.is_trained = True
        print("Entrenamiento completado!")
        
        # Importancia de features
        if hasattr(self.model, 'feature_importances_') and len(self.feature_names) > 0:
            feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("\nImportancia de variables:")
            print(feature_importance.head(10))
        
        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'best_params': grid_search.best_params_
        }
    
    def predecir(self, df):
        """
        Realiza predicciones
        """
        if not self.is_trained:
            raise ValueError("El modelo no ha sido entrenado. Ejecute entrenar() primero.")
        
        # Preprocesar datos
        df_clean = self.preprocessar_datos(df)
        
        # Preparar features
        X = self.preparar_features(df_clean, is_training=False)
        
        # Predecir
        predicciones = self.model.predict(X)
        
        return predicciones
    
    def predecir_simple(self, barrio, ambientes, **kwargs):
        """
        Predice precio solo con barrio y ambientes (modo simplificado)
        """
        # Obtener valores promedio del barrio para las features faltantes
        if hasattr(self, 'datos_entrenamiento'):
            # Preprocesar datos de entrenamiento primero para obtener estadísticas válidas
            df_entrenamiento_limpio = self.preprocessar_datos(self.datos_entrenamiento)
            df_barrio = df_entrenamiento_limpio[df_entrenamiento_limpio['barrio'] == barrio]
            
            if len(df_barrio) > 0:
                m2_promedio = df_barrio['m2_total'].median()
                m2_cubierto_promedio = df_barrio['m2_covered'].median()
                dormitorios_promedio = max(1, int(ambientes * 0.6))  # Estimación
                baños_promedio = max(1, int(ambientes * 0.3))  # Estimación
                antiguedad_promedio = df_barrio['antiquity'].median()
            else:
                # Valores por defecto si no hay datos del barrio
                m2_promedio = ambientes * 25  # Estimación: 25m2 por ambiente
                m2_cubierto_promedio = m2_promedio * 0.9
                dormitorios_promedio = max(1, ambientes - 1)
                baños_promedio = 1
                antiguedad_promedio = 20
        else:
            # Valores por defecto
            m2_promedio = ambientes * 25
            m2_cubierto_promedio = m2_promedio * 0.9
            dormitorios_promedio = max(1, ambientes - 1)
            baños_promedio = 1
            antiguedad_promedio = 20
        
        # Usar valores por defecto o los proporcionados
        data = {
            'barrio': barrio,
            'type': kwargs.get('type', 'Departamentos'),
            'disposition': kwargs.get('disposition', 'Frente'),
            'orientation': kwargs.get('orientation', 'No especificado'),
            'm2_total': kwargs.get('m2_total', m2_promedio),
            'm2_covered': kwargs.get('m2_covered', m2_cubierto_promedio),
            'room': ambientes,
            'bedroom': kwargs.get('bedroom', dormitorios_promedio),
            'bathroom': kwargs.get('bathroom', baños_promedio),
            'toilette': kwargs.get('toilette', 0),
            'antiquity': kwargs.get('antiquity', antiguedad_promedio),
            'garage': kwargs.get('garage', 0),
            'expenses': kwargs.get('expenses', 100),
        }
        
        df_single = pd.DataFrame([data])
        precio_pred = self.predecir(df_single)[0]
        
        return precio_pred
    
    def predecir_single(self, **kwargs):
        """
        Predice precio para una propiedad individual
        """
        # Crear DataFrame con los parámetros
        data = {
            'barrio': kwargs.get('barrio', 'No especificado'),
            'type': kwargs.get('type', 'Departamentos'),
            'disposition': kwargs.get('disposition', 'Frente'),
            'orientation': kwargs.get('orientation', 'No especificado'),
            'm2_total': kwargs.get('m2_total', 50),
            'm2_covered': kwargs.get('m2_covered', 45),
            'room': kwargs.get('room', 2),
            'bedroom': kwargs.get('bedroom', 1),
            'bathroom': kwargs.get('bathroom', 1),
            'toilette': kwargs.get('toilette', 0),
            'antiquity': kwargs.get('antiquity', 20),
            'garage': kwargs.get('garage', 0),
            'expenses': kwargs.get('expenses', 0),
        }
        
        df_single = pd.DataFrame([data])
        precio_pred = self.predecir(df_single)[0]
        
        return precio_pred
    
    def guardar_modelo(self, filepath='modelo_precios.pkl'):
        """
        Guarda el modelo entrenado
        """
        if not self.is_trained:
            raise ValueError("No hay modelo entrenado para guardar.")
        
        modelo_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained,
            'datos_entrenamiento': getattr(self, 'datos_entrenamiento', None)
        }
        
        joblib.dump(modelo_data, filepath)
        print(f"Modelo guardado en {filepath}")
    
    def cargar_modelo(self, filepath='modelo_precios.pkl'):
        """
        Carga un modelo previamente entrenado
        """
        modelo_data = joblib.load(filepath)
        
        self.model = modelo_data['model']
        self.label_encoders = modelo_data['label_encoders']
        self.feature_names = modelo_data['feature_names']
        self.is_trained = modelo_data['is_trained']
        self.datos_entrenamiento = modelo_data.get('datos_entrenamiento', None)
        
        print(f"Modelo cargado desde {filepath}")

# Ejemplo de uso
if __name__ == "__main__":
    # Cargar datos
    df = pd.read_csv('resultado_final.csv')
    
    # Crear y entrenar modelo
    predictor = PredictorPreciosInmuebles()
    
    # Guardar datos de entrenamiento para predicciones simplificadas
    predictor.datos_entrenamiento = df.copy()
    metricas = predictor.entrenar(df)
    
    # Guardar modelo
    predictor.guardar_modelo()
    
    # Ejemplo de predicción individual
    precio_estimado = predictor.predecir_single(
        barrio='Palermo',
        m2_total=80,
        room=3,
        bedroom=2,
        bathroom=1,
        antiquity=10
    )
    print(f"\nPrecio estimado completo: ${precio_estimado:,.2f}")
    
    # Ejemplo de predicción simple
    precio_simple = predictor.predecir_simple(
        barrio='Palermo',
        ambientes=3
    )
    print(f"Precio estimado simple: ${precio_simple:,.2f}")
    