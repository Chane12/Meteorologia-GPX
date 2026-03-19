import pytest
import polars as pl
from meteorologia_gpx.gpx_processor import GPXProcessor

def test_parse_valid_track_gpx():
    gpx_content = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Pytest" xmlns="http://www.topografix.com/GPX/1/1">
    <trk>
        <name>Test Track</name>
        <trkseg>
            <trkpt lat="40.4168" lon="-3.7038">
                <ele>667.0</ele>
                <time>2024-03-19T10:00:00Z</time>
            </trkpt>
            <trkpt lat="40.4170" lon="-3.7040">
                <ele>668.0</ele>
                <time>2024-03-19T10:01:00Z</time>
            </trkpt>
        </trkseg>
    </trk>
</gpx>"""
    df = GPXProcessor.parse_to_dataframe(gpx_content)
    assert isinstance(df, pl.DataFrame)
    assert df.height == 2
    assert "latitude" in df.columns
    assert "longitude" in df.columns
    assert df["latitude"][0] == 40.4168

def test_parse_valid_route_gpx():
    gpx_content = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Pytest" xmlns="http://www.topografix.com/GPX/1/1">
    <rte>
        <name>Test Route</name>
        <rtept lat="40.4168" lon="-3.7038">
            <ele>667.0</ele>
        </rtept>
        <rtept lat="40.4170" lon="-3.7040">
            <ele>668.0</ele>
        </rtept>
    </rte>
</gpx>"""
    df = GPXProcessor.parse_to_dataframe(gpx_content)
    assert df.height == 2
    assert df["latitude"][0] == 40.4168

def test_parse_empty_gpx():
    gpx_content = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Pytest" xmlns="http://www.topografix.com/GPX/1/1">
</gpx>"""
    with pytest.raises(ValueError, match="El archivo GPX no contiene puntos válidos."):
        GPXProcessor.parse_to_dataframe(gpx_content)
