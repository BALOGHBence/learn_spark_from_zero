# Databricks Certified Associate Developer for Apache Spark — Exam Outline

Transcribed verbatim from
`resources/databricks-certified-associate-developer-apache-spark-exam-guide-oct-2025.pdf`
(covers the exam live as of Oct 30, 2025). The guide asks candidates to re-check
it two weeks before the exam; if the PDF in `resources/` is replaced with a newer
version, update this file from it.

## About the Exam

- Number of items: 45 scored multiple-choice questions
- Time limit: 90 minutes
- Test aides: none, including API documentation
- Code language: Python ("complete basic Spark DataFrame tasks using Python")
- Exams may include unscored questions that are not identified on the form
- Section weights: not in the guide, but published on the [certification page](https://www.databricks.com/learn/certification/apache-spark-developer-associate): Section 1 20%, Section 2 20%, Section 3 30%, Section 4 10%, Section 5 10%, Section 6 5%, Section 7 5%. The `mock-exam` skill and the mock exam app build their blueprint from these.

## Section 1: Apache Spark Architecture and Components

- Identify the advantages and challenges of implementing Spark.
- Identify the role of core components of Apache Spark™'s Architecture, including cluster, driver node, worker nodes/executors, CPU cores, and memory.
- Describe the architecture of Apache Spark™, including DataFrame and Dataset concepts, SparkSession lifecycle, caching, storage levels, and garbage collection.
- Explain the Apache Spark™ Architecture execution hierarchy.
- Configure Spark partitioning in distributed data processing, including shuffles and partitions
- Describe the execution patterns of the Apache Spark™ engine, including actions, transformations, and lazy evaluation.
- Identify the features of the Apache Spark Modules, including Core, Spark SQL, DataFrames, Pandas API on Spark, Structured Streaming, and MLib.

## Section 2: Using Spark SQL

- Utilize common data sources such as JDBC, files, etc., to efficiently read from and write to Spark DataFrames using Spark SQL, including overwriting and partitioning by column.
- Execute SQL queries directly on files, including ORC Files, JSON Files, CSV Files, Text Files, and Delta Files, and understand the different save modes for outputting data in Spark SQL.
- Save data to persistent tables while applying sorting and partitioning to optimize data retrieval.
- Register DataFrames as temporary views in Spark SQL, allowing them to be queried with SQL syntax.

## Section 3: Developing Apache Spark™ DataFrame/DataSet API Applications

- Manipulate columns, rows, and table structures by adding, dropping, splitting, renaming column names, applying filters, and exploding arrays.
- Perform data deduplication and validation operations on DataFrames.
- Perform aggregate operations on DataFrames such as count, approximate count distinct, and mean, summary.
- Manipulate and utilize Date data type, such as Unix epoch to date string, and extract date component.
- Combine DataFrames with operations such as Inner join, left join, broadcast join, multiple keys, cross join, union, and union all.
- Manage input and output operations by writing, overwriting, and reading DataFrames with schemas.
- Perform operations on DataFrames such as sorting, iterating, printing schema, and conversion between DataFrame and sequence/list formats.
- Create and invoke user-defined functions with or without stateful operators, including StateStores.
- Describe different types of variables in Spark, including broadcast variables and accumulators.
- Describe the purpose and implementation of broadcast joins

## Section 4: Troubleshooting and Tuning Apache Spark DataFrame API Applications

- Implement performance tuning strategies & optimize cluster utilization, including partitioning, repartitioning, coalescing, identifying data skew, and reducing shuffling
- Describe Adaptive Query Execution (AQE) and its benefits.
- Perform logging and monitoring of Spark applications - publish, customize, and analyze Driver logs and Executor logs to diagnose out-of-memory errors, cluster underutilization, etc.

## Section 5: Structured Streaming

- Explain the Structured Streaming engine in Spark, including its functions, programming model, micro-batch processing, exactly-once semantics, and fault tolerance mechanisms.
- Create and write Streaming DataFrames and Streaming Datasets, including the basic output modes and output sinks.
- Perform basic operations on Streaming DataFrames and Streaming Datasets, such as selection, projection, window and aggregation.
- Perform Streaming Deduplication in Structured Streaming, both with and without watermark usage.

## Section 6: Using Spark Connect to deploy applications

- Describe the features of Spark Connect.
- Describe the different deployment mode types (Client, Cluster, Local) in the Apache Spark™ environment.

## Section 7: Using Pandas API on Spark

- Explain the advantages of using Pandas API on Spark.
- Create and invoke Pandas UDF.

## Sample Question Shape (from the guide)

Each sample question gives the objective, a scenario, and four options:

> *Objective - Utilize common data sources such as JDBC, files, etc. to
> efficiently read from and write to Spark DataFrames using SparkSQL, including
> overwrite and partitioning by column.*
>
> A data engineer needs to write a DataFrame df to a Parquet file, partitioned
> by the column country, and overwrite any existing data at the destination path.
>
> Which code should the data engineer use to accomplish this task in Apache Spark?
>
> A. `df.write.mode("append").partitionBy("country").parquet("/data/output")`
> B. `df.write.partitionBy("country").parquet("/data/output")`
> C. `df.write.mode("overwrite").parquet("/data/output")`
> D. `df.write.mode("overwrite").partitionBy("country").parquet("/data/output")`
