from pyspark.sql import SparkSession


# Create a new Databricks Connect session. If this fails,
# check that you have configured Databricks Connect correctly.
# See https://docs.databricks.com/dev-tools/databricks-connect.html.
def get_spark_session(*, profile:str|None = None, serverless:bool = True) -> SparkSession:
    """Returns a Databricks Connect session."""
    try:
        from databricks.connect import DatabricksSession

        builder = DatabricksSession.builder
        
        if serverless:
            builder = builder.serverless()
        
        if profile:
            builder = builder.profile(profile)

        return builder.getOrCreate()
    except ImportError:
        return SparkSession.builder.getOrCreate()
