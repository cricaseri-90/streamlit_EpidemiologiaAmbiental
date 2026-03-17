import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# --- Configuración de Página ---
st.set_page_config(page_title="Eco-Fármaco Dashboard", layout="wide", page_icon="🧪")

# --- Estilos CSS Personalizados para Tarjetas ---
st.markdown("""
    <style>
    .card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #4CAF50;
        margin-bottom: 20px;
    }
    .card-title {
        font-size: 1.1em;
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
    }
    .card-value {
        font-size: 1.5em;
        font-weight: bold;
        color: #2c3e50;
    }
    .alert-high { border-left-color: #e74c3c; }
    .alert-med { border-left-color: #f39c12; }
    .alert-low { border-left-color: #27ae60; }
    </style>
""", unsafe_allow_html=True)

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
    
    cursor.execute("SELECT COUNT(*) FROM Medicamentos")
    if cursor.fetchone()[0] == 0:
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

@st.cache_data(ttl=600)
def load_data(_conn):
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
    if os.path.exists('epidemiologia.db'):
        os.remove('epidemiologia.db')
    st.rerun()

# --- Componentes de Tarjetas Interactivas ---

def render_interactive_cards(df_filtrado, filtro_rio):
    """
    Renderiza 3 tarjetas interactivas:
    1. Estado de Alerta (Semáforo)
    2. Filtro Rápido por Fármaco
    3. Estadística del Río Seleccionado
    """
    col_card1, col_card2, col_card3 = st.columns(3)
    
    # --- TARJETA 1: Estado de Alerta (Descriptiva) ---
    with col_card1:
        max_riesgo_global = df_filtrado['riesgo'].max() if not df_filtrado.empty else 0
        
        if max_riesgo_global > 1.0:
            estado = "⚠️ CRÍTICO"
            clase = "alert-high"
            desc = "Se superó el umbral de riesgo (RQ > 1)"
        elif max_riesgo_global > 0.5:
            estado = "⚡ PRECAUCIÓN"
            clase = "alert-med"
            desc = "Niveles moderados detectados"
        else:
            estado = "✅ NORMAL"
            clase = "alert-low"
            desc = "Niveles dentro de lo esperado"
            
        st.markdown(f"""
            <div class="card {clase}">
                <div class="card-title">Estado de Alerta Ambiental</div>
                <div class="card-value">{estado}</div>
                <div style="font-size: 0.9em; color: #666;">{desc}</div>
                <div style="font-size: 0.8em; margin-top:5px;">Riesgo Máx: {max_riesgo_global:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    # --- TARJETA 2: Filtro Rápido (Interactiva) ---
    with col_card2:
        st.markdown("""
            <div class="card">
                <div class="card-title">🔍 Filtro Rápido por Fármaco</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Usamos un contenedor dentro de la columna para el widget
        farmaco_seleccionado = st.selectbox(
            "Aislar medicamento:",
            options=["Todos"] + list(df_filtrado['nombre_comun'].unique()),
            key="card_filtro_farmaco",
            label_visibility="collapsed"
        )
        # Nota: Este filtro se aplicará más abajo en la lógica principal

    # --- TARJETA 3: Estadística Dinámica (Descriptiva) ---
    with col_card3:
        # Calculamos stats solo para los ríos seleccionados en la sidebar
        if filtro_rio:
            rio_stats = df_filtrado[df_filtrado['nombre_rio'].isin(filtro_rio)]
            avg_conc = rio_stats['concentracion_hallada'].mean()
            total_muestras = len(rio_stats)
            
            st.markdown(f"""
                <div class="card">
                    <div class="card-title">📊 Estadísticas de Ríos Seleccionados</div>
                    <div class="card-value">{avg_conc:.1f} ng/L</div>
                    <div style="font-size: 0.9em; color: #666;">Concentración Promedio</div>
                    <div style="font-size: 0.8em; margin-top:5px; border-top:1px solid #ddd; padding-top:5px;">
                        Muestras analizadas: <b>{total_muestras}</b>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='card'><div class='card-title'>Sin datos seleccionados</div></div>", unsafe_allow_html=True)
            
    return farmaco_seleccionado

# --- Ejecución Principal ---

def main():
    st.title("🧪 Vigilancia Epidemiológica Ambiental")
    st.markdown("Análisis de medicamentos como contaminantes hídricos (Ref: UNAL)")
    st.markdown("---")

    # Conectar
    conn = init_connection()
    init_db(conn)
    
    if not check_tables_exist(conn):
        st.error("❌ Error crítico: Las tablas no se pudieron crear.")
        st.stop()

    # Cargar Datos
    try:
        df = load_data(conn)
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        if st.button("🔄 Reiniciar Base de Datos"):
            reset_database()
        return

    # --- Barra Lateral (Filtros Globales) ---
    st.sidebar.header("🔍 Filtros Globales")
    filtro_rio = st.sidebar.multiselect(
        "Seleccionar Río", 
        options=df['nombre_rio'].unique(), 
        default=df['nombre_rio'].unique()
    )

    # Aplicar Filtros de Sidebar
    df_filtrado = df[df['nombre_rio'].isin(filtro_rio)]

    # --- KPIs Principales ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Fármacos Monitoreados", df_filtrado['nombre_comun'].nunique())
    with col2:
        max_riesgo = df_filtrado['riesgo'].max() if not df_filtrado.empty else 0
        st.metric("Riesgo Máximo (RQ)", f"{max_riesgo:.2f}x")
    with col3:
        st.metric("Ríos Analizados", df_filtrado['nombre_rio'].nunique())

    st.markdown("---")

    # --- SECCIÓN DE TARJETAS INTERACTIVAS (NUEVO) ---
    st.subheader("Panel de Control Inteligente")
    farmaco_card_filter = render_interactive_cards(df_filtrado, filtro_rio)
    
    # Aplicar el filtro de la tarjeta al dataframe para los gráficos
    if farmaco_card_filter != "Todos":
        df_final = df_filtrado[df_filtrado['nombre_comun'] == farmaco_card_filter]
        st.info(f"🔎 Mostrando datos filtrados para: **{farmaco_card_filter}**")
    else:
        df_final = df_filtrado

    # --- Gráficos ---
    st.subheader("Niveles de Riesgo por Medicamento y Río")
    
    if df_final.empty:
        st.warning("No hay datos para mostrar con los filtros actuales.")
    else:
        fig = px.bar(
            df_final, 
            x='nombre_rio', 
            y='concentracion_hallada', 
            color='nombre_comun', 
            barmode='group', 
            labels={'concentracion_hallada': 'Concentración (ng/L)'},
            log_y=True,
            title=f"Distribución de Concentraciones {'(' + farmaco_card_filter + ')' if farmaco_card_filter != 'Todos' else ''}"
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Tabla Interactiva ---
    st.subheader("Datos Detallados de Laboratorio")
    st.dataframe(df_final, use_container_width=True)
    
    # Botón de descarga
    csv = df_final.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Datos Filtrados (CSV)",
        data=csv,
        file_name='datos_vigilancia.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()
