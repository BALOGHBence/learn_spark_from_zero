# Distributed Systems Programming Fundamentals

{doc}`Spark Runtime Architecture <../01_apache_spark_runtime_architecture/02_spark_runtime_architecture>`
introduced the driver, which plans work, and the executors, which run it.
{doc}`Introduction to DataFrames <../02_spark_dataframes_and_sql/01_introduction_to_dataframes>`
showed that transformations only build a plan. This page connects the two:
how a plan is cut into units of parallel work, why some operations are much
more expensive than others, and how Spark copes when machines fail.

## Thinking Distributed

On a single machine, reading a value from memory takes nanoseconds. In a
cluster, getting a value that lives on *another* machine means serialising
it, sending it over the network, and deserialising it, which is many orders
of magnitude slower. Three rules of thumb follow, and the rest of this page
is mostly about applying them:

1. **Move computation to the data, not data to the computation.** Spark sends
   your query plan to the executors that hold the data.
2. **Move as little data as possible between machines.** Filter early, select
   only the columns you need, and be deliberate about operations that
   redistribute data.
3. **Expect failure.** With enough machines, something is always failing.
   The system has to recover without your help.

## Partitions

A DataFrame's rows are split into **partitions**: chunks of rows that each
live on a single executor. The partition is the unit of parallelism. One task
processes one partition, and a stage can run at most as many tasks at once as
the cluster has slots (CPU cores across all executors).

Where do partitions come from?

- **Reading files**: Spark packs input files into partitions of up to
  `spark.sql.files.maxPartitionBytes` (128 MB by default). A 10 GB table is
  read as roughly 80 partitions.
- **After a shuffle**: the number of output partitions is set by
  `spark.sql.shuffle.partitions`. Open-source Spark defaults to 200; on
  Databricks serverless the default is `auto`, which lets Spark pick the
  number based on the data size.
- **Explicitly**: `df.repartition(n)` or `df.coalesce(n)`, covered
  {ref}`below <repartition-vs-coalesce>`.

On classic compute you can check the count with `df.rdd.getNumPartitions()`.
On serverless the RDD API is unavailable, but you can still see how rows are
spread out with the built-in `spark_partition_id` function:

```python
from pyspark.sql import functions as F

trips = spark.read.table("samples.nyctaxi.trips")

(
    trips
    .groupBy(F.spark_partition_id().alias("partition"))
    .count()
    .orderBy("partition")
    .show()
)
```

Partitions that are too **large** cause memory pressure and spill to disk.
Partitions that are too **small** waste time on per-task scheduling overhead.
A common target is somewhere around 100–200 MB per partition, with at least
as many partitions as the cluster has cores.

## Narrow and Wide Transformations

Transformations fall into two groups depending on whether a task needs data
from other partitions.

- **Narrow transformations** compute each output partition from exactly one
  input partition. `select`, `filter`, `withColumn`, and `union` are narrow.
  Each task can do its work locally, with no network traffic.
- **Wide transformations** need rows from *many* input partitions to compute
  one output partition. `groupBy().agg()`, `join` (in general), `distinct`,
  `orderBy`, and `repartition` are wide. They require a **shuffle**.

```mermaid
:caption: Narrow transformations stay within a partition; wide transformations exchange data between all of them.
:align: center
:name: narrow-vs-wide

graph LR
    subgraph Narrow["Narrow: filter"]
        A1[P1] --> B1[P1']
        A2[P2] --> B2[P2']
        A3[P3] --> B3[P3']
    end
    subgraph Wide["Wide: groupBy"]
        C1[P1] --> D1[P1']
        C1 --> D2[P2']
        C2[P2] --> D1
        C2 --> D2
        C3[P3] --> D1
        C3 --> D2
    end
```

## Shuffles

A **shuffle** redistributes rows so that all rows sharing a key end up in the
same partition. For `groupBy("department")`, every row for "Sales" must
reach the same task, wherever it started. A shuffle has two halves:

1. **Shuffle write**: each task of the upstream stage sorts its rows into
   buckets by the hash of the key and writes the buckets to local disk.
2. **Shuffle read**: each task of the downstream stage fetches its bucket
   from *every* upstream task over the network.

That is disk I/O, serialisation and an all-to-all network exchange, which
makes the shuffle the single most expensive thing Spark does. Most Spark
performance tuning comes down to shuffling less data, or shuffling it less
often.

Spark already limits the damage where it can. For example, `groupBy().agg()`
performs a **partial aggregation** before the shuffle: each task first
computes a per-partition subtotal, so only one row per key per partition
crosses the network, not every input row.

In a physical plan, shuffles appear as `Exchange` operators:

