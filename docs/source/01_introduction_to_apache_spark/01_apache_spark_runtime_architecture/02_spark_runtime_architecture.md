# Spark Runtime Architecture

{doc}`What Is Apache Spark? <01_what_is_apache_spark>` described Spark as an
engine that splits work across many machines. This page shows how that split
is organised: which processes exist, what each one does, and how your
Python code (running in a notebook or on your laptop) reaches them.

## The Building Blocks of a Spark Application

A running Spark program is called a **Spark application**. Every application
has the same three kinds of participants.

```mermaid
:caption: A classic Spark application. The driver plans, the executors do the work.
:align: center
:name: spark-classic-architecture

graph LR
    subgraph DriverProc[Driver]
        SS[SparkSession]
    end
    DriverProc <--> CM[Cluster manager]
    DriverProc --> E1
    DriverProc --> E2
    DriverProc --> E3
    subgraph W1[Worker node 1]
        E1[Executor]
    end
    subgraph W2[Worker node 2]
        E2[Executor]
    end
    subgraph W3[Worker node 3]
        E3[Executor]
    end
```

**The driver** is the process that runs your program's `main` logic and owns
the `SparkSession`. It:

- turns your DataFrame or SQL code into a logical plan, optimises it, and
  produces a physical plan;
- splits the physical plan into **jobs**, **stages** and **tasks**;
- schedules tasks onto executors and tracks their progress;
- collects results that you ask for explicitly (for example with `collect()`
  or `show()`).

**Executors** are worker processes, usually one per worker node, that run the
tasks the driver sends them. Each executor has a fixed number of CPU cores,
and each core can run one task at a time. These task-sized units of
parallelism are often called **slots**: a cluster with 4 executors of 8 cores
each has 32 slots, so it can process 32 tasks at once. Executors also hold
data in memory and on local disk between steps.

**The cluster manager** allocates machines and starts executors. Open-source
Spark supports Standalone, YARN and Kubernetes cluster managers. On
Databricks, the platform plays this role, so you never configure one
yourself.

:::{admonition} Note: The Driver Is a Single Point of Coordination
:class: note

There is exactly one driver per application. Everything that has to be seen
"all at once", such as the final result of `collect()` or a pandas
DataFrame created with `toPandas()`, must fit in driver memory. Pulling a
large distributed dataset back to the driver is one of the most common ways
to crash a Spark application.
:::

## From Code to Tasks

When you trigger a computation, the driver goes through the same pipeline
every time:

```mermaid
:caption: How a DataFrame query becomes tasks running on executors.
:align: center

graph LR
    A[DataFrame / SQL code] --> B[Unresolved logical plan]
    B --> C[Analyzed logical plan]
    C --> D[Optimized logical plan]
    D --> E[Physical plan]
    E --> F[Jobs, stages, tasks]
    F --> G[Executors]
```

1. **Analysis** resolves table and column names against the catalog (Unity
   Catalog on Databricks) and checks types. A typo in a column name fails
   here.
2. **Logical optimisation** (Catalyst) rewrites the plan: it pushes filters
   down towards the data source, drops unused columns and folds constants.
3. **Physical planning** picks concrete algorithms, such as which join
   strategy to use.
4. **Execution** cuts the physical plan into stages at every point where data
   must be redistributed between machines, and each stage into one task per
   data partition.

Jobs, stages, tasks and partitions get their own treatment in
{doc}`Distributed Systems Programming Fundamentals <../03_distributed_systems_programming_fundamentals/03_distributed_systems_programming_fundamentals>`.
For now, the important point is that the driver plans and the executors
execute.

## Spark Classic and Spark Connect

The diagram above shows **Spark Classic**: your code runs *inside* the driver
process, in the same JVM as the Spark engine (PySpark talks to it through a
local bridge). This is simple, but it ties your application tightly to the
cluster. You cannot run your code on a laptop against a remote cluster, and a
misbehaving notebook can take down the driver for everyone sharing it.

**Spark Connect**, which became a first-class part of Spark in Spark 4.0,
splits the driver in two. A thin **client** library builds *unresolved*
query plans and sends them over gRPC to a **Spark Connect server**, which
analyses, optimises and executes them on the cluster and streams results
back.

```mermaid
:caption: Spark Connect. The client only builds plans; the server does all analysis and execution.
:align: center
:name: spark-connect-architecture

graph LR
    subgraph Client[Your machine or notebook]
        Code[Python code] --> Lib[Spark Connect client]
    end
    Lib -- "unresolved plan (gRPC)" --> Server
    Server -- "results (Arrow batches)" --> Lib
    subgraph Cluster[Spark cluster]
        Server[Spark Connect server / driver] --> Ex1[Executor]
        Server --> Ex2[Executor]
    end
```

The DataFrame API looks identical in both modes. What changes is *when* work
happens:

