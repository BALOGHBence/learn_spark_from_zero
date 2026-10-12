# Apache Spark Runtime Architecture

Before writing any Spark code it pays to know what Spark actually *is* and
what happens on the other side of the network when you call `df.show()`.
This section covers both.

- {doc}`What Is Apache Spark? <01_what_is_apache_spark>`: the problem Spark
  solves, its history, and the components that make up the Spark ecosystem.
- {doc}`Spark Runtime Architecture <02_spark_runtime_architecture>`: drivers,
  executors and cluster managers; Spark Classic versus Spark Connect; and how
  Databricks serverless compute fits in.

```{toctree}
:maxdepth: 1
:hidden:

01_what_is_apache_spark
02_spark_runtime_architecture
```
