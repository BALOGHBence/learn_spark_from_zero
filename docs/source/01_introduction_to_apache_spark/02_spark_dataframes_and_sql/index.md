# Spark DataFrames and SQL

The DataFrame is the structure you will use for almost all Spark work: a
distributed table with named, typed columns that you can query with either
Python methods or SQL. This section introduces the abstraction and then shows
how to get data into and out of it on Databricks.

- {doc}`Introduction to DataFrames <01_introduction_to_dataframes>`: schemas,
  rows and columns; transformations versus actions; lazy evaluation; and how
  the DataFrame API and Spark SQL relate.
- {doc}`Reading and Writing Data <02_reading_and_writing_data>`: Unity Catalog
  tables and volumes, file formats, schemas, and save modes.

```{toctree}
:maxdepth: 1
:hidden:

01_introduction_to_dataframes
02_reading_and_writing_data
```
