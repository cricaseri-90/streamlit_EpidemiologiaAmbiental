# 🧪 Epidemiología Ambiental - Monitoreo de Fármacos en Ríos

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-4479A1?style=for-the-badge&logo=python&logoColor=white)

## 📋 Descripción del Proyecto
Este dashboard integrador analiza la presencia de contaminantes farmacéuticos en cuerpos de agua, basándose en la problemática reportada por la **Universidad Nacional de Colombia**. Permite evaluar el riesgo epidemiológico y visualizar la distribución de químicos mediante análisis estadístico avanzado.

Este proyecto desarrolla un sistema de análisis de datos para evaluar la presencia de **contaminantes emergentes (medicamentos)** en fuentes hídricas y su posible impacto en la salud pública y los ecosistemas con referencia en la noticia 'Los medicamentos como contaminantes: el peligro oculto en nuestros ríos'. El problema surge porque residuos de fármacos provenientes de actividades humanas pueden llegar a ríos, lagos o fuentes de agua, generando riesgos como **resistencia a antibióticos o disrupción endocrina** en organismos vivos.

Para abordar este problema se diseñó una **base de datos relacional en MySQL**, basada en un **Modelo Entidad–Relación (MER)** que integra información química, ambiental y epidemiológica. La estructura permite almacenar, relacionar y analizar datos provenientes del monitoreo ambiental.

El modelo incluye cuatro entidades principales. **Medicamentos**, que contiene información sobre los fármacos analizados, su farmacodinamia y los límites de seguridad establecidos. **Puntos_Monitoreo**, que registra la ubicación geográfica y el contexto ambiental de los sitios donde se recolectan las muestras de agua. **Muestras**, que representa cada evento de recolección realizado en un punto de monitoreo en una fecha determinada. Finalmente, **Resultados_Laboratorio**, que conecta las muestras con los medicamentos analizados y registra la concentración detectada de cada compuesto.

A partir de esta estructura se generan **datos sintéticos y consultas SQL** que permiten analizar concentraciones de medicamentos, comparar valores con umbrales de seguridad y detectar posibles riesgos ambientales.

## 🚀 Instalación y Uso
1. Clonar el repositorio: `git clone https://github.com/tu-usuario/tu-proyecto.git`
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar la app: `streamlit run app.py`

## 🛠️ Estructura del Dataset
* **Medicamentos:** Catálogo con umbrales de seguridad (PNEC).
* **Puntos_Monitoreo:** Ubicaciones geográficas y población.
* **Muestras/Resultados:** Datos de laboratorio con concentraciones en ng/L.

## 🚀 Características principales
- **Landing Page:** Introducción al contexto epidemiológico.
- **Dashboard Interactivo:** Filtros por regiones y visualización en tiempo real.
- **Gráficos Científicos:** Implementación de Seaborn para análisis de densidad y Plotly para interactividad.
- **Documentación Integrada:** Pestañas dedicadas a la metodología y ayuda al usuario.

## 🛠️ Requisitos
Asegúrate de tener instaladas las siguientes librerías:
- `streamlit`
- `pandas`
- `numpy`
- `seaborn`
- `matplotlib`
- `plotly`
- `sqlite3`

## 👤 Autoría
Realizado por **Cristian C. Serna-Rivera** **Wilson Castañeda** - *Talento TECH 2024*

---
*Datos obtenidos de prueba generados con base en la noticia https://periodico.unal.edu.co/articulos/los-medicamentos-como-contaminantes-el-peligro-oculto-en-nuestros-rios*
