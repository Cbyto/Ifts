import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from modelo import PredictorPreciosInmuebles
import os

# Configuración de la página
st.set_page_config(
    page_title="Predictor de Precios Inmobiliarios",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1e3d59;
        text-align: center;
        margin-bottom: 2rem;
    }
    .price-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .simple-price-card {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .toggle-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def cargar_datos():
    """Carga los datos base"""
    try:
        df = pd.read_csv('resultado_final.csv')
        return df
    except FileNotFoundError:
        st.error("No se encontró el archivo de datos. Asegúrate de que 'muestra_datos_originales.csv' esté en el directorio.")
        return None

@st.cache_resource
def cargar_modelo():
    """Carga o entrena el modelo"""
    predictor = PredictorPreciosInmuebles()
    
    if os.path.exists('modelo_precios.pkl'):
        try:
            predictor.cargar_modelo()
            return predictor
        except:
            st.warning("Error al cargar modelo guardado. Entrenando nuevo modelo...")
    
    # Si no existe modelo guardado, entrenar uno nuevo
    df = cargar_datos()
    if df is not None:
        with st.spinner("Entrenando modelo... Esto puede tomar unos minutos."):
            predictor.entrenar(df)
            predictor.guardar_modelo()
        return predictor
    return None

def obtener_valores_promedio_barrio(df, barrio):
    """Obtiene valores promedio para un barrio específico"""
    df_barrio = df[df['barrio'] == barrio]
    
    if len(df_barrio) == 0:
        # Si no hay datos del barrio, usar promedios generales
        df_barrio = df

# Función auxiliar para obtener valores seguros
    def safe_int(series, default=0):
        """Convierte a entero de forma segura, manejando NaN"""
        try:
            value = series.median()
            if pd.isna(value):
                return default
            return int(value)
        except:
            return default
    
    def safe_mode(series, default_value):
        """Obtiene la moda de forma segura"""
        try:
            mode_values = series.mode()
            if len(mode_values) > 0:
                return mode_values.iloc[0]
            return default_value
        except:
            return default_value

    promedios = {
            'type': safe_mode(df_barrio['type'], 'Departamento'),
            'disposition': safe_mode(df_barrio['disposition'], 'Frente'),
            'orientation': safe_mode(df_barrio['orientation'], 'Norte'),
            'm2_total': safe_int(df_barrio['m2_total'], 80),
            'm2_covered': safe_int(df_barrio['m2_covered'], 70),
            'bedroom': safe_int(df_barrio['bedroom'], 2),
            'bathroom': safe_int(df_barrio['bathroom'], 1),
            'toilette': safe_int(df_barrio['toilette'], 0),
            'antiquity': safe_int(df_barrio['antiquity'], 20),          # Esta línea era la que fallaba
            'garage': safe_int(df_barrio['garage'], 0),
            'expenses': safe_int(df_barrio['expenses'], 100)
        }    
    return promedios

def crear_grafico_distribucion_precios(df, filtros_aplicados=None):
    """Crea gráfico de distribución de precios"""
    df_filtrado = df.copy()
    
    # Aplicar filtros si existen
    if filtros_aplicados is not None:
        for key, value in filtros_aplicados.items():
            if value and key in df.columns:
                if key == 'barrio':
                    df_filtrado = df_filtrado[df_filtrado[key] == value]
                elif key in ['room', 'bedroom', 'bathroom']:
                    df_filtrado = df_filtrado[df_filtrado[key] == value]
    
    # Limpiar datos de precio
    df_filtrado = df_filtrado.dropna(subset=['price'])
    df_filtrado = df_filtrado[df_filtrado['price'] > 0]
    
    if len(df_filtrado) == 0:
        # Crear gráfico vacío si no hay datos
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos para mostrar con los filtros aplicados",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title='Distribución de Precios',
            xaxis_title='Precio (USD)',
            yaxis_title='Cantidad',
            height=400
        )
        return fig
    
    fig = px.histogram(
        df_filtrado, 
        x='price', 
        nbins=30,
        title='Distribución de Precios',
        labels={'price': 'Precio (USD)', 'count': 'Cantidad'},
        color_discrete_sequence=['#667eea']
    )
    
    fig.update_layout(
        title_font_size=20,
        showlegend=False,
        height=400
    )
    
    return fig

