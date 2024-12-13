from datetime import datetime
import pyspark
import pytest

from mlops_demo.feature_engineering.features.dropoff_features import (
    compute_features_fn,
)


@pytest.mark.usefixtures("spark")
def test_dropoff_features_fn(spark):
    data = [(datetime(2022, 1, 10), datetime(2022, 1, 10), 94400, 2, 100)]
    columns = ["tpep_pickup_datetime", "tpep_dropoff_datetime", "dropoff_zip", "trip_distance", "fare_amount"]
    spark_df = spark.createDataFrame(data, columns)
    output_df = compute_features_fn(spark_df, "tpep_pickup_datetime", datetime(2022, 1, 1), datetime(2022, 1, 15))
    assert isinstance(output_df, pyspark.sql.DataFrame)
    assert output_df.count() == 1
