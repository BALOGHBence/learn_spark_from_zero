# Learn Spark from Zero

[![Read the course](https://img.shields.io/badge/Read%20the%20course-baloghbence.github.io-0969da?style=for-the-badge)](https://baloghbence.github.io/learn_spark_from_zero/)
[![Deploy docs to Pages](https://github.com/BALOGHBence/learn_spark_from_zero/actions/workflows/docs.yml/badge.svg)](https://github.com/BALOGHBence/learn_spark_from_zero/actions/workflows/docs.yml)

**📖 Read the course online: [baloghbence.github.io/learn_spark_from_zero](https://baloghbence.github.io/learn_spark_from_zero/)**

**📝 Take a mock exam in your browser: [baloghbence.github.io/learn_spark_from_zero/mock-exam](https://baloghbence.github.io/learn_spark_from_zero/mock-exam/)**

A hands-on course that takes you from no Apache Spark knowledge to ready for the [Databricks Certified Associate Developer for Apache Spark](https://www.databricks.com/learn/certification/apache-spark-developer-associate) exam. You write and run PySpark from your own editor against Databricks serverless compute, and you test yourself with a bank of 1,000 exam-style questions.

The repository contains:

- **A course** written as Sphinx documentation with runnable Jupyter notebooks ([`docs/source`](docs/source)).
- **A question bank** of 1,000 multiple-choice questions covering every objective in the exam guide ([`fixtures/questions`](fixtures/questions)).
- **Claude Code skills** that turn the question bank into quizzes and a full-length mock exam ([`.claude/skills`](.claude/skills)).
- **A mock exam app** in React that runs a 45-question practice exam from the question bank in your browser ([`apps/mock-exam`](apps/mock-exam)).
- **A Python package** that loads and validates the question bank and creates Spark sessions for the notebooks ([`src/project`](src/project)).

> [!NOTE]
> This is an independent learning resource. It isn't affiliated with or endorsed by Databricks, and the practice questions aren't official exam items. Every claim in the course and every question links to the official documentation on [docs.databricks.com](https://docs.databricks.com) or [spark.apache.org](https://spark.apache.org/docs/latest/) so you can check it.

## Course Contents

| Chapter | What it covers |
| --- | --- |
| [0. Getting Started](docs/source/00_getting_started/index.md) | Setting up Databricks Connect, quizzing yourself and taking a mock exam with Claude Code or in the browser |
| [1. Introduction to Apache Spark](docs/source/01_introduction_to_apache_spark/index.md) | Runtime architecture, DataFrames and Spark SQL, distributed programming fundamentals, ETL with the DataFrame API |
| [2. Developing Applications with Apache Spark](docs/source/02_developing_applications_with_apache_spark/index.md) | DataFrame API basics, grouping and aggregation, joins and other relational operations, complex data types |
| [3. Stream Processing and Analysis](docs/source/03_stream_processing_and_analysis/index.md) | Structured Streaming, windowed aggregations and watermarks, real-time mode |
| [4. Monitoring and Optimizing Spark Workloads on Databricks](docs/source/04_monitoring_and_optimizing_spark_workloads_on_databricks/index.md) | Spark on Databricks, Delta Lake, performance optimization |
| [5. Exam Readiness](docs/source/05_exam_readiness/index.md) | Hands-on tasks to complete from memory before you book the exam |
| [99. Maintaining This Course](docs/source/99_maintaining_this_course/index.md) | Fact-checking the docs against official sources (for maintainers) |

The exam guide this course follows is in [`resources/`](resources/databricks-certified-associate-developer-apache-spark-exam-guide-oct-2025.pdf) (October 2025 version). Databricks asks candidates to re-check the guide shortly before their exam, so compare it with the version on the [certification page](https://www.databricks.com/learn/certification/apache-spark-developer-associate).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) to manage Python and the dependencies. The project uses Python 3.12 ([`.python-version`](.python-version)).
- The [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/install).
- A Databricks workspace with Unity Catalog and serverless compute. [Databricks Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition) is enough.
- Optional: [Claude Code](https://claude.com/claude-code) for the quizzes and the mock exam.
- Optional: [Node.js](https://nodejs.org/) 20 or later to run the mock exam app locally. The [hosted copy](https://baloghbence.github.io/learn_spark_from_zero/mock-exam/) needs nothing.

## Quick Start

1. **Clone the repository and install the dependencies.** `uv sync` creates a virtual environment with the project, Databricks Connect and the docs and test tools.

   ```shell
   git clone https://github.com/BALOGHBence/learn_spark_from_zero.git
   cd learn_spark_from_zero
   uv sync
   ```

   Don't install `pyspark` into the same environment: it conflicts with `databricks-connect` ([Install Databricks Connect for Python](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/install)).

2. **Log in to your workspace.** The CLI opens a browser and then asks for a profile name. The course notebooks use `free-edition`.

   ```shell
   databricks auth login --host <workspace-url>
   ```

3. **Check the connection.** This reads five rows from a sample table on serverless compute:

   ```shell
   uv run python -c "
   from project.utils.sparksession import get_spark_session
   spark = get_spark_session(profile='free-edition')
   spark.read.table('samples.nyctaxi.trips').show(5)
   "
   ```

4. **Start learning.** Open the notebooks under [`docs/source`](docs/source) in your editor, pick the project's `.venv` as the kernel, and begin with [Setting Up Databricks Connect](docs/source/00_getting_started/01_setting_up_databricks_connect.ipynb).

If the connection fails, see the Common Mistakes section of the setup notebook. The usual causes are a `pyspark` install next to `databricks-connect`, a profile name that `databricks auth profiles` doesn't list, or a Python version other than 3.12.

## Build the Docs

The published course at [baloghbence.github.io/learn_spark_from_zero](https://baloghbence.github.io/learn_spark_from_zero/) is rebuilt by the [`docs.yml`](.github/workflows/docs.yml) workflow on every push to `main`. To build it locally:

```shell
uv run make -C docs html
```

Open `docs/build/html/index.html` in a browser. Notebooks aren't executed during the build (`nb_execution_mode = "off"`), so the pages show the outputs saved in the notebooks and the build doesn't need a Databricks connection.

## Practice with Claude Code

Open Claude Code at the root of the repository and ask it to quiz you. The skills in [`.claude/skills`](.claude/skills) load automatically.

| Skill | Use it for | Example prompt |
| --- | --- | --- |
| `certification-quiz` | Short quizzes on one section, objective or topic while you study | `Quiz me with 10 questions on Section 5: Structured Streaming.` |
| `mock-exam` | A full 45-question practice exam across every objective, graded only after you submit all answers | `Give me a mock exam.` |
| `add-docs-content` | Adding a page or section to the course (for contributors) | `Add a page on broadcast joins.` |
| `fact-check-docs` | Checking the docs against official Databricks sources (for maintainers) | `Fact-check chapter 3.` |

Answers stay hidden until you respond. After grading you get each question's explanation and the documentation page that supports it. More example prompts are in [Quizzing Yourself with Claude Code](docs/source/00_getting_started/02_quizzing_yourself_with_claude_code.md) and [Taking a Mock Exam with Claude Code](docs/source/00_getting_started/03_taking_a_mock_exam_with_claude_code.md).

## Mock Exam App

Prefer a testing screen to a chat? [`apps/mock-exam`](apps/mock-exam) is a small React app that runs a full 45-question mock exam from the question bank in your browser. It needs no Databricks connection and no Claude Code.

**Use it online at [baloghbence.github.io/learn_spark_from_zero/mock-exam](https://baloghbence.github.io/learn_spark_from_zero/mock-exam/)**, rebuilt from the question bank on every push to `main`. To run it locally instead, you need [Node.js](https://nodejs.org/) 20 or later:

```shell
cd apps/mock-exam
npm install    # once
npm run dev
```

Open the URL it prints (usually http://localhost:5173/) and select **Start exam**. Stop the server with `Ctrl+C`.

- **Exam format:** 45 questions spread over the sections by the official section weights, with a 90-minute timer that doesn't stop you.
- **While you answer:** move freely between questions, change any answer, and mark the ones you're unsure about. **Review all** lists your marked and unanswered questions so you can go back to them.
- **After you submit:** you see your score, a breakdown by section and an explanation for every question, and nothing before that.
- **Exports:** **Copy LLM prompt** puts your wrong answers on the clipboard as a ready-to-paste tutoring prompt for an LLM. **Download wrong answers (JSON)** saves them as structured data.

The full guide is in [Taking a Mock Exam in the Browser](docs/source/00_getting_started/04_taking_a_mock_exam_in_the_browser.md).

## The Question Bank

The 1,000 questions are spread evenly over the 32 objectives of the exam guide, one YAML file per objective:

| Section | Questions |
| --- | ---: |
| 1. Apache Spark Architecture and Components | 219 |
| 2. Using Spark SQL | 125 |
| 3. Developing Apache Spark DataFrame/DataSet API Applications | 313 |
| 4. Troubleshooting and Tuning Apache Spark DataFrame API Applications | 94 |
| 5. Structured Streaming | 125 |
| 6. Using Spark Connect to deploy applications | 62 |
| 7. Using Pandas API on Spark | 62 |

Each question has four options and exactly one correct answer. Every option has a verdict (`correct`, `incorrect`, `partially_correct` or `true_but_irrelevant`) and a justification, and every question has a `source_url` on docs.databricks.com or spark.apache.org:

```yaml
- id: 1.1-001
  category: apache_spark_architecture_and_components
  objective: '1.1'
  question: |-
    Which characteristic of Spark is the main reason it can run multi-step pipelines faster than MapReduce?
  answers:
  - text: Spark can keep intermediate data in memory across operations instead of writing it to disk after each step.
    verdict: correct
    justification: MapReduce materializes intermediate results to disk between jobs; ...
  # ... three more answers
  source_url: https://spark.apache.org/docs/latest/index.html
```

The schema in [`src/project/questions/schema.py`](src/project/questions/schema.py) enforces these rules, and you can load the bank from Python:

```python
from project.questions import Category, load_questions

questions = load_questions()                                  # all 1,000
streaming = load_questions(category=Category.STRUCTURED_STREAMING)
joins = load_questions(objective="3.5")
```

## Repository Layout

```text
.
├── .claude/skills/       Claude Code skills: quizzes, mock exam, docs authoring and fact-checking
├── apps/mock-exam/       React mock exam app that runs in the browser
├── docs/source/          Course content (Markdown pages and Jupyter notebooks)
├── fixtures/questions/   Question bank, one folder per exam section
├── resources/            Exam guide and Databricks AI Prep Guide (PDF)
├── src/project/          Python package: question bank loader and schema, Spark session helper
├── tests/                pytest suite, including validation of the whole question bank
├── dab/, databricks.yml  Declarative Automation Bundle configuration
└── scratch/              Personal notebooks, ignored by Git
```

## Development

```shell
uv run pytest            # tests, including validation of every question file
uv run ruff check .      # lint
uv run mypy              # type check (strict)
```

Add questions to the YAML file of the matching objective and run `uv run pytest`. The tests fail if a question breaks the schema, uses a duplicate id, or changes the number of questions per section.

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md) first. Course content must be grounded in official sources, with a docs.databricks.com link next to each key claim. The `add-docs-content` and `fact-check-docs` skills apply those rules for you.

## License

[MIT](LICENSE)