```python
(
    trips
    .groupBy("pickup_zip")
    .agg(F.avg("fare_amount").alias("avg_fare"))
    .explain()
)
```

Look for `Exchange hashpartitioning(pickup_zip, ...)` between a
`HashAggregate` marked as partial and the final `HashAggregate`.

With Photon enabled, as on serverless compute, the same operators appear
under Photon names, for example `PhotonShuffleExchangeSink` and
`PhotonGroupingAgg`. The structure of the plan is the same.

## Jobs, Stages and Tasks

When an action runs, the driver turns the physical plan into a hierarchy of
work:

- A **job** is all the work triggered by one action. A single action can
  launch more than one job, for example when Spark first needs to sample the
  data.
- A job is cut into **stages** at every shuffle boundary. Within a stage, all
  transformations are narrow and are fused together, so each row flows through
  the whole chain without being materialised in between.
- A stage consists of **tasks**, one per partition. All tasks in a stage run
  the same code on different data.

```mermaid
:caption: One action becomes one job, cut into stages at shuffle boundaries, each made of one task per partition.
:align: center

graph LR
    subgraph S1["Stage 1: read, filter, partial agg"]
        T1[Task 1]
        T2[Task 2]
        T3[Task 3]
    end
    subgraph S2["Stage 2: final agg"]
        U1[Task 1]
        U2[Task 2]
    end
    S1 -- shuffle --> S2
    S2 --> R[Result to driver]
```

When a stage has more tasks than the cluster has slots, the tasks run in
successive **waves**. With $T$ tasks and $S$ slots, a stage needs

$$
W = \left\lceil \frac{T}{S} \right\rceil
$$ (eq-task-waves)

waves. The last wave is often only partly full, leaving slots idle, which is
one reason partition counts that are a multiple of the slot count tend to
work well.

:::::{dropdown} Example: Counting Waves
:open:
:color: primary
:icon: pencil
:class-body: example-body

A classic cluster has 4 workers with 8 cores each, so $S = 32$ slots. A stage
reads a table that is split into $T = 1000$ partitions.

**Apply the wave formula, {eq}`eq-task-waves`.**

$$
W = \left\lceil \frac{1000}{32} \right\rceil = \lceil 31.25 \rceil = 32
$$

**Look at the last wave.**

The first 31 waves run $31 \times 32 = 992$ tasks, so the last wave runs only
$1000 - 992 = 8$ tasks while 24 slots sit idle.

The stage needs 32 waves, and the final one uses only a quarter of the
cluster. Rounding the partition count to $992$ or $1024$ would keep every
wave full.
:::::

On classic compute you can watch jobs, stages and tasks in the **Spark UI**.
On serverless there is no Spark UI. Use the **query profile** instead,
reachable from the query's output in a notebook or from the query history.

(join-strategies)=
## Join Strategies

Joins are wide in general: to match keys, rows with the same key from both
sides must meet in the same task. Spark picks among a few strategies:

- **Sort-merge join**: shuffle *both* sides by the join key, sort each
  partition, and merge. Works for any size, but shuffles everything.
- **Broadcast hash join**: if one side is small, send a full copy of it to
  every executor and build a hash table there. The large side is *not*
  shuffled at all. This is usually much faster.
- **Shuffle hash join**: shuffle both sides, then build a hash table per
  partition instead of sorting.

Spark broadcasts automatically when it estimates that one side is below a
size threshold. When you know better than the estimate, give a hint:

```python
zips = spark.createDataFrame(
    [(10001, "Chelsea"), (10003, "East Village"), (10023, "Upper West Side")],
    schema="zip INT, neighbourhood STRING",
)

trips_with_area = trips.join(
    F.broadcast(zips),
    trips.pickup_zip == zips.zip,
    "left",
)
```

The physical plan then shows `BroadcastHashJoin` instead of `SortMergeJoin`.
Only broadcast data that comfortably fits in memory on the driver and on each
executor.

{doc}`DataFrame Relational Operations <../../02_developing_applications_with_apache_spark/03_dataframe_relational_operations>`
covers the join types themselves and shows a broadcast join's physical plan.

(adaptive-query-execution)=
## Adaptive Query Execution

Plans are chosen before execution, from estimates. **Adaptive Query
Execution (AQE)**, on by default since Spark 3.2, re-plans the query between
stages using the actual statistics of the shuffle output. It does three main
things:

- **Coalesces shuffle partitions**: merges many small post-shuffle
  partitions into fewer reasonably sized ones, so you don't have to tune
  `spark.sql.shuffle.partitions` by hand for every query.
- **Switches join strategies**: converts a sort-merge join into a broadcast
  join when one side turns out to be small after filtering.
- **Handles skewed joins**: splits an oversized partition into several
  smaller tasks.

