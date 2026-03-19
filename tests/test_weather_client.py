import pytest
import httpx
import asyncio
import polars as pl
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from meteorologia_gpx.weather_client import WeatherAPIClient

@pytest.mark.asyncio
async def test_fetch_batch_success():
    client = WeatherAPIClient()
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = [{
        "hourly": {
            "time": ["2024-03-19T10:00"],
            "temperature_2m": [20.5],
            "precipitation": [0.0],
            "wind_speed_10m": [15.0],
            "weather_code": [0]
        }
    }]
    mock_response.raise_for_status.return_value = None
    
    mock_async_client = AsyncMock(spec=httpx.AsyncClient)
    mock_async_client.get.return_value = mock_response
    
    semaphore = asyncio.Semaphore(1)
    eta_hour = datetime(2024, 3, 19, 10, 0)
    points = [{"latitude": 40.0, "longitude": -3.0, "elevation": 600.0}]
    
    results = await client.fetch_batch(mock_async_client, points, eta_hour, semaphore)
    
    assert len(results) == 1
    assert results[0]["temperature_2m"] == 20.5
    assert results[0]["weather_desc"] == "Despejado"

@pytest.mark.asyncio
async def test_fetch_route_weather_batching():
    client = WeatherAPIClient()
    df = pl.DataFrame({
        "latitude": [40.0, 40.1],
        "longitude": [-3.0, -3.1],
        "elevation": [600.0, 610.0],
        "eta": [datetime(2024, 3, 19, 10, 0), datetime(2024, 3, 19, 10, 30)]
    })
    
    mock_results = [
        {
            "latitude": 40.0,
            "longitude": -3.0,
            "eta_weather_time": datetime(2024, 3, 19, 10, 0),
            "temperature_2m": 20.5,
            "precipitation": 0.0,
            "wind_speed_10m": 15.0,
            "weather_desc": "Despejado"
        },
        {
            "latitude": 40.1,
            "longitude": -3.1,
            "eta_weather_time": datetime(2024, 3, 19, 10, 0),
            "temperature_2m": 21.0,
            "precipitation": 0.1,
            "wind_speed_10m": 12.0,
            "weather_desc": "Lluvia leve"
        }
    ]
    
    with patch.object(WeatherAPIClient, 'fetch_batch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_results
        
        result_df = await client.fetch_route_weather(df)
        
        # Check that it was called once because both points are in the same hour (10:00)
        assert mock_fetch.call_count == 1
        assert result_df.height == 2
        assert result_df["temperature_2m"][0] == 20.5
        assert result_df["temperature_2m"][1] == 21.0
