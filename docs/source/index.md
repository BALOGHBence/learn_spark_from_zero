# Learn Spark from Zero

A hands-on course that takes you from no Apache Spark knowledge to ready for the **Databricks Certified Associate Developer for Apache Spark** exam. You write and run PySpark from your own editor against Databricks serverless compute, and you check what you've learned with a bank of 1,000 exam-style questions.

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} {octicon}`rocket;1.5em` Start here
:link: 00_getting_started/01_setting_up_databricks_connect
:link-type: doc

Connect your local Python environment to Databricks serverless compute so every example in the course runs as written.
:::

:::{grid-item-card} {octicon}`checklist;1.5em` Quiz yourself
:link: 00_getting_started/02_quizzing_yourself_with_claude_code
:link-type: doc

Find your weak spots with short exam-style quizzes on one section, objective or topic.
:::

:::{grid-item-card} {octicon}`stopwatch;1.5em` Take a mock exam
:link: 00_getting_started/03_taking_a_mock_exam_with_claude_code
:link-type: doc

Sit a full 45-question practice exam that covers every objective, graded only after you submit.
:::
::::

## Who This Course Is For

You know some Python and want to learn Apache Spark well enough to use it at work and pass the certification. You don't need any previous Spark or distributed-computing experience. The course starts with what Spark is and why it exists, and builds up to streaming and performance tuning.

The pages target Apache Spark 4.x as it runs on Databricks. Where Databricks behaves differently from open-source Spark, the pages say so. Every claim links to the official documentation on [docs.databricks.com](https://docs.databricks.com) or [spark.apache.org](https://spark.apache.org/docs/latest/), so you can check it yourself.

## What You Need

- **A Databricks workspace** with Unity Catalog and serverless compute. Databricks Free Edition is enough ([Databricks Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition)).
- **Python 3.12, [uv](https://docs.astral.sh/uv/) and the Databricks CLI** on your machine, to run the notebooks locally through Databricks Connect. {doc}`Setting Up Databricks Connect <00_getting_started/01_setting_up_databricks_connect>` walks you through the setup.
- **A copy of the [course repository](https://github.com/BALOGHBence/learn_spark_from_zero)**, which holds the notebooks, the question bank and the Claude Code skills.
- **Optional: [Claude Code](https://claude.com/claude-code)**, to run the quizzes and the mock exam.

## Course Map

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} 0. Getting Started
:link: 00_getting_started/index
:link-type: doc

Set up Databricks Connect, and learn how to quiz yourself and take a mock exam with Claude Code.
:::

:::{grid-item-card} 1. Introduction to Apache Spark
:link: 01_introduction_to_apache_spark/index
:link-type: doc

What Spark is, how an application runs across a driver and executors, DataFrames and Spark SQL, partitions and shuffles, and a first ETL pipeline.
:::

:::{grid-item-card} 2. Developing Applications with Apache Spark
:link: 02_developing_applications_with_apache_spark/index
:link-type: doc

The DataFrame API in depth: transformations, grouping and aggregation, window functions, joins, set operations and complex data types.
:::

:::{grid-item-card} 3. Stream Processing and Analysis
:link: 03_stream_processing_and_analysis/index
:link-type: doc

Structured Streaming: sources, sinks, output modes, triggers and checkpoints, windows and watermarks, and real-time mode.
:::

:::{grid-item-card} 4. Monitoring and Optimizing Spark Workloads on Databricks
:link: 04_monitoring_and_optimizing_spark_workloads_on_databricks/index
:link-type: doc

Query plans and the Spark UI, Delta Lake, and making workloads faster and cheaper with data skipping, join strategies and skew handling.
:::

:::{grid-item-card} 5. Exam Readiness
:link: 05_exam_readiness/index
:link-type: doc

Hands-on tasks, each mapped to exam objectives, that you should be able to complete from memory before you book the exam.
:::
::::

## How to Use This Course

1. **Set up your environment** with {doc}`Setting Up Databricks Connect <00_getting_started/01_setting_up_databricks_connect>`, so you can run every notebook yourself.
2. **Diagnose before you study.** Take a short quiz on an exam section first, as described in {doc}`Quizzing Yourself with Claude Code <00_getting_started/02_quizzing_yourself_with_claude_code>`, and spend your time on the objectives you miss.
3. **Work through the chapters in order.** Each chapter builds on the previous one. Run the notebooks top to bottom rather than only reading them.
4. **Check your readiness.** When you've finished the chapters, {doc}`take a mock exam <00_getting_started/03_taking_a_mock_exam_with_claude_code>` and complete the {doc}`hands-on tasks <05_exam_readiness/01_hands_on_tasks>` from memory.

## The Exam at a Glance

The exam has 45 scored multiple-choice questions and a 90-minute time limit. No test aids are allowed, not even the API documentation, and Databricks recommends at least six months of hands-on experience with the tasks in the exam guide ([Databricks Certified Associate Developer for Apache Spark](https://www.databricks.com/learn/certification/apache-spark-developer-associate)). The exam outline has seven sections, weighted as follows on the same page:

| Section | Weight |
| --- | ---: |
| 1. Apache Spark Architecture and Components | 20% |
| 2. Using Spark SQL | 20% |
| 3. Developing Apache Spark DataFrame/DataSet API Applications | 30% |
| 4. Troubleshooting and Tuning Apache Spark DataFrame API Applications | 10% |
| 5. Structured Streaming | 10% |
| 6. Using Spark Connect to deploy applications | 5% |
| 7. Using Pandas API on Apache Spark | 5% |

The course follows the October 2025 version of the exam guide, which is in the repository's `resources/` folder. Databricks asks candidates to re-check the exam guide shortly before their exam, so compare it with the current version on the certification page.

:::{admonition} Note: An Independent Course
:class: note

This course isn't affiliated with or endorsed by Databricks. The practice questions are written by an AI model and grounded in the official documentation, but they aren't official exam items and they aren't calibrated against the real exam's difficulty.
:::

```{toctree}
:caption: Start Here
:hidden:

00_getting_started/index
```

```{toctree}
:caption: Chapters
:hidden:

01_introduction_to_apache_spark/index
02_developing_applications_with_apache_spark/index
03_stream_processing_and_analysis/index
04_monitoring_and_optimizing_spark_workloads_on_databricks/index
```

```{toctree}
:caption: Exam Preparation
:hidden:

05_exam_readiness/index
```

```{toctree}
:caption: For Maintainers
:hidden:

99_maintaining_this_course/index
```
