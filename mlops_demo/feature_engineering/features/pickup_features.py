"""
This sample module contains  features logic that can be used to generate and populate tables in Feature Store.
You should plug in your own features computation logic in the compute_features_fn method below.
"""

import pyspark.sql.functions as F
from pyspark.sql.types import FloatType, IntegerType, StringType, TimestampType


@F.udf(returnType=StringType())
def _feature_partition_id(data_frame):
    # datetime -> "YYYY-MM"
    return f"{data_frame.year:04d}-{data_frame.month:02d}"


def _feature_filter_df_by_ts(data_frame, ts_column, start_date, end_date):
    if ts_column and start_date:
        data_frame = data_frame.filter(F.col(ts_column) >= start_date)
    if ts_column and end_date:
        data_frame = data_frame.filter(F.col(ts_column) < end_date)
    return data_frame


def compute_features_fn(input_df, timestamp_column, start_date, end_date):
    """Contains logic to compute features.

    Given an input dataframe and time ranges, this function should compute features, populate an output dataframe and
    return it. This method will be called from a  Feature Store pipeline job and the output dataframe will be written
    to a Feature Store table. You should update this method with your own feature computation logic.

    The timestamp_column, start_date, end_date args are optional but strongly recommended for time-series based
    features.

    TODO: Update and adapt the sample code for your use case

    Args:
        input_df (DataFrame): The input DataFrame containing raw data.
        timestamp_column (str): The name of the timestamp column.
        start_date (datetime): The start date for filtering the input DataFrame.
        end_date (datetime): The end date for filtering the input DataFrame.

    Returns:
        DataFrame: The output DataFrame containing computed features.
    """
    data_frame = _feature_filter_df_by_ts(input_df, timestamp_column, start_date, end_date)
    pickupzip_features = (
        data_frame.groupBy(
            "pickup_zip", F.window(timestamp_column, "1 hour", "15 minutes")
        )  # 1 hour window, sliding every 15 minutes
        .agg(
            F.mean("fare_amount").alias("mean_fare_window_1h_pickup_zip"),
            F.count("*").alias("count_trips_window_1h_pickup_zip"),
        )
        .select(
            F.col("pickup_zip").alias("zip"),
            F.unix_timestamp(F.col("window.end")).alias(timestamp_column).cast(TimestampType()),
            _feature_partition_id(F.to_timestamp(F.col("window.end"))).alias("yyyy_mm"),
            F.col("mean_fare_window_1h_pickup_zip").cast(FloatType()),
            F.col("count_trips_window_1h_pickup_zip").cast(IntegerType()),
        )
    )
    return pickupzip_features