def crear_grafico_precio_barrio(df):
    """Crea gráfico de precios promedio por barrio"""
    # Limpiar datos antes de agrupar
    df_clean = df.dropna(subset=['barrio', 'price'])
    df_clean = df_clean[df_clean['price'] > 0]
    
    if len(df_clean) == 0:
        # Crear gráfico vacío si no hay datos
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos suficientes para mostrar precios por barrio",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title='Precio Promedio por Barrio (Top 15)',
            xaxis_title='Barrio',
            yaxis_title='Precio Promedio (USD)',
            height=500
        )
        return fig
    
    precio_barrio = df_clean.groupby('barrio')['price'].agg(['mean', 'count']).reset_index()
    precio_barrio = precio_barrio[precio_barrio['count'] >= 2]  # Solo barrios con más de 1 propiedad
    precio_barrio = precio_barrio.sort_values('mean', ascending=False).head(15)
    
    if len(precio_barrio) == 0:
        # Si no hay barrios con suficientes propiedades
        fig = go.Figure()
        fig.add_annotation(
            text="No hay barrios con suficientes propiedades para mostrar",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title='Precio Promedio por Barrio (Top 15)',
            xaxis_title='Barrio',
            yaxis_title='Precio Promedio (USD)',
            height=500
        )
        return fig
    
    fig = px.bar(
        precio_barrio,
        x='barrio',
        y='mean',
        title='Precio Promedio por Barrio (Top 15)',
        labels={'mean': 'Precio Promedio (USD)', 'barrio': 'Barrio'},
        color='mean',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        title_font_size=20,
        height=500
    )
    
    return fig

def crear_grafico_precio_m2(df):
    """Crea gráfico de relación precio vs m2"""
    # Limpiar datos antes de crear el gráfico
    df_clean = df.copy()
    
    # Eliminar filas con valores NaN en las columnas críticas
    df_clean = df_clean.dropna(subset=['m2_total', 'price', 'room'])
    
    # Asegurar que room sea positivo (para el tamaño de los puntos)
    df_clean = df_clean[df_clean['room'] > 0]
    
    # Si después de limpiar no hay datos suficientes
    if len(df_clean) == 0:
        # Crear un gráfico vacío con mensaje
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos suficientes para mostrar el gráfico",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title='Relación Precio vs Metros Cuadrados',
            xaxis_title='M² Totales',
            yaxis_title='Precio (USD)',
            height=500
        )
        return fig
    
    fig = px.scatter(
        df_clean,
        x='m2_total',
        y='price',
        color='barrio',
        size='room',
        hover_data=['bedroom', 'bathroom', 'antiquity'],
        title='Relación Precio vs Metros Cuadrados',
        labels={'m2_total': 'M² Totales', 'price': 'Precio (USD)'}
    )
    
    fig.update_layout(
        title_font_size=20,
        height=500
    )
    
    return fig

def crear_grafico_comparativo(df, caracteristica, precio_predicho=None):
    """Crea gráfico comparativo de características"""
    if caracteristica not in df.columns:
        return None
    
    # Limpiar datos
    df_clean = df.dropna(subset=[caracteristica, 'price'])
    df_clean = df_clean[df_clean['price'] > 0]
    
    if len(df_clean) == 0:
        # Crear gráfico vacío si no hay datos
        fig = go.Figure()
        fig.add_annotation(
            text=f"No hay datos suficientes para mostrar {caracteristica}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title=f'Distribución de Precios por {caracteristica.title()}',
            xaxis_title=caracteristica.title(),
            yaxis_title='Precio (USD)',
            height=400
        )
        return fig
    
    fig = px.box(
        df_clean,
        x=caracteristica,
        y='price',
        title=f'Distribución de Precios por {caracteristica.title()}',
        labels={'price': 'Precio (USD)', caracteristica: caracteristica.title()}
    )
    
    if precio_predicho:
        fig.add_hline(
            y=precio_predicho,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Precio Predicho: ${precio_predicho:,.0f}"
        )
    
    fig.update_layout(
        title_font_size=20,
        height=400
    )
    
    return fig

