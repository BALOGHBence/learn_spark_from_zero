# Reading and Writing Data

{doc}`Introduction to DataFrames <01_introduction_to_dataframes>` built
DataFrames by hand. Real pipelines read them from storage and write their
results back. This page covers where data lives on Databricks, how to read
tables and files, and how to write results out safely.

## Where Data Lives on Databricks

On Databricks, data is governed by **Unity Catalog**, which organises it in a
three-level namespace:

```mermaid
:caption: The Unity Catalog object hierarchy.
:align: center

graph TD
    C[Catalog] --> S[Schema]
    S --> T[Tables and views]
    S --> V[Volumes]
    T --> TN["catalog.schema.table"]
    V --> VP["/Volumes/catalog/schema/volume/..."]
```

- **Tables** hold structured data and are addressed as
  `catalog.schema.table`. Unless you specify otherwise, tables are stored in
  **Delta Lake** format: Parquet files plus a transaction log that adds ACID
  transactions, schema enforcement and time travel. Most tables on Databricks
  are *managed* tables, where Unity Catalog also manages the underlying
  storage. This is the recommended default.
- **Volumes** hold files (CSV, JSON, images, anything) and are addressed as
  paths of the form `/Volumes/<catalog>/<schema>/<volume>/<path>`. Use them
  for raw files you ingest, or files you need to hand to other systems.

Databricks recommends reading and writing **tables by name** wherever
possible and using volumes for file access, rather than raw cloud storage
URIs (`s3://...`, `abfss://...`) or the legacy DBFS.

:::{admonition} Note: The Catalog and Schema Used on This Page
:class: note

Every workspace has a read-only `samples` catalog with example datasets;
this page reads from `samples.nyctaxi.trips`. To write, you need a schema
where you have `CREATE TABLE` (and, for volumes, `CREATE VOLUME`)
privileges. In Databricks Free Edition the `workspace.default` schema works.
Substitute your own catalog and schema if you are elsewhere.
:::

## The DataFrameReader

All reads start from `spark.read`, a `DataFrameReader`. The general pattern
is:

```python
df = (
    spark.read
    .format("<format>")          # csv, json, parquet, delta, text, ...
    .option("<key>", "<value>")  # format-specific options
    .schema("<ddl schema>")      # optional: declare the schema up front
    .load("<path>")
)
```

Each common format also has a shortcut such as `spark.read.csv(path, ...)`,
`spark.read.json(path)` or `spark.read.parquet(path)`.

### Reading Tables

Reading a table needs only its name:

```python
trips = spark.read.table("samples.nyctaxi.trips")
# or, equivalently
trips = spark.table("samples.nyctaxi.trips")
```

The schema comes from the catalog, so there is nothing to infer and nothing
to declare.

### Reading Files from a Volume

Let's create a volume and put a CSV extract of the taxi data in it, so there
is a file to read:

```python
spark.sql("CREATE VOLUME IF NOT EXISTS workspace.default.raw")

(
    spark.read.table("samples.nyctaxi.trips")
    .limit(1000)
    .write
    .mode("overwrite")
    .option("header", True)
    .csv("/Volumes/workspace/default/raw/trips_csv")
)
```

Spark writes a **directory** of part files, one per partition, rather than a
single file. Readers accept the directory path and read every file in it.

Reading the CSV back with schema inference:

```python
trips_csv = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("/Volumes/workspace/default/raw/trips_csv")
)
trips_csv.printSchema()
```

Schema inference is convenient for exploration, but it has two costs. Spark
must read the data an extra time to guess the types, and the guess can change
when the data does (a column that happens to contain only digits today
becomes an `int`, then breaks when a letter shows up tomorrow). In pipelines,
**declare the schema**:

```python
trips_schema = """
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    trip_distance DOUBLE,
    fare_amount DOUBLE,
    pickup_zip INT,
    dropoff_zip INT
"""

trips_csv = (
    spark.read
    .schema(trips_schema)
    .option("header", True)
    .csv("/Volumes/workspace/default/raw/trips_csv")
)
```

Some useful options for the text-based formats:

| Option | Formats | Meaning |
| --- | --- | --- |
| `header` | CSV | First line contains column names |
| `sep` | CSV | Field delimiter (default `,`) |
| `inferSchema` | CSV | Guess column types from the data |
| `multiLine` | CSV, JSON | Records may span several lines |
| `mode` | CSV, JSON | What to do with malformed rows: `PERMISSIVE` (default), `DROPMALFORMED` or `FAILFAST` |
| `dateFormat` / `timestampFormat` | CSV, JSON | Patterns for parsing dates and timestamps |

Self-describing formats such as **Parquet** and **Delta** store their schema
with the data, so they need neither inference nor a declared schema.

### Which File Did a Row Come From?

Every file-based DataFrame has a hidden `_metadata` column with details about
the source file. Select it explicitly to use it:

```python
trips_csv.select("*", "_metadata.file_path", "_metadata.file_modification_time")
```