| Aspect | Spark Classic | Spark Connect |
| --- | --- | --- |
| Query execution | Lazy | Lazy |
| Transformations (`filter`, `select`, ...) | Analysed eagerly | Analysed lazily, on the server |
| Schema access (`df.columns`, `df.schema`) | Local | One round trip to the server (then cached) |
| Temporary views | Plan captured at creation | Name resolved at execution |
| Python UDFs | Serialised at creation | Serialised at execution |

### Where Spark Connect Is Used on Databricks

Spark Connect is the protocol behind:

- **Serverless compute** for notebooks, jobs and pipelines;
- **Databricks Connect**, the client library this course uses to run code
  from your IDE (see
  {doc}`Setting Up Databricks Connect <../../00_getting_started/01_setting_up_databricks_connect>`);
- Python notebooks on classic compute with **standard** access mode
  (Databricks Runtime 14.3 and above).

In other words, every example in this course runs through Spark Connect.

(spark-connect-practical-consequences)=
### Practical Consequences

Because analysis is deferred, **errors appear later** than you might expect.
Referencing a column that does not exist does not fail on the `filter` line;
it fails when you first access the schema or run an action.

:::::{dropdown} Example: Where a Bad Column Name Fails
:open:
:color: primary
:icon: pencil
:class-body: example-body

We start a serverless session through Databricks Connect and reference a
column that does not exist in the `samples.nyctaxi.trips` table.

**Build the DataFrame.**

```python
from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.serverless().profile("free-edition").getOrCreate()

trips = spark.read.table("samples.nyctaxi.trips")
bad = trips.filter("tip_amount > 5")  # no error yet: the plan is unresolved
```

**Force analysis.**

```python
try:
    bad.columns  # triggers an analysis round trip to the server
except Exception as e:
    print(type(e).__name__)
```

The `filter` line succeeds because the client never checks column names.
The failure surfaces as an `AnalysisException` (`UNRESOLVED_COLUMN`) the
first time anything needs a resolved plan. If you want a `try` block to catch
analysis errors, put a schema access or an action inside it.
:::::

Two other behaviours are worth knowing early:

- **Temporary views are looked up by name at execution time.** If you
  replace a temp view, DataFrames created from the old one will read the new
  data. Give temp views unique names when that matters.
- **Python UDFs capture variables at execution time**, not when the UDF is
  defined. Build UDFs that depend on outer variables in a small factory
  function so each one binds the value you intended.

## Databricks Compute Options

Databricks offers several kinds of compute that can run Spark:

- **Serverless compute**: Databricks starts, sizes and scales the machines
  for you, and you pay only while work runs. It is the only option in
  Databricks Free Edition, and it is what this course uses.
  Serverless uses Spark Connect exclusively, which brings some limits:
  - no RDD API and no direct `SparkContext` access;
  - `df.cache()`, `df.persist()` and `CACHE TABLE` raise an error;
  - most Spark configuration properties cannot be set;
  - global temporary views are not supported (session temp views are);
  - there is no Spark UI; use the query profile instead;
  - ANSI SQL mode is on and the session time zone defaults to `Etc/UTC`.
- **Classic compute**: clusters you configure yourself (instance types,
  number of workers, autoscaling, Databricks Runtime version). **Standard**
  access mode lets several users share a cluster with isolation between them
  (and uses Spark Connect for Python); **dedicated** access mode assigns the
  cluster to a single user or group and gives full access to Spark Classic
  features such as RDDs and the Spark UI.
- **SQL warehouses**: compute tuned for SQL and BI queries. They run only
  SQL, so you won't use them for the DataFrame examples here.

Serverless notebooks and jobs run on a versioned **environment** that pins
the client APIs. Environment version 6 ships Python 3.12 and Databricks
Connect 19, which is why this project pins `databricks-connect==19.1.*` in
`pyproject.toml`.

(spark-session-start)=
## Starting a Session

Everything starts with a `SparkSession`. In a Databricks notebook one already
exists as `spark`. From your IDE, create one with Databricks Connect:

```python
from databricks.connect import DatabricksSession

spark = (
    DatabricksSession.builder
    .serverless()
    .profile("free-edition")  # the CLI profile you created during setup
    .getOrCreate()
)
```

This repository wraps the same logic in `project.utils.sparksession`, which
falls back to a plain local `SparkSession` when Databricks Connect is not
installed:

```python
from project.utils.sparksession import get_spark_session

spark = get_spark_session(profile="free-edition")
```

With a session in hand, the next step is the main data abstraction you will
use with it:
{doc}`Introduction to DataFrames <../02_spark_dataframes_and_sql/01_introduction_to_dataframes>`.

## Resources

- [Cluster mode overview (Apache Spark)](https://spark.apache.org/docs/latest/cluster-overview.html)
- [Spark Connect overview (Apache Spark)](https://spark.apache.org/docs/latest/spark-connect-overview.html)
- [Compare Spark Connect to Spark Classic (Databricks)](https://docs.databricks.com/aws/en/spark/connect-vs-classic)
- [Serverless compute limitations (Databricks)](https://docs.databricks.com/aws/en/compute/serverless/limitations)
- [Serverless environment versions (Databricks)](https://docs.databricks.com/aws/en/release-notes/serverless/environment-version/)