def main():
    # Título principal
    st.markdown('<h1 class="main-header">🏠 Predictor de Precios Inmobiliarios</h1>', unsafe_allow_html=True)
    
    # Cargar datos y modelo
    df = cargar_datos()
    predictor = cargar_modelo()
    
    if df is None or predictor is None:
        st.error("Error al cargar datos o modelo. Por favor, verifica los archivos.")
        return
    
    # Toggle para modo simplificado
    # Puse un tooltip al pasar el mouse sobre el titulo y la descripcion.
    st.sidebar.markdown('''
    <div class="toggle-container">
        <span style="font-size: 1rem; color: #333;">
            <strong title="Selecciona el tipo de predicción que querés hacer">🎯 Modo de Predicción</strong><br>
            <span title="Usa promedios del barrio y simplifica los campos. Útil para estimaciones rápidas.">
                Elegí entre una predicción rápida usando valores promedio del barrio
                o una configuración completa con todos los parámetros.
            </span>
        </span>
    </div>
    ''', unsafe_allow_html=True)    

    modo_simplificado = st.sidebar.checkbox(
        "Activar Predicción Rápida", 
        value=False,
        help="Usa valores promedio del barrio para predecir rápidamente"
    )

    prop_nueva = st.sidebar.checkbox(
        "Propiedades a Estrenar", 
        value=False,
        help="Se consideran propiedades a estrenar",
        disabled=not modo_simplificado
    )

    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Obtener valores únicos para los selectores
    barrios_disponibles = sorted(df['barrio'].dropna().unique())
    tipos_disponibles = sorted(df['type'].dropna().unique())
    orientaciones_disponibles = sorted(df['orientation'].dropna().unique())
    disposiciones_disponibles = sorted(df['disposition'].dropna().unique())
    
    if modo_simplificado:
        # MODO SIMPLIFICADO
        st.sidebar.header("⚡ Predicción Rápida")
        st.sidebar.markdown("*Solo necesitas elegir barrio y ambientes*")
        
        barrio = st.sidebar.selectbox("📍 Barrio", barrios_disponibles, index=0)
        ambientes = st.sidebar.slider("🛋️ Ambientes", 1, 6, 3)
        
        # Obtener valores promedio para el barrio
        ### promedios = obtener_valores_promedio_barrio(df, barrio)
        df_filtrado = df.copy()
        if prop_nueva:
            df_filtrado = df_filtrado[(df_filtrado['antiquity'].fillna(0) == 0)]

        promedios = obtener_valores_promedio_barrio(df_filtrado, barrio)
        
        # Mostrar información sobre los valores utilizados
        with st.sidebar.expander("ℹ️ Valores utilizados automáticamente"):
            st.write(f"**Tipo:** {promedios['type']}")
            st.write(f"**M² Totales:** {promedios['m2_total']}")
            st.write(f"**M² Cubiertos:** {promedios['m2_covered']}")
            st.write(f"**Dormitorios:** {promedios['bedroom']}")
            st.write(f"**Baños:** {promedios['bathroom']}")
            st.write(f"**Antigüedad:** {promedios['antiquity']} años")
            st.write("*Basado en promedios del barrio seleccionado*")
        
        # Botón de predicción simplificada
        if st.sidebar.button("🚀 Predicción Rápida", type="primary"):
            try:
                precio_predicho = predictor.predecir_single(
                    barrio=barrio,
                    type=promedios['type'],
                    disposition=promedios['disposition'],
                    orientation=promedios['orientation'],
                    m2_total=promedios['m2_total'],
                    m2_covered=promedios['m2_covered'],
                    room=ambientes,
                    bedroom=promedios['bedroom'],
                    bathroom=promedios['bathroom'],
                    toilette=promedios['toilette'],
                    antiquity=promedios['antiquity'],
                    garage=promedios['garage'],
                    expenses=promedios['expenses']
                )
                
                # Mostrar resultado con estilo diferente
                st.markdown(f"""
                <div class="simple-price-card">
                    <h2>⚡ Predicción Rápida</h2>
                    <h1>${precio_predicho:,.0f} USD</h1>
                    <p><strong>{barrio} • {ambientes} ambientes</strong></p>
                    <p>Precio por m²: ${precio_predicho/promedios['m2_total']:,.0f} USD/m²</p>
                    <small>*Basado en características promedio del barrio*</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Métricas comparativas simplificadas
                col1, col2, col3 = st.columns(3)
                
                df_barrio = df[df['barrio'] == barrio]
                precio_promedio_barrio = df_barrio['price'].mean()
                precio_promedio_general = df['price'].mean()
                
                with col1:
                    st.metric(
                        "vs Promedio Barrio",
                        f"${precio_promedio_barrio:,.0f}",
                        f"{((precio_predicho - precio_promedio_barrio) / precio_promedio_barrio * 100):+.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "vs Promedio General",
                        f"${precio_promedio_general:,.0f}",
                        f"{((precio_predicho - precio_promedio_general) / precio_promedio_general * 100):+.1f}%"
                    )
                
                with col3:
                    propiedades_similares = len(df[
                        (df['barrio'] == barrio) & 
                        (df['room'] == ambientes)
                    ])
                    st.metric("Propiedades Similares", propiedades_similares)
                
                # Gráfico simplificado
                st.markdown("---")
                st.header("📊 Análisis Rápido")
                
                #### fig_dist = crear_grafico_distribucion_precios(df, {'barrio': barrio, 'room': ambientes})
                df_grafico = df_filtrado if prop_nueva else df
                fig_dist = crear_grafico_distribucion_precios(df_grafico, {'barrio': barrio, 'room': ambientes})


                fig_dist.add_vline(x=precio_predicho, line_dash="dash", line_color="red", 
                                 annotation_text="Tu Predicción")
                st.plotly_chart(fig_dist, use_container_width=True)
                
                # Sugerencia para predicción detallada
                st.info("💡 **Tip:** Desactiva 'Predicción Rápida' arriba para obtener una estimación más precisa con todos los parámetros.")
                
            except Exception as e:
                st.error(f"Error en la predicción: {str(e)}")
    
    else:
        # MODO COMPLETO (código original)
        st.sidebar.header("🔧 Configuración Detallada de la Propiedad")
        
        # Filtros en sidebar
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            barrio = st.selectbox("📍 Barrio", barrios_disponibles, index=0)
            tipo = st.selectbox("🏢 Tipo", tipos_disponibles, index=0)
            m2_total = st.slider("📏 M² Totales", 20, 300, 80)
            m2_covered = st.slider("🏠 M² Cubiertos", 20, 250, int(m2_total * 0.9))
        
        with col2:
            orientacion = st.selectbox("🧭 Orientación", orientaciones_disponibles, index=0)
            disposicion = st.selectbox("🚪 Disposición", disposiciones_disponibles, index=0)
            ambientes = st.slider("🛋️ Ambientes", 1, 6, 3)
            dormitorios = st.slider("🛏️ Dormitorios", 1, 5, 2)
        
        # Más filtros
        st.sidebar.markdown("---")
        col3, col4 = st.sidebar.columns(2)
        
        with col3:
            baños = st.slider("🚿 Baños", 1, 4, 1)
            toilettes = st.slider("🚽 Toilettes", 0, 2, 0)
        
        with col4:
            antiguedad = st.slider("📅 Antigüedad (años)", 0, 100, 20)
            cocheras = st.slider("🚗 Cocheras", 0, 3, 0)
        
        expensas = st.sidebar.slider("💰 Expensas (USD)", 0, 1000, 100)
        
        # Botón de predicción
        if st.sidebar.button("🔮 Predecir Precio", type="primary"):
            try:
                precio_predicho = predictor.predecir_single(
                    barrio=barrio,
                    type=tipo,
                    disposition=disposicion,
                    orientation=orientacion,
                    m2_total=m2_total,
                    m2_covered=m2_covered,
                    room=ambientes,
                    bedroom=dormitorios,
                    bathroom=baños,
                    toilette=toilettes,
                    antiquity=antiguedad,
                    garage=cocheras,
                    expenses=expensas
                )
                
                # Mostrar resultado
                st.markdown(f"""
                <div class="price-card">
                    <h2>💵 Precio Predicho</h2>
                    <h1>${precio_predicho:,.0f} USD</h1>
                    <p>Precio por m²: ${precio_predicho/m2_total:,.0f} USD/m²</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Métricas comparativas
                col1, col2, col3, col4 = st.columns(4)
                
                # Calcular estadísticas comparativas
                df_barrio = df[df['barrio'] == barrio]
                precio_promedio_barrio = df_barrio['price'].mean()
                precio_promedio_general = df['price'].mean()
                precio_por_m2_promedio = precio_promedio_barrio / df_barrio['m2_total'].mean()
                
                with col1:
                    st.metric(
                        "Precio Promedio Barrio",
                        f"${precio_promedio_barrio:,.0f}",
                        f"{((precio_predicho - precio_promedio_barrio) / precio_promedio_barrio * 100):+.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "Precio Promedio General",
                        f"${precio_promedio_general:,.0f}",
                        f"{((precio_predicho - precio_promedio_general) / precio_promedio_general * 100):+.1f}%"
                    )
                
                with col3:
                    st.metric(
                        "Precio/m² Barrio",
                        f"${precio_por_m2_promedio:,.0f}",
                        f"{((precio_predicho/m2_total - precio_por_m2_promedio) / precio_por_m2_promedio * 100):+.1f}%"
                    )
                
                with col4:
                    propiedades_similares = len(df[
                        (df['barrio'] == barrio) & 
                        (df['room'] == ambientes) & 
                        (df['bedroom'] == dormitorios)
                    ])
                    st.metric("Propiedades Similares", propiedades_similares)
                
                # Visualizaciones
                st.markdown("---")
                st.header("📊 Análisis del Mercado")
                
                # Gráficos en tabs
                tab1, tab2, tab3, tab4 = st.tabs(["📈 Distribución", "🏙️ Por Barrio", "📏 Precio vs M²", "🔍 Comparativo"])
                
                with tab1:
                    filtros = {'barrio': barrio, 'room': ambientes, 'bedroom': dormitorios}
                    fig_dist = crear_grafico_distribucion_precios(df, filtros)
                    fig_dist.add_vline(x=precio_predicho, line_dash="dash", line_color="red", 
                                     annotation_text="Predicción")
                    st.plotly_chart(fig_dist, use_container_width=True)
                
                with tab2:
                    fig_barrio = crear_grafico_precio_barrio(df)
                    st.plotly_chart(fig_barrio, use_container_width=True)
                
                with tab3:
                    fig_m2 = crear_grafico_precio_m2(df)
                    # Agregar punto de la predicción
                    fig_m2.add_scatter(
                        x=[m2_total],
                        y=[precio_predicho],
                        mode='markers',
                        marker=dict(size=15, color='red', symbol='star'),
                        name='Tu Predicción'
                    )
                    st.plotly_chart(fig_m2, use_container_width=True)
                
                with tab4:
                    col1, col2 = st.columns(2)
                    with col1:
                        fig_comp1 = crear_grafico_comparativo(df, 'room', precio_predicho)
                        if fig_comp1:
                            st.plotly_chart(fig_comp1, use_container_width=True)
                    
                    with col2:
                        fig_comp2 = crear_grafico_comparativo(df, 'antiquity', precio_predicho)
                        if fig_comp2:
                            st.plotly_chart(fig_comp2, use_container_width=True)
                
                # Análisis de propiedades similares
                st.markdown("---")
                st.header("🏠 Propiedades Similares en el Barrio")
                
                propiedades_similares = df[
                    (df['barrio'] == barrio) & 
                    (abs(df['room'] - ambientes) <= 1) &
                    (abs(df['m2_total'] - m2_total) <= 20)
                ].copy()
                
                if len(propiedades_similares) > 0:
                    propiedades_similares['diferencia_precio'] = abs(propiedades_similares['price'] - precio_predicho)
                    propiedades_similares = propiedades_similares.sort_values('diferencia_precio').head(5)
                    
                    st.dataframe(
                        propiedades_similares[[
                            'price', 'm2_total', 'room', 'bedroom', 'bathroom', 
                            'antiquity', 'disposition', 'orientation'
                        ]].round(0),
                        use_container_width=True
                    )
                else:
                    st.info("No se encontraron propiedades similares en este barrio.")
            
            except Exception as e:
                st.error(f"Error en la predicción: {str(e)}")

            
    # Información adicional
    with st.expander("ℹ️ Información sobre el Modelo"):
        st.markdown("""
        ### Modelo Random Forest
        - **Algoritmo**: Random Forest Regressor
        - **Variables utilizadas**: Barrio, tipo, m², ambientes, dormitorios, baños, antigüedad, etc.
        - **Entrenamiento**: Grid Search con validación cruzada
        
        ### Modos de Predicción
        - **Predicción Rápida**: Solo requiere barrio y ambientes. Usa valores promedio del barrio para el resto de características.
        - **Predicción Detallada**: Permite configurar todos los parámetros para mayor precisión.
        
        ### Métricas del Modelo
        El modelo ha sido entrenado y optimizado usando técnicas de machine learning avanzadas.
        
        ### Recomendaciones
        - Los precios predichos son estimaciones basadas en datos históricos
        - Considera factores adicionales como ubicación exacta, estado del inmueble, etc.
        - Usa esta herramienta como referencia inicial para tus decisiones
        """)

if __name__ == "__main__":
    main()