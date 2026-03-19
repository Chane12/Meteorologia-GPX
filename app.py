import streamlit as st
import asyncio
from datetime import datetime, date, time
import polars as pl

from meteorologia_gpx.gpx_processor import GPXProcessor
from meteorologia_gpx.geospatial import GeospatialEngine
from meteorologia_gpx.weather_client import WeatherAPIClient
from meteorologia_gpx.charts import UIBuilder
from meteorologia_gpx.style_utils import StyleManager

st.set_page_config(
    page_title="Analizador de Rutas Meteorológicas",
    page_icon="🌦️",
    layout="wide"
)

def init_session_state():
    if "polars_df" not in st.session_state:
        st.session_state.polars_df = None
    if "weather_df" not in st.session_state:
        st.session_state.weather_df = None

@st.cache_data(show_spinner=False)
def get_route_data(gpx_content):
    full_route_df = GPXProcessor.parse_to_dataframe(gpx_content)
    full_route_df = GeospatialEngine.calculate_cumulative_distance(full_route_df)
    return full_route_df

@st.cache_data(show_spinner=False)
def get_weather_forecast(_polars_df, interval, start_dt, speed):
    downsampled_df = GeospatialEngine.downsample_by_distance(_polars_df, interval)
    eta_df = GeospatialEngine.calculate_etas(downsampled_df, start_dt, speed)
    weather_client = WeatherAPIClient()
    return asyncio.run(weather_client.fetch_route_weather(eta_df))

init_session_state()
StyleManager.inject_css()

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("## 🛣️ Configuración")
    uploaded_file = st.file_uploader("Sube tu archivo GPX", type=["gpx"], help="Arrastra tu archivo .gpx aquí.")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🕒 Detalles de Salida")
    start_date = st.sidebar.date_input("Fecha de Salida", date.today())
    start_time = st.sidebar.time_input("Hora de Salida", time(8, 0))
    avg_speed = st.sidebar.slider("Velocidad Media (km/h)", min_value=10, max_value=130, value=60)
    polling_interval = st.sidebar.slider("Intervalo de Clima (km)", min_value=5, max_value=50, value=15)

# --- Main Title and Header ---
StyleManager.render_header("METEO ROUTE ANALYZER", "Optimiza tu viaje con previsión meteorológica precisa en cada punto del camino.")

if uploaded_file is not None:
    gpx_content = uploaded_file.getvalue().decode("utf-8")
    try:
        with st.spinner("Analizando archivo GPX..."):
            full_route_df = get_route_data(gpx_content)
            st.session_state.polars_df = full_route_df
            
            total_dist = full_route_df["cumulative_distance_km"].tail(1)[0]
            st.sidebar.success(f"Distancia total: {total_dist:.2f} km")
            
    except Exception as e:
        st.error(f"Error al leer el archivo GPX: {str(e)}")
        st.stop()

    if st.sidebar.button("Calcular Clima en la Ruta", type="primary"):
        start_datetime = datetime.combine(start_date, start_time)
        
        with st.spinner(f"Descargando previsión meteorológica cada {polling_interval} km..."):
            weather_df = get_weather_forecast(st.session_state.polars_df, polling_interval, start_datetime, avg_speed)
            st.session_state.weather_df = weather_df

if st.session_state.polars_df is not None:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Mapa de la Ruta")
        pydeck_map = UIBuilder.build_route_map(st.session_state.polars_df, st.session_state.weather_df)
        st.pydeck_chart(pydeck_map, width="stretch")
        
    with col2:
        if st.session_state.weather_df is not None:
            st.subheader("Resumen Meteorológico")
            w_df = st.session_state.weather_df
            
            # Filtramos nulos para calcular métricas correctamente
            valid_w_df = w_df.drop_nulls(subset=["temperature_2m", "precipitation"])
            
            if valid_w_df.is_empty():
                st.error("❌ No se pudieron obtener los datos meteorológicos.")
            else:
                max_temp = valid_w_df["temperature_2m"].max()
                min_temp = valid_w_df["temperature_2m"].min()
                max_rain = valid_w_df["precipitation"].max()
                
                StyleManager.render_weather_summary(max_temp, min_temp, max_rain)
                
            display_df = w_df.select([
                pl.col("cumulative_distance_km").round(1).alias("Km"),
                pl.col("eta").dt.strftime("%H:%M").alias("ETA"),
                pl.col("temperature_2m").alias("Temp (°C)"),
                pl.col("precipitation").alias("Lluvia (mm)"),
                pl.col("weather_desc").alias("Clima")
            ]).to_pandas()
            
            st.dataframe(
                display_df, 
                width="stretch", 
                hide_index=True,
                column_config={
                    "Lluvia (mm)": st.column_config.ProgressColumn(
                        "Lluvia (mm)",
                        help="Volumen de precipitación estimada (mm)",
                        format="%f mm",
                        min_value=0.0,
                        max_value=15.0,
                    ),
                    "Temp (°C)": st.column_config.NumberColumn(
                        "Temp (°C)",
                        help="Temperatura térmica estimada",
                        format="%f °C",
                    )
                }
            )
            
if st.session_state.weather_df is not None:
    st.subheader("Perfil de Viaje")
    timeline_chart = UIBuilder.build_timeline_chart(st.session_state.weather_df)
    st.plotly_chart(timeline_chart, width="stretch")
