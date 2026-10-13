import yaml from "js-yaml";

export const EXAM_TITLE = "Databricks Certified Associate Developer for Apache Spark";

// From the exam guide in resources/ (Oct 2025): 45 scored questions, 90 minutes.
export const QUESTION_COUNT = 45;
export const TIME_LIMIT_MINUTES = 90;

export const LETTERS = "ABCD";

// Questions per section follow the official section weights on the certification
// page (20/20/30/10/10/5/5%) applied to 45 questions, rounded with the
// largest-remainder method; ties go to the earlier section. The mock-exam skill
// uses the same table (MOCK_BLUEPRINT in
// .claude/skills/certification-quiz/scripts/pick_questions.py).
export const SECTIONS = {
  1: {
    title: "Apache Spark Architecture and Components",
    questions: 9,
    objectives: [
      "Identify the advantages and challenges of implementing Spark.",
      "Identify the role of core components of Apache Spark™'s Architecture, including cluster, driver node, worker nodes/executors, CPU cores, and memory.",
      "Describe the architecture of Apache Spark™, including DataFrame and Dataset concepts, SparkSession lifecycle, caching, storage levels, and garbage collection.",
      "Explain the Apache Spark™ Architecture execution hierarchy.",
      "Configure Spark partitioning in distributed data processing, including shuffles and partitions",
      "Describe the execution patterns of the Apache Spark™ engine, including actions, transformations, and lazy evaluation.",
      "Identify the features of the Apache Spark Modules, including Core, Spark SQL, DataFrames, Pandas API on Spark, Structured Streaming, and MLib.",
    ],
  },
  2: {
    title: "Using Spark SQL",
    questions: 9,
    objectives: [
      "Utilize common data sources such as JDBC, files, etc., to efficiently read from and write to Spark DataFrames using Spark SQL, including overwriting and partitioning by column.",
      "Execute SQL queries directly on files, including ORC Files, JSON Files, CSV Files, Text Files, and Delta Files, and understand the different save modes for outputting data in Spark SQL.",
      "Save data to persistent tables while applying sorting and partitioning to optimize data retrieval.",
      "Register DataFrames as temporary views in Spark SQL, allowing them to be queried with SQL syntax.",
    ],
  },
  3: {
    title: "Developing Apache Spark™ DataFrame/DataSet API Applications",
    questions: 14,
    objectives: [
      "Manipulate columns, rows, and table structures by adding, dropping, splitting, renaming column names, applying filters, and exploding arrays.",
      "Perform data deduplication and validation operations on DataFrames.",
      "Perform aggregate operations on DataFrames such as count, approximate count distinct, and mean, summary.",
      "Manipulate and utilize Date data type, such as Unix epoch to date string, and extract date component.",
      "Combine DataFrames with operations such as Inner join, left join, broadcast join, multiple keys, cross join, union, and union all.",
      "Manage input and output operations by writing, overwriting, and reading DataFrames with schemas.",
      "Perform operations on DataFrames such as sorting, iterating, printing schema, and conversion between DataFrame and sequence/list formats.",
      "Create and invoke user-defined functions with or without stateful operators, including StateStores.",
      "Describe different types of variables in Spark, including broadcast variables and accumulators.",
      "Describe the purpose and implementation of broadcast joins",
    ],
  },
  4: {
    title: "Troubleshooting and Tuning Apache Spark DataFrame API Applications",
    questions: 5,
    objectives: [
      "Implement performance tuning strategies & optimize cluster utilization, including partitioning, repartitioning, coalescing, identifying data skew, and reducing shuffling",
      "Describe Adaptive Query Execution (AQE) and its benefits.",
      "Perform logging and monitoring of Spark applications - publish, customize, and analyze Driver logs and Executor logs to diagnose out-of-memory errors, cluster underutilization, etc.",
    ],
  },
  5: {
    title: "Structured Streaming",
    questions: 4,
    objectives: [
      "Explain the Structured Streaming engine in Spark, including its functions, programming model, micro-batch processing, exactly-once semantics, and fault tolerance mechanisms.",
      "Create and write Streaming DataFrames and Streaming Datasets, including the basic output modes and output sinks.",
      "Perform basic operations on Streaming DataFrames and Streaming Datasets, such as selection, projection, window and aggregation.",
      "Perform Streaming Deduplication in Structured Streaming, both with and without watermark usage.",
    ],
  },
  6: {
    title: "Using Spark Connect to deploy applications",
    questions: 2,
    objectives: [
      "Describe the features of Spark Connect.",
      "Describe the different deployment mode types (Client, Cluster, Local) in the Apache Spark™ environment.",
    ],
  },
  7: {
    title: "Using Pandas API on Spark",
    questions: 2,
    objectives: [
      "Explain the advantages of using Pandas API on Spark.",
      "Create and invoke Pandas UDF.",
    ],
  },
};

export function sectionOf(objective) {
  return Number(objective.split(".")[0]);
}

export function objectiveText(objective) {
  const [section, index] = objective.split(".").map(Number);
  return SECTIONS[section].objectives[index - 1];
}

// Every YAML file of the question bank, bundled at build time.
const files = import.meta.glob("../../../fixtures/questions/**/*.yaml", {
  query: "?raw",
  import: "default",
  eager: true,
});

export const BANK = Object.values(files).flatMap((text) => yaml.load(text));

function shuffle(items) {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

// Picks a full exam: in each section every objective gets one question, and the
// section's remaining questions are dealt one at a time to its objectives in a
// random order, so extras land on different objectives before any gets a third.
// Questions and their options are shuffled.
export function createExam() {
  const byObjective = {};
  for (const q of BANK) (byObjective[q.objective] ??= []).push(q);

  const picked = [];
  for (const [section, { questions, objectives }] of Object.entries(SECTIONS)) {
    const ids = objectives.map((_, i) => `${section}.${i + 1}`);
    const counts = Object.fromEntries(ids.map((id) => [id, 1]));
    const order = shuffle(ids);
    for (let i = 0; i < questions - ids.length; i++) counts[order[i % ids.length]]++;
    for (const id of ids) {
      picked.push(...shuffle(byObjective[id] ?? []).slice(0, counts[id]));
    }
  }

  return shuffle(picked).map((q) => ({ ...q, answers: shuffle(q.answers) }));
}

export function correctIndex(question) {
  return question.answers.findIndex((a) => a.verdict === "correct");
}
