"""
Pydantic schema for the exam question bank.

Every question is tagged with a :class:`Category` (one per section of the
*Databricks Certified Associate Developer for Apache Spark* exam guide) and an
objective id such as ``"3.5"`` that points into :data:`OBJECTIVES`, the
verbatim objective list of the guide. Grouping answers by category shows which
exam section a user is weakest in; grouping by objective narrows it down
further.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)


class Category(StrEnum):
    """The seven sections of the exam guide (Oct 2025)."""

    ARCHITECTURE = "apache_spark_architecture_and_components"
    SPARK_SQL = "using_spark_sql"
    DATAFRAME_API = "developing_dataframe_dataset_api_applications"
    TROUBLESHOOTING_AND_TUNING = "troubleshooting_and_tuning"
    STRUCTURED_STREAMING = "structured_streaming"
    SPARK_CONNECT = "using_spark_connect"
    PANDAS_API_ON_SPARK = "using_pandas_api_on_spark"

    @property
    def section(self) -> int:
        """The section number in the exam guide."""
        return list(Category).index(self) + 1

    @property
    def section_title(self) -> str:
        """The section title as written in the exam guide."""
        return _CATEGORY_TITLES[self]


_CATEGORY_TITLES: dict[Category, str] = {
    Category.ARCHITECTURE: "Apache Spark Architecture and Components",
    Category.SPARK_SQL: "Using Spark SQL",
    Category.DATAFRAME_API: (
        "Developing Apache Spark™ DataFrame/DataSet API Applications"
    ),
    Category.TROUBLESHOOTING_AND_TUNING: (
        "Troubleshooting and Tuning Apache Spark DataFrame API Applications"
    ),
    Category.STRUCTURED_STREAMING: "Structured Streaming",
    Category.SPARK_CONNECT: "Using Spark Connect to deploy applications",
    Category.PANDAS_API_ON_SPARK: "Using Pandas API on Spark",
}


@dataclass(frozen=True)
class Objective:
    """One objective of the exam guide, copied verbatim."""

    id: str
    category: Category
    text: str


def _objectives(category: Category, *texts: str) -> dict[str, Objective]:
    return {
        f"{category.section}.{i}": Objective(f"{category.section}.{i}", category, text)
        for i, text in enumerate(texts, start=1)
    }


OBJECTIVES: dict[str, Objective] = {
    **_objectives(
        Category.ARCHITECTURE,
        "Identify the advantages and challenges of implementing Spark.",
        "Identify the role of core components of Apache Spark™'s Architecture, "
        "including cluster, driver node, worker nodes/executors, CPU cores, and "
        "memory.",
        "Describe the architecture of Apache Spark™, including DataFrame and "
        "Dataset concepts, SparkSession lifecycle, caching, storage levels, and "
        "garbage collection.",
        "Explain the Apache Spark™ Architecture execution hierarchy.",
        "Configure Spark partitioning in distributed data processing, including "
        "shuffles and partitions",
        "Describe the execution patterns of the Apache Spark™ engine, including "
        "actions, transformations, and lazy evaluation.",
        "Identify the features of the Apache Spark Modules, including Core, Spark "
        "SQL, DataFrames, Pandas API on Spark, Structured Streaming, and MLib.",
    ),
    **_objectives(
        Category.SPARK_SQL,
        "Utilize common data sources such as JDBC, files, etc., to efficiently "
        "read from and write to Spark DataFrames using Spark SQL, including "
        "overwriting and partitioning by column.",
        "Execute SQL queries directly on files, including ORC Files, JSON Files, "
        "CSV Files, Text Files, and Delta Files, and understand the different "
        "save modes for outputting data in Spark SQL.",
        "Save data to persistent tables while applying sorting and partitioning "
        "to optimize data retrieval.",
        "Register DataFrames as temporary views in Spark SQL, allowing them to be "
        "queried with SQL syntax.",
    ),
    **_objectives(
        Category.DATAFRAME_API,
        "Manipulate columns, rows, and table structures by adding, dropping, "
        "splitting, renaming column names, applying filters, and exploding "
        "arrays.",
        "Perform data deduplication and validation operations on DataFrames.",
        "Perform aggregate operations on DataFrames such as count, approximate "
        "count distinct, and mean, summary.",
        "Manipulate and utilize Date data type, such as Unix epoch to date "
        "string, and extract date component.",
        "Combine DataFrames with operations such as Inner join, left join, "
        "broadcast join, multiple keys, cross join, union, and union all.",
        "Manage input and output operations by writing, overwriting, and reading "
        "DataFrames with schemas.",
        "Perform operations on DataFrames such as sorting, iterating, printing "
        "schema, and conversion between DataFrame and sequence/list formats.",
        "Create and invoke user-defined functions with or without stateful "
        "operators, including StateStores.",
        "Describe different types of variables in Spark, including broadcast "
        "variables and accumulators.",
        "Describe the purpose and implementation of broadcast joins",
    ),
    **_objectives(
        Category.TROUBLESHOOTING_AND_TUNING,
        "Implement performance tuning strategies & optimize cluster utilization, "
        "including partitioning, repartitioning, coalescing, identifying data "
        "skew, and reducing shuffling",
        "Describe Adaptive Query Execution (AQE) and its benefits.",
        "Perform logging and monitoring of Spark applications - publish, "
        "customize, and analyze Driver logs and Executor logs to diagnose "
        "out-of-memory errors, cluster underutilization, etc.",
    ),
    **_objectives(
        Category.STRUCTURED_STREAMING,
        "Explain the Structured Streaming engine in Spark, including its "
        "functions, programming model, micro-batch processing, exactly-once "
        "semantics, and fault tolerance mechanisms.",
        "Create and write Streaming DataFrames and Streaming Datasets, including "
        "the basic output modes and output sinks.",
        "Perform basic operations on Streaming DataFrames and Streaming Datasets, "
        "such as selection, projection, window and aggregation.",
        "Perform Streaming Deduplication in Structured Streaming, both with and "
        "without watermark usage.",
    ),
    **_objectives(
        Category.SPARK_CONNECT,
        "Describe the features of Spark Connect.",
        "Describe the different deployment mode types (Client, Cluster, Local) in "
        "the Apache Spark™ environment.",
    ),
    **_objectives(
        Category.PANDAS_API_ON_SPARK,
        "Explain the advantages of using Pandas API on Spark.",
        "Create and invoke Pandas UDF.",
    ),
}

#: Hosts that count as curated, official documentation.
ALLOWED_SOURCE_HOSTS: frozenset[str] = frozenset(
    {"docs.databricks.com", "spark.apache.org"}
)


def _check_source_host(url: HttpUrl) -> HttpUrl:
    if url.host not in ALLOWED_SOURCE_HOSTS:
        raise ValueError(
            f"source_url host {url.host!r} is not curated documentation; "
            f"use one of {sorted(ALLOWED_SOURCE_HOSTS)}"
        )
    return url


SourceUrl = Annotated[HttpUrl, AfterValidator(_check_source_host)]


class Verdict(StrEnum):
    """How an answer option relates to the question."""

    #: The answer to the question.
    CORRECT = "correct"
    #: Factually wrong.
    INCORRECT = "incorrect"
    #: Right in part, but incomplete or wrong in a detail.
    PARTIALLY_CORRECT = "partially_correct"
    #: A true statement that does not answer this question.
    TRUE_BUT_IRRELEVANT = "true_but_irrelevant"


class Answer(BaseModel):
    """One answer option with the reasoning behind its verdict."""

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    text: str = Field(min_length=1)
    verdict: Verdict
    justification: str = Field(min_length=1)

    @property
    def is_correct(self) -> bool:
        return self.verdict is Verdict.CORRECT


class Question(BaseModel):
    """A single multiple-choice exam question with exactly one correct answer.

    ``question`` and the answers' ``text`` and ``justification`` are Markdown,
    so code is written in fenced or inline code blocks.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    id: str = Field(pattern=r"^\d\.\d{1,2}-\d{3}$", examples=["3.5-012"])
    category: Category
    objective: str = Field(examples=["3.5"])
    question: str = Field(min_length=1)
    answers: list[Answer] = Field(min_length=4, max_length=4)
    source_url: SourceUrl

    @model_validator(mode="after")
    def _check_consistency(self) -> Self:
        objective = OBJECTIVES.get(self.objective)
        if objective is None:
            raise ValueError(f"unknown objective {self.objective!r}")
        if objective.category is not self.category:
            raise ValueError(
                f"objective {self.objective} belongs to {objective.category}, "
                f"not {self.category}"
            )
        if not self.id.startswith(f"{self.objective}-"):
            raise ValueError(f"id {self.id!r} must start with {self.objective!r}-")
        texts = [a.text for a in self.answers]
        if len(set(texts)) != len(texts):
            raise ValueError("answer texts must be unique")
        if sum(a.is_correct for a in self.answers) != 1:
            raise ValueError("exactly one answer must have the verdict 'correct'")
        return self

    @property
    def correct_index(self) -> int:
        """Zero-based position of the correct answer in :attr:`answers`."""
        return next(i for i, a in enumerate(self.answers) if a.is_correct)

    @property
    def correct_answer(self) -> Answer:
        """The correct answer option."""
        return self.answers[self.correct_index]

    @property
    def objective_text(self) -> str:
        """The verbatim objective from the exam guide."""
        return OBJECTIVES[self.objective].text

    def is_correct(self, answer: str | int) -> bool:
        """Check a response given as the answer text or its zero-based index."""
        if isinstance(answer, int):
            return answer == self.correct_index
        return answer.strip() == self.correct_answer.text
