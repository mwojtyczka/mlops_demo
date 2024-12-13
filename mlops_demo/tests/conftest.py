# pylint: disable=redefined-outer-name
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark(request: pytest.FixtureRequest):
    """fixture for creating a spark session
    Args:
        request: pytest.FixtureRequest object
    """
    spark = SparkSession.builder.master("local[1]").appName("pytest-pyspark-local-testing").getOrCreate()
    request.addfinalizer(spark.stop)

    return spark