This replaces the older `input_file_name()` function, which is deprecated on
serverless compute.

### Reading Files with SQL

In SQL, the `read_files` table-valued function reads files from a volume and
infers the schema across them:

```python
spark.sql("""
    SELECT *
    FROM read_files(
        '/Volumes/workspace/default/raw/trips_csv',
        format => 'csv',
        header => true
    )
""")
```

## The DataFrameWriter

Writes start from `df.write`, a `DataFrameWriter`, and mirror the reader:

```python
(
    df.write
    .format("<format>")       # delta by default for tables
    .mode("<save mode>")      # what to do if the target exists
    .option("<key>", "<value>")
    .saveAsTable("<catalog.schema.table>")   # or .save("<path>") for files
)
```

### Save Modes

The **save mode** decides what happens when the target already exists:

| Mode | Behaviour if the target exists |
| --- | --- |
| `errorifexists` (default) | Fail with an error |
| `append` | Add the new rows to the existing data |
| `overwrite` | Replace the existing data |
| `ignore` | Do nothing, silently |

### Writing Tables

Writing a managed Delta table to Unity Catalog:

```python
(
    trips_csv.write
    .mode("overwrite")
    .saveAsTable("workspace.default.trips_bronze")
)
```

The table is immediately queryable from SQL, from other notebooks and from
dashboards:

```python
spark.sql("SELECT count(*) FROM workspace.default.trips_bronze").show()
```

Because the table is in Delta format, a failed or interrupted write leaves the
previous version intact. Delta also enforces the table's schema: appending a
DataFrame whose columns do not match the table fails unless you explicitly
allow the schema to change, for example with `.option("mergeSchema", True)`.

An alternative is the newer `DataFrameWriterV2` API, reached through
`df.writeTo(...)`, which uses more explicit verbs:

```python
trips_csv.writeTo("workspace.default.trips_bronze").createOrReplace()
trips_csv.writeTo("workspace.default.trips_bronze").append()
```

### Writing Files

To produce files, for example to hand data to another system, use `save` (or
a format shortcut) with a volume path:

```python
(
    trips_csv.write
    .mode("overwrite")
    .parquet("/Volumes/workspace/default/raw/trips_parquet")
)
```

`partitionBy` splits the output into one subdirectory per value of the given
columns, which lets later readers skip directories they don't need:

```python
from pyspark.sql import functions as F

(
    trips_csv
    .withColumn("pickup_date", F.to_date("tpep_pickup_datetime"))
    .write
    .mode("overwrite")
    .partitionBy("pickup_date")
    .parquet("/Volumes/workspace/default/raw/trips_by_date")
)
```

Partition only on low-cardinality columns that queries actually filter by.
Partitioning on a column with many distinct values creates many tiny files,
which is slower, not faster. For Delta tables on Databricks, prefer **liquid
clustering** (`CLUSTER BY` in `CREATE TABLE`, or `clusterBy(...)` on the
writer) over hand-picked partitions.

:::::{dropdown} Example: Ingest a CSV Extract into a Table
:open:
:color: primary
:icon: pencil
:class-body: example-body

We want a table of long taxi trips, built from the CSV extract in the `raw`
volume, with a declared schema and the source file recorded on each row.

**Read with an explicit schema.**

```python
from pyspark.sql import functions as F

raw = (
    spark.read
    .schema(trips_schema)
    .option("header", True)
    .csv("/Volumes/workspace/default/raw/trips_csv")
)
```

**Keep the long trips and record the source file.**

```python
long_trips = (
    raw
    .filter(F.col("trip_distance") > 10)
    .withColumn("source_file", F.col("_metadata.file_path"))
)
```

**Write the result as a managed Delta table.**

```python
long_trips.write.mode("overwrite").saveAsTable("workspace.default.long_trips")
```

Only the final `saveAsTable` is an action, so Spark plans and runs the read,
filter and write as a single job. The result is a governed Delta table that
anyone with access can query by name.
:::::

## Cleaning Up

Tables and volumes are persistent. Drop the ones you created on this page
when you no longer need them:

```python
spark.sql("DROP TABLE IF EXISTS workspace.default.trips_bronze")
spark.sql("DROP TABLE IF EXISTS workspace.default.long_trips")
spark.sql("DROP VOLUME IF EXISTS workspace.default.raw")
```

Dropping a *managed* table or volume also deletes its underlying data.

With reading, transforming and writing covered, the next section looks at
what happens on the cluster while these operations run:
{doc}`Distributed Systems Programming Fundamentals <../03_distributed_systems_programming_fundamentals/index>`.

## Resources

- [Query data (Databricks)](https://docs.databricks.com/aws/en/query/)
- [What are Unity Catalog volumes? (Databricks)](https://docs.databricks.com/aws/en/volumes/)
- [Data sources (Apache Spark)](https://spark.apache.org/docs/latest/sql-data-sources.html)
