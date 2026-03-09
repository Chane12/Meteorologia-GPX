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
        
    async def fetch_single_point(self, client: httpx.AsyncClient, lat: float, lon: float, eta: datetime, semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """Fetches weather for a single coordinate and extracts the hourly value closest to ETA."""
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,precipitation,wind_speed_10m,weather_code",
            "timezone": "auto",
        }
        
        async with semaphore:
            for attempt in range(3):
                try:
                    response = await client.get(self.base_url, params=params, timeout=15.0)
                    response.raise_for_status()
                    data = response.json()
                    
                    hourly_times = [datetime.fromisoformat(t) for t in data["hourly"]["time"]]
                    eta_naive = eta.replace(tzinfo=None) if eta.tzinfo else eta
                    
                    closest_idx = 0
                    min_diff = float('inf')
                    
                    for i, t in enumerate(hourly_times):
                        t_naive = t.replace(tzinfo=None) if t.tzinfo else t
                        diff = abs((t_naive - eta_naive).total_seconds())
                        if diff < min_diff:
                            min_diff = diff
                            closest_idx = i
                            
                    wmo_code = data["hourly"]["weather_code"][closest_idx]
                    
                    return {
                        "latitude": lat,
                        "longitude": lon,
                        "eta_weather_time": hourly_times[closest_idx],
                        "temperature_2m": data["hourly"]["temperature_2m"][closest_idx],
                        "precipitation": data["hourly"]["precipitation"][closest_idx],
                        "wind_speed_10m": data["hourly"]["wind_speed_10m"][closest_idx],
                        "weather_desc": WMO_CODES_ES.get(wmo_code, "Desconocido")
                    }
                except (httpx.HTTPStatusError, httpx.RequestError) as e:
                    if attempt < 2:
                        await asyncio.sleep(1 + attempt * 2)
                        continue
                    else:
                        break
                except Exception:
                    break
                    
            return {
                "latitude": lat,
                "longitude": lon,
                "eta_weather_time": None,
                "temperature_2m": None,
                "precipitation": None,
                "wind_speed_10m": None,
                "weather_desc": "Error de conexión"
            }

    async def fetch_route_weather(self, df: pl.DataFrame) -> pl.DataFrame:
        """Takes a downsampled dataframe and fetches weather concurrently."""
        points = df.select(["latitude", "longitude", "eta"]).to_dicts()
        
        semaphore = asyncio.Semaphore(5)  # Limitar concurrencia para evitar bloqueos
        
        async with httpx.AsyncClient(limits=httpx.Limits(max_connections=5)) as client:
            tasks = []
            for point in points:
                tasks.append(self.fetch_single_point(client, point["latitude"], point["longitude"], point["eta"], semaphore))
                
            results = await asyncio.gather(*tasks)
            
        weather_df = pl.DataFrame(results)
        
        resulting_df = df.hstack(weather_df.select(
            ["eta_weather_time", "temperature_2m", "precipitation", "wind_speed_10m", "weather_desc"]
        ))
        
        return resulting_df
