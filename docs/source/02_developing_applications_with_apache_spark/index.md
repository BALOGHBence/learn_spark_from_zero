# Developing Applications with Apache Spark

{doc}`Introduction to Apache Spark <../01_introduction_to_apache_spark/index>`
explained how Spark works and walked through a first ETL pipeline. This
chapter is hands-on: each page is a Jupyter notebook that you can run
yourself, top to bottom, against Databricks serverless compute through the
session set up in
{doc}`Setting Up Databricks Connect <../00_getting_started/01_setting_up_databricks_connect>`.

All examples use the `samples.bakehouse` dataset, the sales records of a
fictional chain of bakeries, from the `samples` catalog
([Sample datasets](https://docs.databricks.com/aws/en/discover/databricks-datasets#unity-catalog-datasets)).
{doc}`DataFrame API Basics <01_dataframe_api_basics>` notes what to do if
your workspace doesn't have it. The chapter is organised into four
notebooks:

- {doc}`DataFrame API Basics <01_dataframe_api_basics>`: inspecting data,
  deriving columns, casting under ANSI mode, filtering, conditional logic,
  strings and timestamps, missing values, sorting and de-duplication.
- {doc}`Grouping and Aggregating Data <02_grouping_and_aggregating_data>`:
  `groupBy` and `agg`, counting correctly, conditional aggregates, pivot
  tables, subtotals with `rollup` and `cube`, and window functions.
- {doc}`DataFrame Relational Operations <03_dataframe_relational_operations>`:
  every join type, ambiguous columns, self-joins and range joins, null keys,
  broadcast joins, and set operations.
- {doc}`Working with Complex Data <04_working_with_complex_data>`: arrays,
  higher-order functions, structs, maps, JSON strings and the `VARIANT`
  type.

```{toctree}
:maxdepth: 1
:hidden:

01_dataframe_api_basics
02_grouping_and_aggregating_data
03_dataframe_relational_operations
04_working_with_complex_data
```
