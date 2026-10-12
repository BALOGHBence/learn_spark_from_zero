# Hands-On Tasks Before the Exam

The {doc}`mock exam <../00_getting_started/03_taking_a_mock_exam_with_claude_code>`
tells you whether you can *recognise* the right answer. The tasks on this page
check whether you can *produce* it. The exam has no test aids, not even the API
documentation, so you need to write the code from memory. Before you sit the
exam, you should be able to do each task below without looking anything up.

Each task maps to one or more objectives from the exam guide, quoted word for
word. Every task fits in under 30 minutes in Databricks Free Edition. If one
takes much longer, or you need to look things up to finish it, go back to the
linked course page and then try again.

## Before You Start

Free Edition gives you serverless compute only, and supports Python and SQL but
not R or Scala
([Databricks Free Edition limitations](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations)).
Do the tasks in a Free Edition notebook, or locally through the Databricks
Connect session from
{doc}`Setting Up Databricks Connect <../00_getting_started/01_setting_up_databricks_connect>`.

Use the read-only `samples` catalog as input. Write your output to
`workspace.default`, and keep your files in a scratch volume. Files in a volume
are addressed as `/Volumes/<catalog>/<schema>/<volume>/<path>`
([What are Unity Catalog volumes?](https://docs.databricks.com/aws/en/volumes/)):

```sql
CREATE VOLUME IF NOT EXISTS workspace.default.exam_tasks;
```

Use absolute `/Volumes/...` paths. Serverless doesn't guarantee the working
directory of a notebook, and access to DBFS is limited
([Serverless compute limitations](https://docs.databricks.com/aws/en/compute/serverless/limitations)).

(task-read-write-files)=
## Task 1: Read and Write Files with an Explicit Schema

Write `samples.nyctaxi.trips` to the volume as CSV, read it back with a
`StructType` schema you define yourself instead of an inferred one, then write
it as Parquet partitioned by pickup date with `mode("overwrite")`, and run the
write twice to confirm the second run replaces the first.

**Objectives:**

- *Utilize common data sources such as JDBC, files, etc., to efficiently read from and write to Spark DataFrames using Spark SQL, including overwriting and partitioning by column.*
- *Manage input and output operations by writing, overwriting, and reading DataFrames with schemas.*

**Course page:**
{doc}`Reading and Writing Data <../01_introduction_to_apache_spark/02_spark_dataframes_and_sql/02_reading_and_writing_data>`

(task-sql-on-files)=
## Task 2: Query Files with SQL and Save Tables

Query the Task 1 files directly with SQL. Use
`` SELECT * FROM json.`/Volumes/...` `` for JSON files, which works the same way
for other formats, and `read_files`, which reads JSON, CSV, Parquet, ORC, text
and other formats
([Query data](https://docs.databricks.com/aws/en/query/),
[read_files](https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files)).
Then register the DataFrame as a temporary view, and save it as a persistent
table with `saveAsTable`, sorted within partitions and partitioned by a column.
Try every save mode (`errorifexists`, `append`, `overwrite`, `ignore`) and
predict each result before you run it.

**Objectives:**

- *Execute SQL queries directly on files, including ORC Files, JSON Files, CSV Files, Text Files, and Delta Files, and understand the different save modes for outputting data in Spark SQL.*
- *Save data to persistent tables while applying sorting and partitioning to optimize data retrieval.*
- *Register DataFrames as temporary views in Spark SQL, allowing them to be queried with SQL syntax.*

**Course page:**
{doc}`Reading and Writing Data <../01_introduction_to_apache_spark/02_spark_dataframes_and_sql/02_reading_and_writing_data>`

(task-clean-dataframe)=
## Task 3: Clean a Messy DataFrame

Build a small DataFrame with `spark.createDataFrame` that has duplicate rows,
nulls, and a comma-separated tags column. Then clean it:

- split the tags into an array and `explode` it into one row per tag;
- rename, add and drop columns;
- remove duplicates with `dropDuplicates` on a subset of columns;
- handle nulls with `na.drop` and `na.fill`;
- filter out rows that fail a validation rule, and count how many each step
  removed.

**Objectives:**

- *Manipulate columns, rows, and table structures by adding, dropping, splitting, renaming column names, applying filters, and exploding arrays.*
- *Perform data deduplication and validation operations on DataFrames.*

**Course pages:**
{doc}`DataFrame API Basics <../02_developing_applications_with_apache_spark/01_dataframe_api_basics>`,
{doc}`Working with Complex Data <../02_developing_applications_with_apache_spark/04_working_with_complex_data>`

(task-aggregate-dates)=
## Task 4: Aggregate Trips by Time

From `samples.nyctaxi.trips`:

- convert the pickup timestamp to Unix epoch seconds and back to a formatted
  date string with `from_unixtime`
  ([from_unixtime function](https://docs.databricks.com/aws/en/sql/language-manual/functions/from_unixtime));
- extract the hour and day of week;
- per hour, compute the trip count, mean fare and `approx_count_distinct` of
  pickup zip codes. Its estimate is accurate to within 5% by default
  ([approx_count_distinct aggregate function](https://docs.databricks.com/aws/en/sql/language-manual/functions/approx_count_distinct));
- sort the result, print its schema, run `summary()` on it, and `collect()` the
  top five rows into a Python list.

**Objectives:**

- *Perform aggregate operations on DataFrames such as count, approximate count distinct, and mean, summary.*
- *Manipulate and utilize Date data type, such as Unix epoch to date string, and extract date component.*
- *Perform operations on DataFrames such as sorting, iterating, printing schema, and conversion between DataFrame and sequence/list formats.*

**Course page:**
{doc}`Grouping and Aggregating Data <../02_developing_applications_with_apache_spark/02_grouping_and_aggregating_data>`

(task-join-combine)=
## Task 5: Join and Combine Tables

Join the `samples.tpch` tables `orders`, `customer` and `nation`:

- write an inner join and a left join, and explain the row counts of each;
- join on two keys;
- add a `broadcast()` hint on `nation`, and find the broadcast join in the
  `explain()` output. The hinted side is broadcast regardless of
  `autoBroadcastJoinThreshold`
  ([Hints](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-select-hints));
- build a small `crossJoin`;
- stack two DataFrames with `union` and with `unionByName`, and show where the
  two differ.

**Objectives:**

- *Combine DataFrames with operations such as Inner join, left join, broadcast join, multiple keys, cross join, union, and union all.*
- *Describe the purpose and implementation of broadcast joins*

**Course page:**
{doc}`DataFrame Relational Operations <../02_developing_applications_with_apache_spark/03_dataframe_relational_operations>`

(task-partitions-aqe)=
## Task 6: Inspect Partitions, Shuffles and AQE

On `samples.tpch.lineitem`:

- count the rows in each partition with `spark_partition_id()`;
- compare `repartition(n)` with `coalesce(n)` in `explain()`, and find which
  one adds an `Exchange`;
- find the most skewed key by counting rows per key;
- find the `AdaptiveSparkPlan` node that shows Adaptive Query Execution is on,
  and check its `isFinalPlan` flag before and after an action
  ([Adaptive query execution](https://docs.databricks.com/aws/en/optimizations/aqe)).
  In a notebook, also open the query profile through **See performance**
  ([Serverless compute for notebooks](https://docs.databricks.com/aws/en/compute/serverless/notebooks)).

**Objectives:**

- *Configure Spark partitioning in distributed data processing, including shuffles and partitions*
- *Implement performance tuning strategies & optimize cluster utilization, including partitioning, repartitioning, coalescing, identifying data skew, and reducing shuffling*
- *Describe Adaptive Query Execution (AQE) and its benefits.*

**Course pages:**
{doc}`Distributed Systems Programming Fundamentals <../01_introduction_to_apache_spark/03_distributed_systems_programming_fundamentals/03_distributed_systems_programming_fundamentals>`,
{doc}`Optimizing Apache Spark <../04_monitoring_and_optimizing_spark_workloads_on_databricks/03_optimizing_apache_spark>`

(task-streaming)=
## Task 7: Build a Small Streaming Pipeline

1. Drop a few JSON files of events, some of them duplicates, into the volume.
2. Read them with `readStream` and a fixed schema.
3. Remove duplicates with `withWatermark` and `dropDuplicatesWithinWatermark`,
   and compute a windowed count.
4. Write the result to a Delta table with a checkpoint in the volume, using
   `trigger(availableNow=True)`.
5. Add more files, run the query again, and confirm that only the new data is
   processed.

Serverless compute supports only the `availableNow` and `once` triggers
([Configure Structured Streaming trigger intervals](https://docs.databricks.com/aws/en/structured-streaming/triggers)).
Watermarks let Spark drop old aggregation state and duplicates
([Apply watermarks to control data processing thresholds](https://docs.databricks.com/aws/en/structured-streaming/watermarks)).

**Objectives:**

- *Create and write Streaming DataFrames and Streaming Datasets, including the basic output modes and output sinks.*
- *Perform basic operations on Streaming DataFrames and Streaming Datasets, such as selection, projection, window and aggregation.*
- *Perform Streaming Deduplication in Structured Streaming, both with and without watermark usage.*

**Course page:**
{doc}`Stream Aggregations, Windows and Watermarks <../03_stream_processing_and_analysis/03_stream_aggregations_windows_and_watermarks>`

(task-udfs)=
## Task 8: Write a Python UDF and a pandas UDF

Compute the same value, such as fare per mile on `samples.nyctaxi.trips`, three
ways:

- with a row-at-a-time Python `udf`;
- with a Series-to-Series `pandas_udf`;
- with built-in column functions.

Then check that all three return the same results. pandas UDFs are
vectorized: they exchange data with Spark in Apache Arrow batches, and on
serverless the platform sizes those batches itself
([pandas user-defined functions](https://docs.databricks.com/aws/en/udf/pandas)).

**Objectives:**

- *Create and invoke Pandas UDF.*
- *Create and invoke user-defined functions with or without stateful operators, including StateStores.*

**Course page:** none yet. Use the official
[pandas user-defined functions](https://docs.databricks.com/aws/en/udf/pandas)
page.

:::{admonition} Note: UDFs Through Databricks Connect on the Course Workspace
:class: note

When this page was last checked, both a Python `udf` and a `pandas_udf` sent
through Databricks Connect to the course's Free Edition workspace failed with
`ISOLATION_STARTUP_FAILURE.SANDBOX_STARTUP`: the serverless sandbox that runs
Python UDF code didn't start. Built-in functions were unaffected. If you see
the same error, do this task in a notebook in the workspace instead.
:::

(task-spark-connect)=
## Task 9: Watch Lazy Evaluation Through Spark Connect

From your local IDE, connected through Databricks Connect:

- chain several transformations and time them;
- time an action such as `count()`;
- explain the difference between the two timings;
- point out which lines ran locally and which ran on Databricks compute.

Databricks Connect is built on Spark Connect. DataFrame operations are sent to
Databricks compute as plans, and results come back only when you call methods
such as `collect()`, `show()` or `toPandas()`
([Databricks Connect](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/)).

**Objectives:**

- *Describe the features of Spark Connect.*
- *Describe the execution patterns of the Apache Spark™ engine, including actions, transformations, and lazy evaluation.*

**Course pages:**
{doc}`Setting Up Databricks Connect <../00_getting_started/01_setting_up_databricks_connect>`,
{doc}`Introduction to DataFrames <../01_introduction_to_apache_spark/02_spark_dataframes_and_sql/01_introduction_to_dataframes>`

(free-edition-gaps)=
## What You Can't Practise on Free Edition

Some objectives depend on features that serverless compute, and therefore Free
Edition, doesn't offer. Study these from the course pages and the
documentation instead:

- **Driver and executor logs, and the Spark UI.** Serverless has no Spark UI
  and no Spark logs. Only client-side application logs are available
  ([Serverless compute limitations](https://docs.databricks.com/aws/en/compute/serverless/limitations)).
  The query profile in Task 6 is the serverless way to inspect a query. Learn
  the log-based diagnosis from the docs for *Perform logging and monitoring of
  Spark applications - publish, customize, and analyze Driver logs and
  Executor logs to diagnose out-of-memory errors, cluster underutilization,
  etc.*
- **Broadcast variables and accumulators.** These are created through
  `SparkContext`
  ([Apache Spark API reference: SparkContext.broadcast](https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.SparkContext.broadcast.html)),
  and Spark Connect doesn't expose `SparkContext` or RDDs
  ([Limitations with Databricks Connect for Python](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/limitations)).
  This affects *Describe different types of variables in Spark, including
  broadcast variables and accumulators.*
- **Caching and storage levels.** `df.cache()` and `df.persist()` aren't
  supported on serverless
  ([Serverless compute limitations](https://docs.databricks.com/aws/en/compute/serverless/limitations)).
  This is part of *Describe the architecture of Apache Spark™, including
  DataFrame and Dataset concepts, SparkSession lifecycle, caching, storage
  levels, and garbage collection.*
- **Deployment modes.** Free Edition has no custom compute configurations
  ([Databricks Free Edition limitations](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations)),
  so client, cluster and local mode are conceptual here. This affects
  *Describe the different deployment mode types (Client, Cluster, Local) in
  the Apache Spark™ environment.*

:::{admonition} Unverified: Pandas API on Spark on Serverless Compute
:class: warning

The [pandas API on Spark](https://docs.databricks.com/aws/en/pandas/pandas-on-spark)
page says the feature is available on Databricks Runtime 10.0 and above, but it
doesn't say whether `pyspark.pandas` works on serverless compute or through
Databricks Connect. This couldn't be confirmed in the official Databricks
documentation when this page was written. In practice, on the course's Free
Edition workspace through Databricks Connect,
`spark.read.table("samples.nyctaxi.trips").pandas_api()` returned a
pandas-on-Spark DataFrame and computed `fare_amount.mean()` when this page
was last checked. That shows it worked there, not that Databricks supports
it. Check the serverless and Databricks Connect limitation pages before you
rely on it for *Explain the advantages of using Pandas API on Spark.*
:::

Once you can do all nine tasks fluently, take a fresh
{doc}`mock exam <../00_getting_started/03_taking_a_mock_exam_with_claude_code>`
and compare your section scores with your last attempt.
