import gpxpy
import polars as pl

class GPXProcessor:
    """Handles parsing of GPX files into Polars DataFrames."""

    @staticmethod
    def parse_to_dataframe(gpx_content: str) -> pl.DataFrame:
        """
        Parses GPX string content and returns a Polars DataFrame with the route points.
        """
        gpx = gpxpy.parse(gpx_content)
        
        points_data = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points_data.append({
                        "latitude": point.latitude,
                        "longitude": point.longitude,
                        "elevation": point.elevation if point.elevation is not None else 0.0,
                        "original_time": point.time if point.time else None 
                    })
        
        if not points_data:
             for route in gpx.routes:
                for point in route.points:
                    points_data.append({
                        "latitude": point.latitude,
                        "longitude": point.longitude,
                        "elevation": point.elevation if point.elevation is not None else 0.0,
                        "original_time": point.time if point.time else None 
                    })

        df = pl.DataFrame(points_data)
        
        if df.is_empty():
            raise ValueError("El archivo GPX no contiene puntos válidos en trk/trkseg o rte.")
            
        # Check if elevation is all zeros (common if missing in GPX)
        if (df["elevation"] == 0.0).all():
            import streamlit as st
            st.sidebar.warning("⚠️ El archivo GPX no contiene datos de elevación. El perfil se mostrará plano.")

        return df
