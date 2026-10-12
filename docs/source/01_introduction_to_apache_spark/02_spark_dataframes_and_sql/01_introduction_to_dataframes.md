# Introduction to DataFrames

{doc}`Spark Runtime Architecture <../01_apache_spark_runtime_architecture/02_spark_runtime_architecture>`
showed that the driver turns your code into a query plan and the executors
run it. The **DataFrame** is the API you use to write that code. This page
covers what a DataFrame is, how to build and transform one, and why nothing
actually runs until you ask for a result.

All examples assume a session created as in
{ref}`Starting a Session <spark-session-start>`.

## What a DataFrame Is

A DataFrame is a dataset organised into **named columns**, like a SQL table
or a spreadsheet. If you know pandas, the shape will feel familiar, but there
are three important differences:

- **It is distributed.** The rows are split into *partitions* spread across
  the executors. No single machine needs to hold the whole thing.
- **It is immutable.** Every operation returns a *new* DataFrame. Nothing is
  modified in place, so you must assign the result to a variable.
- **It is lazy.** A DataFrame doesn't hold data. It holds a *plan* for
  producing data, which runs only when an action asks for a result.

Every DataFrame has three parts:

- **Schema**: the column names and their data types. It can be declared
  explicitly, read from a source such as a table, or inferred from data.
- **Rows**: records, represented in Python as `pyspark.sql.Row` objects.
- **Columns**: expressions over the rows, represented as
  `pyspark.sql.Column` objects. A column can be a simple value (`string`,
  `int`, `double`, `timestamp`, ...) or a complex one (`array`, `map`,
  `struct`, or the semi-structured `variant` type added in Spark 4.0).

## Creating a DataFrame

In practice most DataFrames come from tables or files (see
{doc}`Reading and Writing Data <02_reading_and_writing_data>`). For learning
and testing, it is handy to build a small one from Python data:

```python
employees = spark.createDataFrame(
    [
        ("Alice", "Engineering", 85000),
        ("Bob", "Engineering", 72000),
        ("Carla", "Sales", 64000),
        ("Dan", "Sales", 58000),
        ("Eve", "Marketing", 70000),
    ],
    schema="name STRING, department STRING, salary INT",
)

employees.printSchema()
```

```text
root
 |-- name: string (nullable = true)
 |-- department: string (nullable = true)
 |-- salary: integer (nullable = true)
```

The `schema` argument is a DDL string, the same column syntax you would use
in `CREATE TABLE`. You can also build schemas from `pyspark.sql.types`
(`StructType`, `StructField`, ...), which is more verbose but easier to
generate programmatically.

To look at the data, use `show()`. In a Databricks notebook, `display(df)`
renders an interactive table with sorting and charts instead.

```python
employees.show()
```

```text
+-----+-----------+------+
| name| department|salary|
+-----+-----------+------+
|Alice|Engineering| 85000|
|  Bob|Engineering| 72000|
|Carla|      Sales| 64000|
|  Dan|      Sales| 58000|
|  Eve|  Marketing| 70000|
+-----+-----------+------+
```

## Working with Columns

Most DataFrame methods take **column expressions**. There are several
equivalent ways to refer to a column:

```python
from pyspark.sql import functions as F

employees.select("salary")              # a column name as a string
employees.select(F.col("salary"))       # an explicit Column object
employees.select(employees["salary"])   # bound to this specific DataFrame
employees.select(employees.salary)      # attribute access (avoid: breaks on names with spaces)
```

`F.col(...)` is the most common choice in production code. Column objects
support arithmetic, comparison and boolean operators, and the
`pyspark.sql.functions` module (conventionally imported as `F`) contains
hundreds of built-in functions for strings, dates, arrays, aggregation and
more:

```python
employees.select(
    F.upper("name").alias("name_upper"),
    (F.col("salary") * 1.1).alias("salary_after_raise"),
)
```

:::{admonition} Note: Prefer Built-in Functions over Python UDFs
:class: note

Built-in functions run inside the Spark engine, where Catalyst can optimise
them and Photon can vectorise them. A Python user-defined function (UDF)
forces Spark to ship every row to a Python process and back. Reach for a UDF
only when no combination of built-in functions can express what you need.
:::

## Transformations

A **transformation** takes a DataFrame and returns a new one. These are the
ones you will use constantly:

| Method | What it does | SQL equivalent |
| --- | --- | --- |
| `select(...)` | Choose or compute columns | `SELECT` |
| `withColumn(name, expr)` | Add or replace one column | `SELECT *, expr AS name` |
| `withColumnRenamed(old, new)` | Rename a column | `SELECT old AS new` |
| `drop(...)` | Remove columns | `SELECT` without them |
| `filter(cond)` / `where(cond)` | Keep matching rows | `WHERE` |
| `groupBy(...).agg(...)` | Aggregate per group | `GROUP BY` |
| `join(other, on, how)` | Combine two DataFrames | `JOIN` |
| `orderBy(...)` / `sort(...)` | Sort rows | `ORDER BY` |
| `distinct()` / `dropDuplicates(...)` | Remove duplicate rows | `SELECT DISTINCT` |
| `limit(n)` | Keep the first *n* rows | `LIMIT` |
| `union(other)` / `unionByName(other)` | Stack rows | `UNION ALL` |

Because each transformation returns a DataFrame, they chain naturally.
Wrapping the chain in parentheses lets you put one step per line:

```python
engineering = (
    employees
    .filter(F.col("department") == "Engineering")
    .withColumn("monthly_salary", F.col("salary") / 12)
    .select("name", "monthly_salary")
)
```

:::::{dropdown} Example: Average Salary per Department
:open:
:color: primary
:icon: pencil
:class-body: example-body

Using the `employees` DataFrame from above, which department pays the most
on average?

**Group and aggregate.**

```python
avg_salary = (
    employees
    .groupBy("department")
    .agg(F.avg("salary").alias("avg_salary"))
)
```

**Sort and show the result.**

```python
avg_salary.orderBy(F.desc("avg_salary")).show()
```

```text
+-----------+----------+
| department|avg_salary|
+-----------+----------+
|Engineering|   78500.0|
|  Marketing|   70000.0|
|      Sales|   61000.0|
+-----------+----------+
```

Engineering averages $(85000 + 72000)/2 = 78500$, Sales
$(64000 + 58000)/2 = 61000$, and Marketing's single employee gives $70000$.
Note that `avg` returns a `double` even though `salary` is an `INT`.
:::::

## Actions

An **action** asks Spark for a result, either returning it to your Python
program or writing it somewhere. Only actions make Spark do any work.

| Action | Returns |
| --- | --- |
| `show(n)` / `display(df)` | Prints or renders the first rows |
| `count()` | Number of rows, as a Python `int` |
| `collect()` | *All* rows as a list of `Row` objects on the driver |
| `take(n)` / `head(n)` / `first()` | The first rows as `Row` objects |
| `toPandas()` | All rows as a pandas DataFrame on the driver |
| `df.write...save(...)` / `saveAsTable(...)` | Writes the result to storage |

`collect()` and `toPandas()` pull the entire result into the driver's memory,
so use them only on results you know are small, such as an aggregate. In
production pipelines the write is usually the only action: every extra
action re-runs the plan (or the part of it that is needed) from the
beginning.

## Lazy Evaluation

When you call a transformation, Spark only records it. The work happens when
an action runs, and at that point Spark can optimise the *whole* chain
together.

```python
trips = spark.read.table("samples.nyctaxi.trips")      # nothing read yet

long_trips = (
    trips
    .filter(F.col("trip_distance") > 10)               # nothing filtered yet
    .select("tpep_pickup_datetime", "trip_distance", "fare_amount")
)

long_trips.count()                                     # now Spark runs a job
```

Because the optimiser sees the whole query, it can, for example, read only
the three columns that are actually used and push the `trip_distance > 10`
filter into the table scan, so files that cannot contain matching rows are
skipped entirely. You can inspect the plan Spark chose with `explain()`:

```python
long_trips.explain()             # physical plan only
long_trips.explain(mode="formatted")  # physical plan with details per operator
```

Learning to read these plans pays off when diagnosing performance problems.
{doc}`Distributed Systems Programming Fundamentals <../03_distributed_systems_programming_fundamentals/03_distributed_systems_programming_fundamentals>`
explains what the operators in them mean.

:::{admonition} Note: Lazy Analysis under Spark Connect
:class: note

On serverless compute and Databricks Connect, Spark defers *checking* your
plan as well as executing it. A misspelt column name is reported when you
first access `df.columns` or `df.schema`, or run an action, not on the line
that contains the typo. See
{ref}`the Spark Connect section <spark-connect-practical-consequences>` of the
architecture page.
:::

## DataFrames and SQL Are the Same Engine

Anything you can write with the DataFrame API you can also write in SQL, and
both produce the same optimised plan. You can switch between them freely:

```python
# DataFrame -> SQL: register a temporary view
employees.createOrReplaceTempView("employees")

top_departments = spark.sql("""
    SELECT department, avg(salary) AS avg_salary
    FROM employees
    GROUP BY department
    ORDER BY avg_salary DESC
""")

# SQL -> DataFrame: the result of spark.sql is an ordinary DataFrame
top_departments.filter(F.col("avg_salary") > 65000).show()
```

Unity Catalog tables can be queried directly by their three-level name
without registering anything:

```python
spark.sql("SELECT count(*) AS n FROM samples.nyctaxi.trips").show()
```

`spark.sql` also accepts named parameters, which is safer than formatting
values into the query string yourself:

```python
spark.sql(
    "SELECT * FROM samples.nyctaxi.trips WHERE trip_distance > :min_distance",
    args={"min_distance": 10},
)
```

Inside a DataFrame chain, `F.expr("...")` and `selectExpr("...")` let you use
SQL snippets where that is shorter:

```python
employees.selectExpr("name", "salary * 12 AS yearly_cost")
```

Which one to use is mostly taste: SQL is often clearer for ad hoc analysis,
while the DataFrame API is easier to test, reuse and compose in Python code.

Next, {doc}`Reading and Writing Data <02_reading_and_writing_data>` replaces
these hand-built DataFrames with real tables and files.

## Resources

- [PySpark DataFrame quickstart (Apache Spark)](https://spark.apache.org/docs/latest/api/python/getting_started/quickstart_df.html)
- [PySpark basics (Databricks)](https://docs.databricks.com/aws/en/pyspark/basics)
- [Tutorial: Load and transform data using Spark DataFrames (Databricks)](https://docs.databricks.com/aws/en/getting-started/dataframes)