In `explain()` output, AQE plans start with `AdaptiveSparkPlan`. On Databricks
it is enabled by default, and on serverless it is not something you
configure.

## Data Skew

A shuffle sends all rows for one key to one task. If one key is far more
common than the others, say 40% of all trips start in a single zip code,
that task gets far more data than the rest. The stage cannot finish until its
slowest task does, so the whole job waits on one overloaded core while the
others sit idle. This is **data skew**.

Typical signs: a stage where most tasks finish in seconds and a few run for
minutes, or tasks that spill to disk or run out of memory.

Remedies, roughly in order of preference:

1. **Let AQE handle it.** Skew-join handling covers many join cases with no
   code change.
2. **Filter or pre-aggregate** before the shuffle so less data reaches the
   hot key.
3. **Broadcast** the smaller side of a join so the skewed side isn't
   shuffled at all.
4. **Salt the key**: add a random suffix to the hot key so its rows spread
   over several partitions, aggregate, then aggregate again without the salt.

(repartition-vs-coalesce)=
## Controlling Partitioning: `repartition` and `coalesce`

You rarely need to set partitioning by hand, but two methods let you:

- `df.repartition(n)` or `df.repartition(n, "col")` performs a **full
  shuffle** into exactly `n` partitions (hashed by `col` if given). Use it to
  increase parallelism, or to co-locate rows by key before a write.
- `df.coalesce(n)` **merges** existing partitions down to `n` without a
  shuffle. It is cheap, but it can only reduce the count, and it can leave
  partitions unevenly sized. Use it to avoid writing many tiny files.

```python
trips.repartition(64, "pickup_zip")   # shuffle: 64 partitions, by key
trips.coalesce(8)                     # no shuffle: merge into 8 partitions
```

Be careful with `coalesce(1)`: it forces the whole upstream stage onto a
single task, which throws away all parallelism.

## Fault Tolerance

Spark does not replicate intermediate results to survive failures. Instead,
it keeps the **lineage** of every partition: the chain of transformations
that produced it from data in durable storage. If a task fails, the driver
reruns it, on another executor if necessary, and recomputes only the lost
partitions from their inputs. Shuffle files written by completed upstream
tasks are reused where they still exist.

This is why Spark's transformations must be **deterministic**: rerunning a
task must produce the same rows. Functions such as `rand()` without a seed,
or a UDF that calls an external service, can make retries produce different
results.

Spark also uses **speculative execution** for stragglers: when one task runs
much slower than its siblings, a copy can be launched elsewhere and whichever
finishes first wins.

(driver-vs-executor-code)=
## Driver Code versus Executor Code

In a PySpark program, it matters where each line runs:

- Ordinary Python statements (loops, `if`s, variable assignments) run on the
  **driver**, or, with Databricks Connect, in your local Python process.
- DataFrame operations are shipped to and run on the **executors**.
- A Python UDF's body also runs on the **executors**, in separate Python
  worker processes.

Two habits follow from this:

- **Don't loop over rows in Python.** `for row in df.collect(): ...` pulls
  everything to one machine and processes it serially. Express the logic as
  DataFrame operations instead.
- **Don't build plans in large Python loops.** A loop that calls
  `withColumn` hundreds of times creates a very deep plan that is slow to
  analyse. Build a list of column expressions and pass them to a single
  `select`.

```python
# Slow: one plan node per column
for i in range(100):
    trips = trips.withColumn(f"fare_x{i}", F.col("fare_amount") * i)

# Better: one select
trips = trips.select(
    "*",
    *[(F.col("fare_amount") * i).alias(f"fare_x{i}") for i in range(100)],
)
```

## A Short Checklist

When a Spark job is slower than expected, work through:

1. **Read less.** Filter on clustering or partition columns and select only
   the columns you need, so Spark can skip files.
2. **Shuffle less.** Count the `Exchange` operators in `explain()`. Can a
   join be broadcast? Can you aggregate before joining?
3. **Look for skew.** In the Spark UI or query profile, compare the slowest
   task in a stage with the median.
4. **Size partitions sensibly.** Avoid thousands of tiny files and avoid a
   handful of huge partitions.
5. **Keep work off the driver.** No `collect()` on large data, no row loops,
   and prefer built-in functions to Python UDFs.

The {doc}`next section <../04_etl_with_the_dataframe_api/index>` applies
these ideas to a complete ETL pipeline.

## Resources

- [Performance tuning (Apache Spark)](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
- [Diagnose cost and performance issues using the Spark UI (Databricks)](https://docs.databricks.com/aws/en/optimizations/spark-ui-guide/)
- [Set Spark configuration properties on Databricks](https://docs.databricks.com/aws/en/spark/conf)
