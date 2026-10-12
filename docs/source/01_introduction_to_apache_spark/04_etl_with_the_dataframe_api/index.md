# ETL with the DataFrame API

**ETL** (extract, transform, load) is the bread and butter of data
engineering: pull data out of a source, clean and reshape it, and store the
result where analysts, dashboards and models can use it. This page builds a
small but complete ETL pipeline over the NYC taxi sample data. It uses the
DataFrame operations from
{doc}`Introduction to DataFrames <../02_spark_dataframes_and_sql/01_introduction_to_dataframes>`,
the readers and writers from
{doc}`Reading and Writing Data <../02_spark_dataframes_and_sql/02_reading_and_writing_data>`,
and the performance ideas from
{doc}`Distributed Systems Programming Fundamentals <../03_distributed_systems_programming_fundamentals/03_distributed_systems_programming_fundamentals>`.

## The Medallion Architecture

Most pipelines on Databricks organise tables into three layers of
increasing quality, known as the **medallion architecture**:

```mermaid
:caption: Bronze, silver and gold layers of the pipeline built on this page.
:align: center

graph LR
    Src[("samples.nyctaxi.trips")] --> B[Bronze: trips_bronze]
    B --> S[Silver: trips_silver]
    S --> G[Gold: daily_zip_revenue]
```

- **Bronze**: raw data as it arrived, plus ingestion metadata. Nothing is
  thrown away, so you can always reprocess.
- **Silver**: cleaned, validated, de-duplicated and correctly typed data.
  This is the "single source of truth" for the entity.
- **Gold**: aggregated, business-level tables shaped for a specific use,
  such as a dashboard or a report.

The examples write to `workspace.default`; substitute your own catalog and
schema if needed.

```python
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from project.utils.sparksession import get_spark_session

spark = get_spark_session(profile="free-edition")

TARGET = "workspace.default"
```

## Extract: Building the Bronze Layer

The extract step reads the source as faithfully as possible and records
where and when each row came from:

```python
def extract_trips(source_table: str) -> DataFrame:
    return (
        spark.read.table(source_table)
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source", F.lit(source_table))
    )


bronze = extract_trips("samples.nyctaxi.trips")
bronze.write.mode("overwrite").saveAsTable(f"{TARGET}.trips_bronze")
```

When the source is a set of files in a volume instead of a table, the same
function would use `spark.read` with an explicit schema and record
`_metadata.file_path` as the source, as shown in
{doc}`Reading and Writing Data <../02_spark_dataframes_and_sql/02_reading_and_writing_data>`.

:::{admonition} Note: Incremental Ingestion
:class: note

This page reloads the whole source on every run, which is fine for a sample
table. For sources that keep growing, you would ingest only *new* data, for
example with Auto Loader and Structured Streaming, or declaratively with
Lakeflow Spark Declarative Pipelines. Those tools build on exactly the same
DataFrame transformations shown here.
:::

## Transform: Building the Silver Layer

Transformations are where most of the logic lives. Write each one as a
function from DataFrame to DataFrame, so that each step can be named, tested
on its own and reused.

### Cleaning and Validating

Raw taxi data contains trips with zero distance, negative fares and drop-off
times before pick-up times. Keep only rows that make physical sense:

```python
def filter_valid_trips(df: DataFrame) -> DataFrame:
    return df.filter(
        (F.col("trip_distance") > 0)
        & (F.col("fare_amount") > 0)
        & (F.col("tpep_dropoff_datetime") > F.col("tpep_pickup_datetime"))
        & F.col("pickup_zip").isNotNull()
        & F.col("dropoff_zip").isNotNull()
    )
```

Instead of silently dropping bad rows, a production pipeline usually counts
them or writes them to a separate quarantine table, so data problems are
visible.

### Deriving Columns

Add the columns downstream consumers will need, computed once, here:

```python
def add_trip_features(df: DataFrame) -> DataFrame:
    duration_minutes = (
        F.unix_timestamp("tpep_dropoff_datetime")
        - F.unix_timestamp("tpep_pickup_datetime")
    ) / 60

    return df.select(
        "*",
        F.to_date("tpep_pickup_datetime").alias("pickup_date"),
        F.round(duration_minutes, 2).alias("duration_minutes"),
        F.round(
            F.col("trip_distance") / (duration_minutes / 60), 2
        ).alias("avg_speed_mph"),
    )
```

