import pytest
import httpx
import asyncio
import polars as pl
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from meteorologia_gpx.weather_client import WeatherAPIClient

@pytest.mark.asyncio
async def test_fetch_single_point_success():
    client = WeatherAPIClient()
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "hourly": {
            "time": ["2024-03-19T10:00"],
            "temperature_2m": [20.5],
            "precipitation": [0.0],
            "wind_speed_10m": [15.0],
            "weather_code": [0]
        }
    }
    mock_response.raise_for_status.return_value = None
    
    mock_async_client = AsyncMock(spec=httpx.AsyncClient)
    mock_async_client.get.return_value = mock_response
    
    semaphore = asyncio.Semaphore(1)
    eta = datetime(2024, 3, 19, 10, 0)
    
    result = await client.fetch_single_point(mock_async_client, 40.0, -3.0, 600.0, eta, semaphore)
    
    assert result["temperature_2m"] == 20.5
    assert result["weather_desc"] == "Despejado"
    assert result["latitude"] == 40.0

@pytest.mark.asyncio
async def test_fetch_single_point_error():
    client = WeatherAPIClient()
    mock_async_client = AsyncMock(spec=httpx.AsyncClient)
    mock_async_client.get.side_effect = httpx.RequestError("Connection failed")
    
    semaphore = asyncio.Semaphore(1)
    eta = datetime(2024, 3, 19, 10, 0)
    
    # We expect it to retry 3 times and then return Error dict
    result = await client.fetch_single_point(mock_async_client, 40.0, -3.0, 600.0, eta, semaphore)
    
    assert result["weather_desc"] == "Error de conexión"
    assert result["temperature_2m"] is None

@pytest.mark.asyncio
async def test_fetch_route_weather():
    client = WeatherAPIClient()
    df = pl.DataFrame({
        "latitude": [40.0],
        "longitude": [-3.0],
        "elevation": [600.0],
        "eta": [datetime(2024, 3, 19, 10, 0)]
    })
    
    mock_result = {
        "latitude": 40.0,
        "longitude": -3.0,
        "eta_weather_time": datetime(2024, 3, 19, 10, 0),
        "temperature_2m": 20.5,
        "precipitation": 0.0,
        "wind_speed_10m": 15.0,
        "weather_desc": "Despejado"
    }
    
    with patch.object(WeatherAPIClient, 'fetch_single_point', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_result
        
        result_df = await client.fetch_route_weather(df)
        
        assert result_df.height == 1
        assert "temperature_2m" in result_df.columns
        assert result_df["temperature_2m"][0] == 20.5
