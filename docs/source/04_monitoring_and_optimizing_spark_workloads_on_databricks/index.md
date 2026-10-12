# Monitoring and Optimizing Spark Workloads on Databricks

The previous chapters were about writing Spark code that produces the right
result, in batch with
{doc}`Developing Applications with Apache Spark <../02_developing_applications_with_apache_spark/index>`
and incrementally with
{doc}`Stream Processing and Analysis <../03_stream_processing_and_analysis/index>`.
This chapter is about running that code efficiently: seeing what a workload
does on Databricks, understanding the Delta Lake storage layer it reads and
writes, and making it faster and cheaper.

Each page is a Jupyter notebook that runs against Databricks serverless
compute through the session set up in
{doc}`Setting Up Databricks Connect <../00_getting_started/01_setting_up_databricks_connect>`.
The notebooks create their own tables in `workspace.default` and drop them
again at the end.

- {doc}`Spark and Databricks <01_spark_and_databricks>`: what Databricks
  changes about how Spark runs, reading query plans, the query profile and
  the Spark UI, query history and billing system tables, and observed
  metrics.
- {doc}`Using Apache Spark with Delta Lake <02_using_apache_spark_with_delta_lake>`:
  the transaction log, `UPDATE`, `DELETE` and `MERGE`, schema enforcement
  and constraints, time travel, the change data feed, and table maintenance.
- {doc}`Optimizing Apache Spark <03_optimizing_apache_spark>`: column
  pruning, data skipping and liquid clustering, file sizes, join strategies,
  data skew, Photon and caching, with a checklist to finish.

```{toctree}
:maxdepth: 1
:hidden:

01_spark_and_databricks
02_using_apache_spark_with_delta_lake
03_optimizing_apache_spark
```