Using a single `select` that adds all three columns keeps the plan shallow,
as recommended in
{ref}`Driver Code versus Executor Code <driver-vs-executor-code>`.

### De-duplicating with a Window Function

Sources often deliver the same record more than once. `dropDuplicates` keeps
an arbitrary row per key. When you need to control *which* row survives,
for example the most recently ingested one, use a **window function**:

```python
def deduplicate_trips(df: DataFrame) -> DataFrame:
    trip_key = ["tpep_pickup_datetime", "tpep_dropoff_datetime", "pickup_zip", "dropoff_zip"]
    latest_first = Window.partitionBy(*trip_key).orderBy(F.desc("_ingested_at"))

    return (
        df
        .withColumn("_row_number", F.row_number().over(latest_first))
        .filter(F.col("_row_number") == 1)
        .drop("_row_number")
    )
```

A window function computes a value for each row from a group of related rows
(the *window*) without collapsing the group the way `groupBy` does. Like
`groupBy`, `partitionBy` triggers a shuffle on the key columns.

:::::{dropdown} Example: How `row_number` Picks the Survivor
:open:
:color: primary
:icon: pencil
:class-body: example-body

Suppose the same trip arrived twice, in two loads an hour apart.

**Input rows sharing one trip key.**

```text
pickup_zip  fare_amount  _ingested_at
10001       12.5         2026-10-12 08:00
10001       12.5         2026-10-12 09:00
```

**Number the rows within the window, newest first.**

```text
pickup_zip  fare_amount  _ingested_at       _row_number
10001       12.5         2026-10-12 09:00   1
10001       12.5         2026-10-12 08:00   2
```

Keeping `_row_number == 1` retains exactly one row per trip, the 09:00 copy.
Changing the `orderBy` in the window changes which copy survives.
:::::

### Composing the Steps

`DataFrame.transform` chains functions that take and return a DataFrame,
so the whole silver step reads as a list of named stages:

```python
def build_silver(bronze: DataFrame) -> DataFrame:
    return (
        bronze
        .transform(filter_valid_trips)
        .transform(add_trip_features)
        .transform(deduplicate_trips)
    )


silver = build_silver(spark.read.table(f"{TARGET}.trips_bronze"))
silver.write.mode("overwrite").saveAsTable(f"{TARGET}.trips_silver")
```

Nothing runs until `saveAsTable`. At that point Spark optimises the
filter, the derived columns and the de-duplication as one plan, as described
in {doc}`Introduction to DataFrames <../02_spark_dataframes_and_sql/01_introduction_to_dataframes>`.

## Transform: Building the Gold Layer

Gold tables answer a specific question. Here: how much fare revenue did each
pick-up zip code generate per day, and what did a typical trip look like?

```python
def build_daily_zip_revenue(silver: DataFrame) -> DataFrame:
    return (
        silver
        .groupBy("pickup_date", "pickup_zip")
        .agg(
            F.count("*").alias("trip_count"),
            F.round(F.sum("fare_amount"), 2).alias("total_fare"),
            F.round(F.avg("trip_distance"), 2).alias("avg_distance"),
            F.round(F.percentile_approx("duration_minutes", 0.5), 2).alias("median_duration_minutes"),
        )
    )


gold = build_daily_zip_revenue(spark.read.table(f"{TARGET}.trips_silver"))
gold.write.mode("overwrite").saveAsTable(f"{TARGET}.daily_zip_revenue")
```

`percentile_approx` computes an approximate median. An exact median would
need all values for a group in one place, while the approximate version can
be computed in partial aggregates on each executor before the shuffle.

## Load: Writing Results Safely

Every run of a pipeline should leave the target in a correct state, even if
the run is repeated. A pipeline with this property is **idempotent**, and
it lets you safely retry after a failure. The choice of write strategy
decides whether a pipeline is idempotent:

| Strategy | When to use it | Idempotent? |
| --- | --- | --- |
| `mode("overwrite")` | Small tables you can rebuild completely | Yes |
| `mode("overwrite")` with `replaceWhere` | Rebuilding one slice, such as one day | Yes |
| `mode("append")` | Adding new, never-seen-before rows | No: a retry duplicates rows |
| `MERGE INTO` | Inserting new rows and updating changed ones | Yes, when keyed correctly |

Overwriting a single slice of a Delta table with `replaceWhere`:

```python
day = "2016-02-13"

(
    gold
    .filter(F.col("pickup_date") == day)
    .write
    .mode("overwrite")
    .option("replaceWhere", f"pickup_date = '{day}'")
    .saveAsTable(f"{TARGET}.daily_zip_revenue")
)
```

An **upsert** with `MERGE INTO` updates rows that already exist and inserts
the rest. The new data is exposed to SQL as a temporary view:

```python
gold.createOrReplaceTempView("daily_zip_revenue_updates")

spark.sql(f"""
    MERGE INTO {TARGET}.daily_zip_revenue AS target
    USING daily_zip_revenue_updates AS source
    ON  target.pickup_date = source.pickup_date
    AND target.pickup_zip  = source.pickup_zip
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")
```

`MERGE` is a Delta Lake operation and runs as a single atomic transaction.
Readers see either the old table or the new one, never a half-written state.

## Checking the Result

A few cheap checks after each load catch most problems before anyone else
notices them:

```python
silver = spark.read.table(f"{TARGET}.trips_silver")

checks = silver.agg(
    F.count("*").alias("rows"),
    F.sum(F.when(F.col("fare_amount") <= 0, 1).otherwise(0)).alias("non_positive_fares"),
    F.sum(F.when(F.col("duration_minutes") <= 0, 1).otherwise(0)).alias("non_positive_durations"),
).first()

assert checks["rows"] > 0, "silver table is empty"
assert checks["non_positive_fares"] == 0
assert checks["non_positive_durations"] == 0
```

All three numbers come back in a single `Row`, from a single job, because
they are computed in one `agg`. Running three separate `count()` actions
would scan the table three times.

Delta tables also keep a history of every write, which helps when something
does go wrong:

```python
spark.sql(f"DESCRIBE HISTORY {TARGET}.daily_zip_revenue").show(truncate=False)
```

## Testing Transformations

Because each transformation is a plain function from DataFrame to DataFrame,
it can be unit tested with a tiny hand-built input. This repository has a
`pytest` setup under the `test` dependency group. Assuming the functions
above live in a module such as `project/etl/trips.py`, a test looks like this:

```python
from datetime import datetime

from project.utils.sparksession import get_spark_session

# wherever you keep the pipeline's transformations
from project.etl.trips import filter_valid_trips


def test_filter_valid_trips_drops_negative_fares():
    spark = get_spark_session(profile="free-edition")
    df = spark.createDataFrame(
        [
            (datetime(2016, 2, 1, 10, 0), datetime(2016, 2, 1, 10, 15), 2.0, 9.5, 10001, 10003),
            (datetime(2016, 2, 1, 11, 0), datetime(2016, 2, 1, 11, 10), 1.5, -3.0, 10001, 10003),
        ],
        schema="""
            tpep_pickup_datetime TIMESTAMP, tpep_dropoff_datetime TIMESTAMP,
            trip_distance DOUBLE, fare_amount DOUBLE,
            pickup_zip INT, dropoff_zip INT
        """,
    )

    result = filter_valid_trips(df)

    assert result.count() == 1
```

The first row is a valid 15-minute trip and passes the filter;
the second has a negative fare and is dropped, so exactly one row remains.

## Cleaning Up

Drop the tables created on this page when you are finished:

```python
for table in ["trips_bronze", "trips_silver", "daily_zip_revenue"]:
    spark.sql(f"DROP TABLE IF EXISTS {TARGET}.{table}")
```

## Resources

- [What is the medallion lakehouse architecture? (Databricks)](https://docs.databricks.com/aws/en/lakehouse/medallion)
- [Upsert into a Delta Lake table using merge (Databricks)](https://docs.databricks.com/aws/en/delta/merge)
- [Selectively overwrite data with Delta Lake (Databricks)](https://docs.databricks.com/aws/en/delta/selective-overwrite)
- [Window functions (Apache Spark)](https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-window.html)
