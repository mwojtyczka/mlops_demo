# Databricks notebook source
df = spark.sql('SELECT * FROM delta.`dbfs:/databricks-datasets/nyctaxi-with-zipcodes/subsampled`')

# COMMAND ----------

import pyspark.sql.functions as F
from datetime import timedelta, timezone
import math
import mlflow.pyfunc
import pyspark.sql.functions as F
from pyspark.sql.types import IntegerType

def rounded_unix_timestamp(dt, num_minutes=15):
    """
    Ceilings datetime dt to interval num_minutes, then returns the unix timestamp.
    """
    nsecs = dt.minute * 60 + dt.second + dt.microsecond * 1e-6
    delta = math.ceil(nsecs / (60 * num_minutes)) * (60 * num_minutes) - nsecs
    return int((dt + timedelta(seconds=delta)).replace(tzinfo=timezone.utc).timestamp())

rounded_unix_timestamp_udf = F.udf(rounded_unix_timestamp, IntegerType())

def rounded_taxi_data(taxi_data_df):
    # Round the taxi data timestamp to 15 and 30 minute intervals so we can join with the pickup and dropoff features
    # respectively.
    taxi_data_df = (
        taxi_data_df.withColumn(
            "rounded_pickup_datetime",
            F.to_timestamp(
                rounded_unix_timestamp_udf(
                    taxi_data_df["tpep_pickup_datetime"], F.lit(15)
                )
            ),
        )
        .withColumn(
            "rounded_dropoff_datetime",
            F.to_timestamp(
                rounded_unix_timestamp_udf(
                    taxi_data_df["tpep_dropoff_datetime"], F.lit(30)
                )
            ),
        )
        .drop("tpep_pickup_datetime")
        .drop("tpep_dropoff_datetime")
    )
    taxi_data_df.createOrReplaceTempView("taxi_data")
    return taxi_data_df


data = rounded_taxi_data(df)

# COMMAND ----------

data.write.format("delta").mode("overwrite").saveAsTable("qa_mlops_demo.marcin_wojtyczka.feature_store_inference_input")

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from qa_mlops_demo.marcin_wojtyczka.feature_store_inference_input

# COMMAND ----------

