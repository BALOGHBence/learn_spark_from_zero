# Stream Processing and Analysis

The previous chapters processed data at rest: a query read a complete table
and produced a result. This chapter is about data in motion. It introduces
stream processing, shows how Spark's Structured Streaming turns the
DataFrame API from
{doc}`Developing Applications with Apache Spark <../02_developing_applications_with_apache_spark/index>`
into incremental, fault-tolerant pipelines, and ends with real-time mode for
millisecond latency.

Like the previous chapter, each page is a Jupyter notebook that runs against
Databricks serverless compute through the session set up in
{doc}`Setting Up Databricks Connect <../00_getting_started/01_setting_up_databricks_connect>`.
On serverless compute Databricks recommends the `availableNow` trigger
([Serverless compute limitations](https://docs.databricks.com/aws/en/compute/serverless/limitations#streaming-limitations)),
so each query processes the data that has arrived and then stops. The
notebooks simulate arriving data by adding files and rows between runs, and
create their own Unity Catalog volume and tables in `workspace.default`,
which they remove again at the end.

- {doc}`Introduction to Stream Processing <01_introduction_to_stream_processing>`:
  bounded and unbounded data, event time and processing time, processing
  models, delivery guarantees, and a first incremental query.
- {doc}`Spark Structured Streaming <02_spark_structured_streaming>`: the
  programming model, sources including Auto Loader, sinks, output modes,
  triggers, checkpoints and monitoring, built into a streaming medallion
  pipeline.
- {doc}`Stream Aggregations, Windows and Watermarks <03_stream_aggregations_windows_and_watermarks>`:
  state, tumbling, sliding and session windows, watermarks and late data,
  de-duplication, and stream-stream joins.
- {doc}`Real-Time Mode in Structured Streaming <04_real_time_mode_in_structured_streaming>`:
  how real-time mode removes the micro-batch latency floor, its
  requirements, supported operations, cluster sizing and monitoring.

```{toctree}
:maxdepth: 1
:hidden:

01_introduction_to_stream_processing
02_spark_structured_streaming
03_stream_aggregations_windows_and_watermarks
04_real_time_mode_in_structured_streaming
```
