import polars as pl
import numpy as np
from datetime import datetime, timedelta
from meteorologia_gpx.geospatial import GeospatialEngine

def test_haversine_distance():
    # Madrid to Barcelona (roughly)
    lat1, lon1 = 40.4168, -3.7038
    lat2, lon2 = 41.3851, 2.1734
    
    # Create simple expressions for testing
    df = pl.DataFrame({"lat1": [lat1], "lon1": [lon1], "lat2": [lat2], "lon2": [lon2]})
    result = df.select(
        GeospatialEngine.haversine_distance(
            pl.col("lat1"), pl.col("lon1"), pl.col("lat2"), pl.col("lon2")
        ).alias("distance")
    )
    
    distance = result["distance"][0]
    # Madrid-Barcelona is ~505km
    assert 500 < distance < 510

def test_calculate_cumulative_distance():
    df = pl.DataFrame({
        "latitude": [40.0, 40.0, 41.0],
        "longitude": [0.0, 1.0, 1.0]
    })
    
    df_result = GeospatialEngine.calculate_cumulative_distance(df)
    assert "cumulative_distance_km" in df_result.columns
    assert df_result["cumulative_distance_km"][0] == 0.0
    assert df_result["cumulative_distance_km"][1] > 0
    assert df_result["cumulative_distance_km"][2] > df_result["cumulative_distance_km"][1]

def test_downsample_by_distance():
    # Points every ~111km (1 degree lat)
    df = pl.DataFrame({
        "latitude": [40.0, 41.0, 42.0, 43.0, 44.0],
        "longitude": [0.0, 0.0, 0.0, 0.0, 0.0]
    })
    
    # Downsample every 150km
    df_down = GeospatialEngine.downsample_by_distance(df, 150.0)
    # Start point (0km), 42.0 (approx 222km), 44.0 (approx 444km)
    # Actually the logic is based on interval_group = dist // interval
    assert df_down.height < df.height
    assert df_down["latitude"][0] == 40.0
    assert df_down["latitude"].to_list()[-1] == 44.0 # Should keep last point

def test_calculate_etas():
    df = pl.DataFrame({
        "latitude": [40.0, 41.0],
        "longitude": [0.0, 0.0]
    })
    start_time = datetime(2024, 3, 19, 10, 0, 0)
    avg_speed = 100.0 # km/h
    
    df_eta = GeospatialEngine.calculate_etas(df, start_time, avg_speed)
    assert "eta" in df_eta.columns
    assert df_eta["eta"][0] == start_time
    assert df_eta["eta"][1] > start_time
