# What Is Apache Spark?

Apache Spark is an open-source, distributed engine for large-scale data
processing. You describe *what* you want to compute (filter these rows, join
those tables, aggregate by that key) through a high-level API in Python, SQL,
Scala, Java or R, and Spark works out *how* to run it in parallel across many
machines.

This page explains the problem Spark was built to solve, how it evolved, and
what the pieces of the Spark ecosystem are. The
{doc}`next page <02_spark_runtime_architecture>` looks at what a running
Spark application looks like.

## The Problem: Data That Does Not Fit on One Machine

A laptop can comfortably process a few gigabytes of data with pandas. Once the
data grows to hundreds of gigabytes or terabytes, a single machine runs out of
memory, disk throughput or CPU time. There are two ways out:

- **Scale up**: buy a bigger machine. This gets expensive fast and has a hard
  ceiling.
- **Scale out**: split the data into pieces and process the pieces on many
  ordinary machines at once.

Scaling out brings hard problems of its own. Someone has to split the data,
ship code to where the data lives, collect the partial results, and recover
when one of the machines fails halfway through. Spark exists so that you don't
have to solve those problems yourself for every job.

## A Short History

Spark grew out of a reaction to **Hadoop MapReduce**, the dominant big data
framework before it. It started as a research project in UC Berkeley's
AMPLab, whose authors set out to support "a much wider class of applications
than MapReduce" while keeping its automatic fault tolerance. MapReduce runs a
multi-step computation as a series of separate jobs that each read their input
from, and write their output back to, stable storage, which is inefficient for
*multi-pass* workloads such as iterative machine learning. Spark keeps
intermediate data in memory between steps instead, and rebuilds lost pieces
from their *lineage* when a machine fails
([Apache Spark: Research](https://spark.apache.org/research.html)).

The milestones below come from the Apache Spark project's own announcements
([Apache Spark News](https://spark.apache.org/news/index.html)):

- **2013–2014**: Spark is accepted into the Apache Incubator (June 2013) and
  becomes a top-level Apache project (February 2014).
- **2016, Spark 2.0**: DataFrame and Dataset are unified, `SparkSession`
  becomes the single entry point, and the first, experimental release of
  Structured Streaming ships
  ([Apache Spark: Spark Release 2.0.0](https://spark.apache.org/releases/spark-release-2-0-0.html)).
- **2020, Spark 3.0**: Adaptive Query Execution (AQE) lets Spark re-optimise a
  query while it runs
  ([Apache Spark: Spark Release 3.0.0](https://spark.apache.org/releases/spark-release-3-0-0.html)).
- **2025, Spark 4.0**: ANSI SQL mode becomes the default, the `VARIANT` type
  for semi-structured data is added, and Spark Connect, a client–server
  protocol for talking to Spark remotely, gets a lightweight Python client and
  greatly expanded API coverage
  ([Apache Spark: Spark Release 4.0.0](https://spark.apache.org/releases/spark-release-4-0-0.html)).

Databricks Runtime 19 is powered by Apache Spark 4.2.0
([Databricks Runtime 19](https://docs.databricks.com/aws/en/release-notes/runtime/19)),
and everything in this course targets the Spark 4 line.

## Why Spark Is Fast

Three design decisions account for most of Spark's speed:

1. **In-memory processing.** Intermediate results stay in memory between
   steps instead of being written to stable storage after every one
   ([Apache Spark: Research](https://spark.apache.org/research.html)).
2. **Lazy evaluation and whole-query optimisation.** Transformations don't
   compute their results right away; Spark only remembers them, and computes
   them when an action needs a result
   ([Apache Spark: RDD Programming Guide](https://spark.apache.org/docs/latest/rdd-programming-guide.html)).
   Because the DataFrame and SQL APIs tell Spark the structure of both the
   data and the computation, its optimiser (Catalyst) can use that extra
   information to rewrite the whole query, for example by reordering filters
   and pruning unused columns
   ([Apache Spark: Spark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)).
   See
   {doc}`Introduction to DataFrames <../02_spark_dataframes_and_sql/01_introduction_to_dataframes>`
   for how this looks from the API.
3. **Native execution on Databricks.** Photon is the Databricks-native
   vectorised query engine. It replaces the JVM-based Spark SQL execution
   engine with a native C++ runtime, and it works with existing Apache Spark
   code with no changes. Catalyst still plans the query; operations Photon
   doesn't support fall back to the regular Spark engine
   ([What is Photon?](https://docs.databricks.com/aws/en/compute/photon)).

## The Spark Ecosystem

Spark is a single engine with several libraries on top of it. Everything in
this course goes through the top layer of the diagram below.

```mermaid
:caption: The Spark stack. Every high-level API compiles down to the same engine.
:align: center

graph TD
    subgraph APIs[High-level APIs]
        SQL[Spark SQL]
        DF[DataFrame API]
        SS[Structured Streaming]
        PS[pandas API on Spark]
        ML[MLlib]
    end
    APIs --> Catalyst[Catalyst optimizer]
    Catalyst --> Core[Spark Core execution engine]
    Core --> CM[Cluster manager]
```

- **Spark SQL and DataFrames**: the structured API you will use for almost
  everything. Whether you write SQL or DataFrame code, the same execution
  engine computes the result
  ([Apache Spark: Spark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)).
- **Structured Streaming**: the DataFrame API applied to continuously
  arriving data, which Databricks describes as a near real-time processing
  engine
  ([Apache Spark overview](https://docs.databricks.com/aws/en/spark/)).
- **pandas API on Spark**: pandas-equivalent APIs that run on Spark, for when
  pandas code has to scale beyond one machine
  ([Pandas API on Spark](https://docs.databricks.com/aws/en/pandas/pandas-on-spark)).
- **MLlib**: distributed machine learning
  ([Apache Spark overview](https://docs.databricks.com/aws/en/spark/)).
- **Spark Core**: task scheduling, memory management and fault recovery. It
  also exposes the low-level **RDD** (Resilient Distributed Dataset) API that
  the earliest versions of Spark were built around
  ([Apache Spark: Research](https://spark.apache.org/research.html)).

:::{admonition} Note: Where RDDs Fit in Today
:class: note

Unlike the RDD API, the DataFrame and SQL APIs give Spark the structure of
the data and the computation, which it uses for extra optimisations
([Apache Spark: Spark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)).
On Databricks serverless compute, which this course uses, only Spark Connect
APIs are supported and the RDD APIs are not
([Serverless compute limitations](https://docs.databricks.com/aws/en/compute/serverless/limitations#language-and-api-support)).
:::

## Spark on Databricks

Apache Spark is the technology powering compute clusters and SQL warehouses
in Databricks
([Apache Spark overview](https://docs.databricks.com/aws/en/spark/)). When you
run Spark on Databricks you get:

- **Managed compute.** Either *serverless* compute, which Databricks
  provisions and scales for you, or *classic* compute, which you configure
  yourself
  ([Compute](https://docs.databricks.com/aws/en/compute/)).
- **The Databricks Runtime**: Apache Spark plus Databricks features such as
  Photon, which is enabled on serverless compute and SQL warehouses and on by
  default on classic compute
  ([What is Photon?](https://docs.databricks.com/aws/en/compute/photon)).
- **Delta Lake** as the default format: unless otherwise specified, all
  tables on Databricks are Delta Lake tables
  ([What is Delta Lake?](https://docs.databricks.com/aws/en/delta/)).
- **Unity Catalog** for governance: tables, views and volumes are addressed by
  a three-level name, `catalog.schema.object`
  ([What is Unity Catalog?](https://docs.databricks.com/aws/en/data-governance/unity-catalog/)),
  and files in volumes live under
  `/Volumes/<catalog>/<schema>/<volume>/`
  ([What are Unity Catalog volumes?](https://docs.databricks.com/aws/en/volumes/)).

## When to Use Spark, and the Alternatives

Spark pays off when the data or the computation is too big for one machine.
For small data, its planning and coordination overhead buys you nothing.

| Tool | Runs on | Choose it when |
| --- | --- | --- |
| pandas | One machine (on Databricks, the driver) | The data fits comfortably in memory and you need its library ecosystem |
| pandas API on Spark | A Spark cluster | You have pandas code that now has to scale out |
| PySpark DataFrames and Spark SQL | A Spark cluster | The default for data engineering on Databricks, and the subject of this course |
| SQL warehouse | Databricks compute for SQL | The workload is SQL and BI queries only |

The trade-offs come straight from the documentation: pandas does not scale out
to big data, which is the gap pandas API on Spark fills
([Pandas API on Spark](https://docs.databricks.com/aws/en/pandas/pandas-on-spark)),
and SQL warehouses are compute optimised for SQL queries, analytics and
business intelligence
([Compute](https://docs.databricks.com/aws/en/compute/#sql-warehouses)).

## Common Mistakes

- **Programming against RDDs.** Old tutorials start with `sc.parallelize`
  and `rdd.map`. On serverless compute the RDD APIs are not supported
  ([Serverless compute limitations](https://docs.databricks.com/aws/en/compute/serverless/limitations#language-and-api-support)),
  and Photon doesn't accelerate RDD code either
  ([What is Photon?](https://docs.databricks.com/aws/en/compute/photon)).
  Express the same logic with DataFrames or SQL.
- **Pulling a big dataset into pandas.** `df.toPandas()` collects every record
  of the DataFrame to the driver program, even with Arrow enabled, so it should
  be used on a small subset of the data
  ([Convert between PySpark and pandas DataFrames](https://docs.databricks.com/aws/en/pandas/pyspark-pandas-conversion#example)).
  Filter and aggregate in Spark first, then convert the small result.
- **Expecting Photon to speed up everything.** Photon doesn't support UDFs,
  RDD APIs or Dataset APIs, and queries that normally finish in under two
  seconds see little benefit
  ([What is Photon?](https://docs.databricks.com/aws/en/compute/photon)).
  Prefer built-in functions over UDFs when performance matters.

How your Python process on a laptop ends up driving Spark on Databricks is
the subject of {doc}`Spark Runtime Architecture <02_spark_runtime_architecture>`.

## Resources

- [Apache Spark documentation (Apache Spark)](https://spark.apache.org/docs/latest/)
- [Apache Spark overview (Databricks)](https://docs.databricks.com/aws/en/spark/)
- [PySpark on Databricks (Databricks)](https://docs.databricks.com/aws/en/pyspark/)
