import pydeck as pdk
import plotly.graph_objects as go
import polars as pl
from plotly.subplots import make_subplots

class UIBuilder:
    """Constructs visualizations for the Streamlit app."""

    @staticmethod
    def build_route_map(full_route_df: pl.DataFrame, weather_points_df: pl.DataFrame = None) -> pdk.Deck:
        """
        Creates a high-performance 3D map using PyDeck.
        """
        center_lat = full_route_df["latitude"].mean()
        center_lon = full_route_df["longitude"].mean()

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=10,
            pitch=45,
            bearing=0
        )

        layers = []

        coords = full_route_df.select(["longitude", "latitude"]).to_numpy().tolist()
        path_data = [{"path": coords, "name": "Ruta"}]

        route_layer = pdk.Layer(
            type="PathLayer",
            data=path_data,
            pickable=True,
            get_color=[255, 50, 50],
            width_scale=20,
            width_min_pixels=3,
            get_path="path",
            get_width=5
        )
        layers.append(route_layer)

        if weather_points_df is not None and not weather_points_df.is_empty():
            weather_data = weather_points_df.to_dicts()
            clean_weather_data = []
            
            for w in weather_data:
                eta_str = w["eta"].strftime("%d/%m/%Y %H:%M") if w.get("eta") else "N/A"
                if w.get("temperature_2m") is None:
                    tooltip = f"ETA: {eta_str}<br/>Sin datos meteorológicos"
                else:
                    tooltip = (f"ETA: {eta_str}<br/>"
                               f"Temp: {w['temperature_2m']}°C<br/>"
                               f"Lluvia: {w['precipitation']} mm<br/>"
                               f"Viento: {w['wind_speed_10m']} km/h<br/>"
                               f"Clima: {w['weather_desc']}")
                
                clean_weather_data.append({
                    "longitude": w["longitude"],
                    "latitude": w["latitude"],
                    "tooltip": tooltip
                })

            scatter_layer = pdk.Layer(
                "ScatterplotLayer",
                data=clean_weather_data,
                get_position=["longitude", "latitude"],
                get_fill_color=[50, 150, 255, 200],
                get_radius=800,
                radius_min_pixels=5,
                radius_max_pixels=15,
                pickable=True,
            )
            layers.append(scatter_layer)

        tooltip = {
            "html": "<b>{tooltip}</b>",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white"
            }
        }

        return pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            tooltip=tooltip if weather_points_df is not None else True,
            map_style="light"
        )

    @staticmethod
    def build_timeline_chart(weather_df: pl.DataFrame) -> go.Figure:
        """
        Creates a Plotly timeline showing elevation and weather metrics.
        """
        distances = weather_df["cumulative_distance_km"].to_numpy()
        elevations = weather_df["elevation"].to_numpy()
        temps = weather_df["temperature_2m"].to_numpy()
        rains = weather_df["precipitation"].to_numpy()

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(
                x=distances, y=elevations,
                fill='tozeroy',
                mode='lines',
                line=dict(color='rgba(100, 100, 100, 0.5)'),
                name='Elevación (m)'
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                x=distances, y=temps,
                mode='lines+markers',
                line=dict(color='red', width=2),
                name='Temp (°C)'
            ),
            secondary_y=True,
        )

        fig.add_trace(
            go.Bar(
                x=distances, y=rains,
                marker_color='blue',
                name='Lluvia (mm)',
                opacity=0.6
            ),
            secondary_y=True,
        )

        fig.update_layout(
            title_text="Clima vs Elevación en la Ruta",
            xaxis_title="Distancia (km)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=50, b=0)
        )

        fig.update_yaxes(title_text="Elevación (m)", secondary_y=False)
        fig.update_yaxes(title_text="Clima (°C / mm)", secondary_y=True)

        return fig
