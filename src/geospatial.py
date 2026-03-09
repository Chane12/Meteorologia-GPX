import polars as pl
import numpy as np
from datetime import datetime

class GeospatialEngine:
    """Handles distance calculations and downsampling based on geography."""
    
    EARTH_RADIUS_KM = 6371.0

    @staticmethod
    def haversine_distance(lat1: pl.Expr, lon1: pl.Expr, lat2: pl.Expr, lon2: pl.Expr) -> pl.Expr:
        """Vectorized Haversine formula for Polars."""
        lat1_rad = lat1 * np.pi / 180.0
        lon1_rad = lon1 * np.pi / 180.0
        lat2_rad = lat2 * np.pi / 180.0
        lon2_rad = lon2 * np.pi / 180.0

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (dlat / 2).sin() ** 2 + lat1_rad.cos() * lat2_rad.cos() * (dlon / 2).sin() ** 2
        # Ensure 'a' is within [0, 1] for sqrt
        a_clipped = pl.when(a < 1.0).then(a).otherwise(1.0)
        a_clipped = pl.when(a_clipped > 0.0).then(a_clipped).otherwise(0.0)
        c = 2 * a_clipped.sqrt().arcsin()
        
        return GeospatialEngine.EARTH_RADIUS_KM * c

    @staticmethod
    def calculate_cumulative_distance(df: pl.DataFrame) -> pl.DataFrame:
        """Calculates distance between consecutive points and cumulative distance."""
        if df.height < 2:
            return df.with_columns([
                pl.lit(0.0).alias("distance_step_km"),
                pl.lit(0.0).alias("cumulative_distance_km")
            ])

        df = df.with_columns([
            pl.col("latitude").shift(1).alias("prev_lat"),
            pl.col("longitude").shift(1).alias("prev_lon")
        ])

        df = df.with_columns(
            pl.when(pl.col("prev_lat").is_not_null())
            .then(GeospatialEngine.haversine_distance(
                pl.col("latitude"), pl.col("longitude"), 
                pl.col("prev_lat"), pl.col("prev_lon")
            ))
            .otherwise(0.0)
            .alias("distance_step_km")
        )

        df = df.with_columns(
            pl.col("distance_step_km").cum_sum().alias("cumulative_distance_km")
        ).drop(["prev_lat", "prev_lon"])

        return df

    @staticmethod
    def downsample_by_distance(df: pl.DataFrame, interval_km: float) -> pl.DataFrame:
        """Filters dataframe to keep points roughly at given interval."""
        if "cumulative_distance_km" not in df.columns:
            df = GeospatialEngine.calculate_cumulative_distance(df)
            
        df = df.with_columns(
            (pl.col("cumulative_distance_km") / interval_km).cast(pl.Int32).alias("interval_group")
        )
        
        downsampled = df.group_by("interval_group", maintain_order=True).first()
        
        last_group_original = df.tail(1)["interval_group"][0]
        last_group_downsampled = downsampled.tail(1)["interval_group"][0]
        if last_group_original != last_group_downsampled:
            downsampled = pl.concat([downsampled, df.tail(1)])
            
        return downsampled.drop("interval_group")

    @staticmethod
    def calculate_etas(df: pl.DataFrame, start_time: datetime, avg_speed_kmh: float) -> pl.DataFrame:
        """Calculates expected time of arrival at each point."""
        if "cumulative_distance_km" not in df.columns:
            df = GeospatialEngine.calculate_cumulative_distance(df)
            
        # time in milliseconds = (distance / speed) * 3600 * 1000
        df = df.with_columns(
            (pl.col("cumulative_distance_km") / avg_speed_kmh * 3600 * 1000).cast(pl.Duration("ms")).alias("duration_from_start")
        )
        
        df = df.with_columns(
            (pl.lit(start_time) + pl.col("duration_from_start")).alias("eta")
        )
        
        return df
