# 🏍️ Analizador de Rutas Meteorológicas (GPX)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://meteorologiagpx.streamlit.app)

**¡Prueba la aplicación en vivo aquí! 👉 [https://meteorologiagpx.streamlit.app](https://meteorologiagpx.streamlit.app)**

## 🌟 Descripción

¿Planeando una ruta en moto, bicicleta o coche y no sabes qué tiempo hará exactamente cuando pases por cada punto?

**Meteorología-GPX** es una aplicación interactiva construida con [Streamlit](https://streamlit.io/) que te permite subir cualquier archivo de ruta GPS (`.gpx`), definir tu hora de salida y tu velocidad media, y calcular de forma precisa la **previsión meteorológica exacta** (temperatura, lluvia, viento) que te encontrarás en cada tramo de la ruta a la Hora Estimada de Llegada (ETA).

En lugar de mirar el tiempo general de una ciudad, esta herramienta analiza las coordenadas geográficas a lo largo de tu viaje y realiza peticiones quirúrgicas a la API de clima para darte información hiperlocalizada y sincronizada con tu avance.

## ✨ Características Principales

*   **🗺️ Mapa 3D Interactivo (PyDeck):** Visualiza tu ruta con marcadores dinámicos que cambian de color y tamaño según las condiciones climáticas (Ej. Marcadores azules grandes para lluvia intensa, gradientes térmicos para zonas secas).
*   **📈 Perfil de Elevación y Clima (Plotly):** Entiende la topografía de tu viaje superpuesta con la temperatura y la precipitación a lo largo de los kilómetros.
*   **⚡ Alto Rendimiento (Polars):** Procesamiento ultra-rápido de archivos GPX masivos gracias al uso de dataframes optimizados en Rust.
*   **🎯 Previsión Quirúrgica Asíncrona (Open-Meteo):** Integración con la API de Open-Meteo mediante peticiones asíncronas por lotes (batching), agrupando puntos por hora para minimizar el tráfico de red y maximizar la velocidad.
*   **📊 Tabla de Riesgos:** Un resumen claro paso a paso con indicadores visuales de lluvia y temperatura.
*   **🖼️ Interfaz Premium:** Diseño moderno con efectos de glassmorphism y fuentes elegantes.

## 🛠️ ¿Cómo funciona?

El análisis se realiza en cinco etapas críticas:

1.  **Ingesta de Datos:** El archivo `.gpx` se parsea y se convierte en un DataFrame de **Polars**.
2.  **Cálculo Geoespacial:** Se calcula la distancia acumulada y la elevación entre cada par de coordenadas usando la fórmula de Haversine vectorizada.
3.  **Muestreo de Ruta:** Para evitar saturar las APIs, la ruta se "remuestrea" (downsampling) según el intervalo de clima definido (ej. cada 15 km).
4.  **Cálculo de ETA:** Basándose en la hora de salida y la velocidad media, se estima el momento exacto (ETA) en el que pasarás por cada punto de control.
5.  **Consulta de Clima por Lotes:** Se agrupan los puntos por hora de llegada y se realizan peticiones asíncronas a Open-Meteo, descargando solo la previsión relevante para ese momento preciso.

## 📂 Estructura del Proyecto

```text
Meteorologia-GPX/
├── app.py                # Punto de entrada de la aplicación Streamlit
├── meteorologia_gpx/     # Paquete principal con la lógica modular
│   ├── charts.py         # Visualizaciones (PyDeck y Plotly)
│   ├── geospatial.py     # Motor de cálculos geoespaciales y ETAs
│   ├── gpx_processor.py  # Procesamiento de archivos GPX con Polars
│   ├── style_utils.py    # Gestión de CSS y diseño visual
│   └── weather_client.py # Cliente asíncrono para la API de Open-Meteo
├── tests/                # Suite de pruebas automatizadas
└── pyproject.toml        # Gestión de dependencias con uv
```

## 🚀 Instalación y Uso Local

Este proyecto utiliza [uv](https://github.com/astral-sh/uv) para una gestión de dependencias y entornos virtual ultra-rápida y reproducible.

### Pasos

1.  **Instalar `uv`** (si no lo tienes):
    ```bash
    curl -LsSf https://astral-sh/uv/install.sh | sh
    ```

2.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/Chane12/Meteorologia-GPX.git
    cd Meteorologia-GPX
    ```

3.  **Sincronizar el entorno e instalar dependencias:**
    `uv` creará automáticamente un entorno virtual y sincronizará todas las librerías necesarias con el archivo `uv.lock`.
    ```bash
    uv sync
    ```

4.  **Ejecutar la aplicación:**
    ```bash
    uv run streamlit run app.py
    ```

5.  Abre tu navegador en la dirección local que indique Streamlit (normalmente `http://localhost:8501`).

## 🧪 Pruebas (Unit Testing)

Se ha incluido una suite completa de pruebas para asegurar la integridad de los cálculos y el procesamiento de datos:

```bash
uv run pytest
```

## 🛠️ Tecnologías Utilizadas

*   **[uv](https://github.com/astral-sh/uv):** Gestión de paquetes y entornos Python de alto rendimiento.
*   **[Streamlit](https://streamlit.io/):** Framework para la interfaz web.
*   **[Polars](https://pola.rs/):** Manipulación eficiente de datos.
*   **[GPXPY](https://github.com/tkrajina/gpxpy):** Parseo de archivos de rutas GPS.
*   **[Open-Meteo API](https://open-meteo.com/):** Datos meteorológicos de alta precisión (sin API Key).
*   **[PyDeck](https://deckgl.readthedocs.io/) & [Plotly](https://plotly.com/python/):** Mapas 3D y gráficos interactivos.
*   **[HTTPX](https://www.python-httpx.org/) & Asyncio:** Peticiones de red asíncronas optimizadas.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar la predicción, añadir nuevos tipos de mapas o optimizar los algoritmos geospaciales, no dudes en abrir un *Issue* o enviar un *Pull Request*.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](LICENSE) para más detalles (o siéntete libre de usar el código como base para tus proyectos).
