"""
This sample module contains features logic that can be used to generate and populate tables in Feature Store. 
You should plug in your own features computation logic in the compute_features_fn method below.
"""

import pyspark.sql.functions as F
from pyspark.sql.types import IntegerType, StringType, TimestampType
from pytz import timezone


@F.udf(returnType=IntegerType())
def _is_weekend(data_frame):
    time_zone = "America/New_York"
    return int(data_frame.astimezone(timezone(time_zone)).weekday() >= 5)  # 5 = Saturday, 6 = Sunday


@F.udf(returnType=StringType())
def _partition_id(data_frame):
    # datetime -> "YYYY-MM"
    return f"{data_frame.year:04d}-{data_frame.month:02d}"


def _filter_df_by_ts(data_frame, ts_column, start_date, end_date):
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
    data_frame = _filter_df_by_ts(input_df, timestamp_column, start_date, end_date)
    dropoffzip_features = (
        data_frame.groupBy("dropoff_zip", F.window(timestamp_column, "30 minute"))
        .agg(F.count("*").alias("count_trips_window_30m_dropoff_zip"))
        .select(
            F.col("dropoff_zip").alias("zip"),
            F.unix_timestamp(F.col("window.end")).alias(timestamp_column).cast(TimestampType()),
            _partition_id(F.to_timestamp(F.col("window.end"))).alias("yyyy_mm"),
            F.col("count_trips_window_30m_dropoff_zip").cast(IntegerType()),
            _is_weekend(F.col("window.end")).alias("dropoff_is_weekend"),  # pylint: disable=no-member
        )
    )
    return dropoffzip_features
