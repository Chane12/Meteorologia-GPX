# 🏍️ Analizador de Rutas Meteorológicas (GPX)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://meteorologiagpx.streamlit.app)

**¡Prueba la aplicación en vivo aquí! 👉 [https://meteorologiagpx.streamlit.app](https://meteorologiagpx.streamlit.app)**

## 🌟 Descripción

¿Planeando una ruta en moto, bicicleta o coche y no sabes qué tiempo hará exactamente cuando pases por cada punto?

**Meteorología-GPX** es una aplicación interactiva construida con [Streamlit](https://streamlit.io/) que te permite subir cualquier archivo de ruta GPS (`.gpx`), definir tu hora de salida y tu velocidad media, y calcular de forma precisa la **previsión meteorológica exacta** (temperatura, lluvia, viento) que te encontrarás en cada tramo de la ruta a la Hora Estimada de Llegada (ETA).

En lugar de mirar el tiempo general de una ciudad, esta herramienta analiza las coordenadas geográficas a lo largo de tu viaje y realiza peticiones quirúrgicas a la API de clima para darte información hiperlocalizada y sincronizada con tu avance.

## ✨ Características Principales

* **🗺️ Mapa 3D Interactivo (PyDeck):** Visualiza tu ruta con marcadores dinámicos que cambian de color y tamaño según las condiciones climáticas (Ej. Nodos azules grandes para lluvia intensa, gradientes térmicos para zonas secas).
* **📈 Perfil de Elevación y Clima (Plotly):** Entiende la topografía de tu viaje superpuesta con la temperatura y la precipitación a lo largo de los kilómetros.
* **⚡ Alto Rendimiento (Polars):** Procesamiento ultra-rápido de archivos GPX masivos gracias al uso de dataframes en Rust.
* **🎯 Previsión Quirúrgica (Open-Meteo):** Integración asíncrona y optimizada con la API de Open-Meteo para descargar únicamente los datos horarios necesarios, minimizando el consumo de red.
* **📊 Tabla de Riesgos:** Un resumen claro paso a paso con indicadores visuales de lluvia y temperatura.

## 🚀 Instalación y Uso Local

Si deseas correr el proyecto en tu propia máquina:

### Requisitos Previos

* Python 3.9 o superior.
* Se recomienda crear un entorno virtual (`venv` o `conda`).

### Pasos

1. **Clonar el repositorio:**

    ```bash
    git clone https://github.com/Chane12/Meteorologia-GPX.git
    cd Meteorologia-GPX
    ```

2. **Instalar las dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Ejecutar la aplicación:**

    ```bash
    streamlit run app.py
    ```

4. Abre tu navegador en la dirección local que indique Streamlit (normalmente `http://localhost:8501`).

## 🛠️ Tecnologías Utilizadas

* **[Streamlit](https://streamlit.io/):** Framework para la interfaz web.
* **[Polars](https://pola.rs/):** Manipulación eficiente de datos.
* **[GPXPY](https://github.com/tkrajina/gpxpy):** Parseo de archivos de rutas GPS.
* **[Open-Meteo API](https://open-meteo.com/):** Proveedor de datos meteorológicos de alta precisión (sin necesidad de API Key).
* **[PyDeck](https://deckgl.readthedocs.io/) & [Plotly](https://plotly.com/python/):** Creación de mapas 3D avanzados y gráficos financieros/científicos.
* **[HTTPX](https://www.python-httpx.org/) & Asyncio:** Peticiones de red asíncronas de alto rendimiento.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar la predicción, añadir nuevos tipos de mapas o optimizar los algoritmos geospaciales, no dudes en abrir un *Issue* o enviar un *Pull Request*.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](LICENSE) para más detalles (o siéntete libre de usar el código como base para tus proyectos).
