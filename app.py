import streamlit as st
import asyncio
from datetime import datetime, date, time
import polars as pl

from src.gpx_processor import GPXProcessor
from src.geospatial import GeospatialEngine
from src.weather_client import WeatherAPIClient
from src.charts import UIBuilder

st.set_page_config(
    page_title="Analizador de Rutas Meteorológicas",
    page_icon="🏍️",
    layout="wide"
)

def init_session_state():
    if "polars_df" not in st.session_state:
        st.session_state.polars_df = None
    if "weather_df" not in st.session_state:
        st.session_state.weather_df = None

init_session_state()

st.sidebar.title("🛣️ Configuración")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo GPX", type=["gpx"])

st.sidebar.markdown("### Detalles de Salida")
start_date = st.sidebar.date_input("Fecha de Salida", date.today())
start_time = st.sidebar.time_input("Hora de Salida", time(8, 0))
avg_speed = st.sidebar.slider("Velocidad Media (km/h)", min_value=10, max_value=130, value=60)
polling_interval = st.sidebar.slider("Intervalo de Clima (km)", min_value=5, max_value=50, value=15)

st.title("Analizador de Rutas Meteorológicas")
st.markdown("Carga una ruta GPS, define cuándo sales y evalúa las condiciones climáticas exactas a lo largo de tu viaje.")

if uploaded_file is not None:
    with st.spinner("Analizando archivo GPX..."):
        gpx_content = uploaded_file.getvalue().decode("utf-8")
        try:
            full_route_df = GPXProcessor.parse_to_dataframe(gpx_content)
            full_route_df = GeospatialEngine.calculate_cumulative_distance(full_route_df)
            st.session_state.polars_df = full_route_df
            
            total_dist = full_route_df["cumulative_distance_km"].tail(1)[0]
            st.sidebar.success(f"Distancia total: {total_dist:.2f} km")
            
        except Exception as e:
            st.error(f"Error al leer el archivo GPX: {str(e)}")
            st.stop()

    if st.sidebar.button("Calcular Clima en la Ruta", type="primary"):
        start_datetime = datetime.combine(start_date, start_time)
        
        with st.spinner(f"Descargando previsión meteorológica cada {polling_interval} km..."):
            downsampled_df = GeospatialEngine.downsample_by_distance(st.session_state.polars_df, polling_interval)
            eta_df = GeospatialEngine.calculate_etas(downsampled_df, start_datetime, avg_speed)
            
            weather_client = WeatherAPIClient()
            weather_df = asyncio.run(weather_client.fetch_route_weather(eta_df))
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
            
            max_temp = w_df["temperature_2m"].max()
            min_temp = w_df["temperature_2m"].min()
            max_rain = w_df["precipitation"].max()
            
            st.metric("Temp. Máxima Estimada", f"{max_temp}°C")
            st.metric("Temp. Mínima Estimada", f"{min_temp}°C")
            
            if max_rain is not None and max_rain > 0:
                st.warning(f"⚠️ Previsión de lluvia (Máx: {max_rain}mm).")
            else:
                st.success("☀️ No se prevé lluvia en la ruta.")
                
            display_df = w_df.select([
                pl.col("cumulative_distance_km").round(1).alias("Km"),
                pl.col("eta").dt.strftime("%H:%M").alias("ETA"),
                pl.col("temperature_2m").alias("Temp (°C)"),
                pl.col("precipitation").alias("Lluvia (mm)"),
                pl.col("weather_desc").alias("Clima")
            ]).to_pandas()
            
            st.dataframe(display_df, width="stretch", hide_index=True)
            
if st.session_state.weather_df is not None:
    st.subheader("Perfil de Viaje")
    timeline_chart = UIBuilder.build_timeline_chart(st.session_state.weather_df)
    st.plotly_chart(timeline_chart, width="stretch")
