import streamlit as st
import pandas as pd
import sqlite3 # Usamos sqlite3 para el ejemplo local, puedes cambiar a mysql-connector
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Eco-Farmaco Dashboard", layout="wide")
st.title("🧪 Vigilancia Epidemiológica Ambiental")
st.markdown("Análisis de medicamentos como contaminantes hídricos (Ref: UNAL)")

# Conexión a la base de datos (Ejemplo con SQLite)
conn = sqlite3.connect('epidemiologia.db')

# Cargar datos para el Dashboard
query = """
SELECT 
    p.nombre_rio, m.nombre_comun, r.concentracion_hallada, m.pnec_ngl,
    (r.concentracion_hallada / m.pnec_ngl) as riesgo
FROM Resultados_Laboratorio r
JOIN Medicamentos m ON r.id_med = m.id_med
JOIN Muestras mu ON r.id_muestra = mu.id_muestra
JOIN Puntos_Monitoreo p ON mu.id_punto = p.id_punto
"""
df = pd.read_sql(query, conn)

# Metricas principales
col1, col2, col3 = st.columns(3)
col1.metric("Fármacos Monitoreados", df['nombre_comun'].nunique())
col2.metric("Riesgo Máximo Detectado", f"{df['riesgo'].max():.2f}x")
col3.metric("Ríos Analizados", df['nombre_rio'].nunique())

# Gráfico de barras de riesgo
st.subheader("Niveles de Riesgo por Medicamento y Río")
fig = px.bar(df, x='nombre_rio', y='concentracion_hallada', color='nombre_comun', 
             barmode='group', labels={'concentracion_hallada': 'Concentración (ng/L)'})
st.plotly_chart(fig, use_container_width=True)

# Tabla interactiva con filtro
st.subheader("Datos Detallados de Laboratorio")
filtro_rio = st.multiselect("Filtrar por Río", options=df['nombre_rio'].unique(), default=df['nombre_rio'].unique())
df_filtrado = df[df['nombre_rio'].isin(filtro_rio)]
st.dataframe(df_filtrado)
