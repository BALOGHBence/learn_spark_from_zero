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

Scaling out is the approach that won, but it brings hard problems of its own.
Someone has to split the data, ship code to where the data lives, collect the
partial results, and recover when one of the machines inevitably fails
halfway through. Spark exists so that you don't have to solve those problems
yourself for every job.

## A Short History

Spark grew out of a reaction to **Hadoop MapReduce**, the dominant big data
framework of the late 2000s. MapReduce forced every computation into a rigid
map-then-reduce shape and wrote intermediate results to disk between every
step. That was robust, but slow for multi-step pipelines, and painfully slow
for iterative workloads such as machine learning, which pass over the same
data many times.

- **2009**: Matei Zaharia starts Spark as a research project at UC Berkeley's
  AMPLab. The central idea is to keep intermediate data **in memory** and to
  plan whole multi-step computations as a graph instead of a chain of
  independent MapReduce jobs.
- **2013–2014**: Spark is donated to the Apache Software Foundation and
  becomes a top-level Apache project. The original authors found Databricks.
- **2016, Spark 2.0**: the DataFrame and Dataset APIs become the primary way
  to program Spark, and Structured Streaming arrives.
- **2020, Spark 3.0**: Adaptive Query Execution (AQE) lets Spark re-optimise a
  query while it runs, using statistics gathered along the way.
- **2025, Spark 4.0**: ANSI SQL mode becomes the default, the `VARIANT` type
  for semi-structured data is added, and **Spark Connect**, a client–server
  protocol for talking to Spark remotely, becomes a first-class way to use
  Spark.

At the time of writing, Databricks Runtime 19 ships Apache Spark 4.2.0, and
everything in this course targets the Spark 4 line.

## Why Spark Is Fast

Three design decisions account for most of Spark's speed advantage over the
systems that came before it:

1. **In-memory processing.** Intermediate results stay in executor memory
   where possible instead of being written to disk between every step.
2. **Lazy evaluation and whole-query optimisation.** Spark does not execute a
   transformation the moment you write it. It records the transformations,
   and only when you ask for a result does it hand the complete plan to an
   optimiser (Catalyst), which can reorder filters, prune unused columns and
   pick join strategies for the query as a whole. See
   {doc}`Introduction to DataFrames <../02_spark_dataframes_and_sql/01_introduction_to_dataframes>`
   for how this looks from the API.
3. **Efficient execution.** Spark generates compact code for whole stages of
   a query and stores data in a compact binary format. On Databricks, the
   **Photon** engine goes further: it is a native, vectorised execution engine
   that runs compatible DataFrame and SQL operations without changes to your
   code.

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
  everything. SQL queries and DataFrame code produce the same plans and run
  equally fast.
- **Structured Streaming**: the same DataFrame API applied to unbounded,
  continuously arriving data.
- **pandas API on Spark**: a pandas-compatible API that runs on Spark, useful
  for scaling existing pandas code.
- **MLlib**: distributed machine learning algorithms and feature pipelines.
- **Spark Core**: task scheduling, memory management and fault recovery. It
  also exposes the low-level **RDD** (Resilient Distributed Dataset) API that
  the earliest versions of Spark were built around.

:::{admonition} Note: Where RDDs Fit in Today
:class: note

RDDs are still what Spark uses internally, but you should not program against
them directly. The DataFrame API is easier to use and, because Catalyst can
see inside it, usually much faster. On Databricks serverless compute (which
this course uses), the RDD API is not available at all: only DataFrame and
SQL APIs are supported.
:::

## Spark on Databricks

Databricks is a managed platform built by Spark's original creators. When you
run Spark on Databricks you get:

- **Managed compute.** Either *serverless* compute, which Databricks
  provisions and scales for you, or *classic* compute, where you choose the
  machine types and cluster size yourself.
- **The Databricks Runtime**: Apache Spark plus performance features such as
  Photon, and pre-installed libraries.
- **Delta Lake** as the default table format: every table you create with
  `saveAsTable` is a Delta table unless you say otherwise.
- **Unity Catalog** for governance: tables are addressed by a three-level
  name, `catalog.schema.table`, and files live in *volumes* under
  `/Volumes/<catalog>/<schema>/<volume>/`.

How your Python process on a laptop ends up driving Spark on Databricks is
the subject of {doc}`Spark Runtime Architecture <02_spark_runtime_architecture>`.

## Resources

- [Apache Spark documentation](https://spark.apache.org/docs/latest/)
- [Apache Spark on Databricks](https://docs.databricks.com/aws/en/spark/)
- [PySpark on Databricks](https://docs.databricks.com/aws/en/pyspark/)
