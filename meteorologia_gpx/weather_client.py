import httpx
import asyncio
import polars as pl
from typing import List, Dict, Any
from datetime import datetime

# WMO Weather interpretation codes mapped to Spanish
WMO_CODES_ES = {
    0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado", 3: "Nublado",
    45: "Niebla", 48: "Niebla con escarcha",
    51: "Llovizna ligera", 53: "Llovizna moderada", 55: "Llovizna densa",
    56: "Llovizna helada ligera", 57: "Llovizna helada densa",
    61: "Lluvia leve", 63: "Lluvia moderada", 65: "Lluvia fuerte",
    66: "Lluvia helada leve", 67: "Lluvia helada fuerte",
    71: "Nieve leve", 73: "Nieve moderada", 75: "Nieve fuerte", 77: "Granos de nieve",
    80: "Chubascos leves", 81: "Chubascos moderados", 82: "Chubascos violentos",
    85: "Chubascos de nieve leves", 86: "Chubascos de nieve fuertes",
    95: "Tormenta", 96: "Tormenta con granizo leve", 99: "Tormenta con granizo fuerte",
}

class WeatherAPIClient:
    """Handles asynchronous requests to Open-Meteo."""

    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        
    async def fetch_batch(self, client: httpx.AsyncClient, points: List[Dict[str, Any]], eta_hour: datetime, semaphore: asyncio.Semaphore) -> List[Dict[str, Any]]:
        """Fetches weather for a list of coordinates for the same hour in a single call."""
        eta_hour_str = eta_hour.strftime("%Y-%m-%dT%H:00")
        
        # Open-Meteo allows up to 50 locations per request
        params = {
            "latitude": [p["latitude"] for p in points],
            "longitude": [p["longitude"] for p in points],
            "elevation": [p["elevation"] for p in points],
            "hourly": "temperature_2m,precipitation,wind_speed_10m,weather_code",
            "timezone": "auto",
            "start_hour": eta_hour_str,
            "end_hour": eta_hour_str,
        }
        
        async with semaphore:
            for attempt in range(3):
                try:
                    response = await client.get(self.base_url, params=params, timeout=15.0)
                    response.raise_for_status()
                    data_list = response.json()
                    
                    # If only one location is requested, Open-Meteo returns a dict.
                    # If multiple, it returns a list of dicts.
                    if isinstance(data_list, dict):
                        data_list = [data_list]
                    
                    results = []
                    for i, data in enumerate(data_list):
                        wmo_code = data["hourly"]["weather_code"][0]
                        results.append({
                            "point_id": points[i]["point_id"],
                            "latitude": points[i]["latitude"],
                            "longitude": points[i]["longitude"],
                            "eta_weather_time": datetime.fromisoformat(data["hourly"]["time"][0]),
                            "temperature_2m": data["hourly"]["temperature_2m"][0],
                            "precipitation": data["hourly"]["precipitation"][0],
                            "wind_speed_10m": data["hourly"]["wind_speed_10m"][0],
                            "weather_desc": WMO_CODES_ES.get(wmo_code, "Desconocido")
                        })
                    return results
                except Exception:
                    if attempt < 2:
                        await asyncio.sleep(1 + attempt * 2)
                        continue
            
            # Error fallback
            return [{
                "point_id": p["point_id"],
                "latitude": p["latitude"],
                "longitude": p["longitude"],
                "eta_weather_time": None,
                "temperature_2m": None,
                "precipitation": None,
                "wind_speed_10m": None,
                "weather_desc": "Error de conexión"
            } for p in points]

    async def fetch_route_weather(self, df: pl.DataFrame) -> pl.DataFrame:
        """Groups points by ETA hour and fetches weather in batches."""
        # Add a unique point_id to safely join back later, avoiding cartesian products
        df = df.with_row_index("point_id")
        
        # Add a column for the ETA hour to group by
        df_with_hour = df.with_columns(
            pl.col("eta").dt.truncate("1h").alias("eta_hour")
        )
        
        # Group points by hour
        hour_groups = df_with_hour.group_by("eta_hour", maintain_order=True).all()
        
        semaphore = asyncio.Semaphore(5)  # Back to conservative semaphore as requests are larger
        limits = httpx.Limits(max_connections=5, max_keepalive_connections=2)
        headers = {"User-Agent": "Meteorologia-GPX-Optimizer/1.0 (https://github.com/Chane12/Meteorologia-GPX)"}
        
        async with httpx.AsyncClient(limits=limits, headers=headers) as client:
            tasks = []
            for hour_row in hour_groups.to_dicts():
                eta_hour = hour_row["eta_hour"]
                # Create dicts for each point in this hour
                p_ids = hour_row["point_id"]
                lats = hour_row["latitude"]
                lons = hour_row["longitude"]
                eles = hour_row["elevation"]
                
                points_in_hour = []
                for i in range(len(lats)):
                    points_in_hour.append({
                        "point_id": p_ids[i],
                        "latitude": lats[i],
                        "longitude": lons[i],
                        "elevation": eles[i]
                    })
                
                # Split points_in_hour into chunks of 50 if necessary
                for i in range(0, len(points_in_hour), 50):
                    chunk = points_in_hour[i:i+50]
                    tasks.append(self.fetch_batch(client, chunk, eta_hour, semaphore))
                    
            batch_results = await asyncio.gather(*tasks)
            
        # Flatten the list of lists
        flat_results = [item for sublist in batch_results for item in sublist]
        weather_df_results = pl.DataFrame(flat_results)
        
        # Join the results back based on unique point_id implicitly preventing duplicates
        resulting_df = df.join(
            weather_df_results.drop(["latitude", "longitude"]),
            on="point_id",
            how="left"
        ).drop("point_id")
        
        return resulting_df
