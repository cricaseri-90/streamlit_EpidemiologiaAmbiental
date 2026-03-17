import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# --- Configuración de Página ---
st.set_page_config(page_title="Eco-Fármaco Dashboard", layout="wide", page_icon="🧪")

# --- Funciones de Base de Datos ---

@st.cache_resource
def init_connection():
    """Inicializa la conexión a la base de datos."""
    return sqlite3.connect('epidemiologia.db', check_same_thread=False)

def check_tables_exist(conn):
    """Verifica si las tablas necesarias existen."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Resultados_Laboratorio'")
    return cursor.fetchone() is not None

def init_db(conn):
    """Crea las tablas y datos de ejemplo si no existen."""
    cursor = conn.cursor()
    
    # Crear tablas (IF NOT EXISTS asegura que no falla si ya existen)
    cursor.execute('''CREATE TABLE IF NOT EXISTS Medicamentos (
                        id_med INTEGER PRIMARY KEY, 
                        nombre_comun TEXT, 
                        pnec_ngl REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Puntos_Monitoreo (
                        id_punto INTEGER PRIMARY KEY, 
                        nombre_rio TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Muestras (
                        id_muestra INTEGER PRIMARY KEY, 
                        id_punto INTEGER, 
                        fecha_muestreo DATE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Resultados_Laboratorio (
                        id_res INTEGER PRIMARY KEY, 
                        id_muestra INTEGER, 
                        id_med INTEGER, 
                        concentracion_hallada REAL)''')
    
    # Verificar si ya hay datos
    cursor.execute("SELECT COUNT(*) FROM Medicamentos")
    if cursor.fetchone()[0] == 0:
        # Insertar datos de ejemplo solo si está vacío
        meds = [(1, 'Diclofenaco', 50.0), (2, 'Carbamazepina', 200.0), (3, 'Ibuprofeno', 300.0)]
        rios = [(1, 'Río Bogotá'), (2, 'Río Magdalena'), (3, 'Río Cauca')]
        
        cursor.executemany("INSERT INTO Medicamentos VALUES (?,?,?)", meds)
        cursor.executemany("INSERT INTO Puntos_Monitoreo VALUES (?,?)", rios)
        
        muestras = [(1, 1, '2023-01-01'), (2, 2, '2023-01-02'), (3, 3, '2023-01-03')]
        cursor.executemany("INSERT INTO Muestras VALUES (?,?,?)", muestras)
        
        resultados = [
            (1, 1, 1, 120.5), (2, 1, 2, 10.0), (3, 1, 3, 450.0),
            (4, 2, 1, 30.0),  (5, 2, 2, 210.0), (6, 2, 3, 50.0),
            (7, 3, 1, 80.0),  (8, 3, 2, 15.0),  (9, 3, 3, 100.0)
        ]
        cursor.executemany("INSERT INTO Resultados_Laboratorio VALUES (?,?,?,?)", resultados)
        
        conn.commit()
        st.success("✅ Base de datos inicializada correctamente.")

@st.cache_data(ttl=600)
def load_data(_conn):  # ✅ El guion bajo evita el error de hashing
    """Carga los datos desde SQL a Pandas."""
    query = """
    SELECT 
        p.nombre_rio, 
        m.nombre_comun, 
        r.concentracion_hallada, 
        m.pnec_ngl,
        (r.concentracion_hallada / m.pnec_ngl) as riesgo
    FROM Resultados_Laboratorio r
    JOIN Medicamentos m ON r.id_med = m.id_med
    JOIN Muestras mu ON r.id_muestra = mu.id_muestra
    JOIN Puntos_Monitoreo p ON mu.id_punto = p.id_punto
    """
    df = pd.read_sql(query, _conn)
    return df

def reset_database():
    """Elimina la base de datos para reiniciar desde cero."""
    os.remove('epidemiologia.db')
    st.rerun()

# --- Ejecución Principal ---

def main():
    st.title("🧪 Vigilancia Epidemiológica Ambiental")
    st.markdown("Análisis de medicamentos como contaminantes hídricos (Ref: UNAL)")
    st.markdown("---")

    # Conectar
    conn = init_connection()
    
    # Inicializar DB (Verifica tablas, no solo el archivo)
    init_db(conn)
    
    # Verificación final antes de cargar
    if not check_tables_exist(conn):
        st.error("❌ Error crítico: Las tablas no se pudieron crear.")
        st.stop()

    # Cargar Datos
    try:
        df = load_data(conn)
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        # Botón de emergencia para reiniciar
        if st.button("🔄 Reiniciar Base de Datos"):
            reset_database()
        return

    # --- Barra Lateral (Filtros) ---
    st.sidebar.header("🔍 Filtros")
    filtro_rio = st.sidebar.multiselect(
        "Seleccionar Río", 
        options=df['nombre_rio'].unique(), 
        default=df['nombre_rio'].unique()
    )

    # Aplicar Filtros
    df_filtrado = df[df['nombre_rio'].isin(filtro_rio)]

    # --- KPIs (Métricas) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Fármacos Monitoreados", df_filtrado['nombre_comun'].nunique())
    with col2:
        max_riesgo = df_filtrado['riesgo'].max() if not df_filtrado.empty else 0
        st.metric("Riesgo Máximo (RQ)", f"{max_riesgo:.2f}x")
    with col3:
        st.metric("Ríos Analizados", df_filtrado['nombre_rio'].nunique())

    st.markdown("---")

    # --- Gráficos ---
    st.subheader("Niveles de Riesgo por Medicamento y Río")
    
    fig = px.bar(
        df_filtrado, 
        x='nombre_rio', 
        y='concentracion_hallada', 
        color='nombre_comun', 
        barmode='group', 
        labels={'concentracion_hallada': 'Concentración (ng/L)'},
        log_y=True
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Tabla Interactiva ---
    st.subheader("Datos Detallados de Laboratorio")
    st.dataframe(df_filtrado, use_container_width=True)
    
    # Botón de descarga
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Datos Filtrados (CSV)",
        data=csv,
        file_name='datos_vigilancia.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()
