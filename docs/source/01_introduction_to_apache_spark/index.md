# Introduction to Apache Spark

This chapter takes you from "what is Spark?" to writing a small but complete
ETL pipeline with the DataFrame API. It assumes you have a working Databricks
Connect session, as set up in
{doc}`Setting Up Databricks Connect <../00_getting_started/01_setting_up_databricks_connect>`.
Every code example on these pages runs against Databricks serverless compute
through that session.

The material targets **Apache Spark 4.x as shipped on Databricks**:
Databricks Runtime 19 is powered by Apache Spark 4.2.0
([Databricks Runtime 19](https://docs.databricks.com/aws/en/release-notes/runtime/19)),
and serverless environment version 6 ships Databricks Connect 19
([Serverless environment version 6](https://docs.databricks.com/aws/en/release-notes/serverless/environment-version/six)).
Where Databricks behaves differently from open-source Spark (for example,
serverless compute supports only Spark Connect APIs), the pages call it out.

The chapter is organised into four sections:

- {doc}`Apache Spark Runtime Architecture <01_apache_spark_runtime_architecture/index>`:
  what Spark is, why it exists, and how a Spark application is laid out
  across a driver, executors and, on Databricks, a Spark Connect client.
- {doc}`Spark DataFrames and SQL <02_spark_dataframes_and_sql/index>`: the
  DataFrame abstraction, lazy evaluation, and reading and writing data with
  Unity Catalog tables and volumes.
- {doc}`Distributed Systems Programming Fundamentals <03_distributed_systems_programming_fundamentals/index>`:
  partitions, shuffles, jobs, stages and tasks, and the performance habits
  that come from understanding them.
- {doc}`ETL with the DataFrame API <04_etl_with_the_dataframe_api/index>`:
  putting it all together into an extract, transform, load pipeline.

```{toctree}
:maxdepth: 2
:hidden:

01_apache_spark_runtime_architecture/index
02_spark_dataframes_and_sql/index
03_distributed_systems_programming_fundamentals/index
04_etl_with_the_dataframe_api/index
```
