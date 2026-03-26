# Local Lakehouse

This repository is a minimal baseline for building and operating a local lakehouse.

The goal is to keep only the parts that are broadly useful across projects:
- local infrastructure for object storage and query engines
- engine configuration checked into source control
- a stable data layout for `bronze`, `silver`, and `gold`
- a small operational script for validating the end-to-end flow on sample data

This repository does not include framework scaffolding, sample application code, or placeholder ETL modules.

## Architecture

The local stack is composed of:
- `MinIO` as S3-compatible object storage
- `Iceberg REST catalog` as the table metadata service
- `Spark` for ETL, table creation, and maintenance jobs
- `Trino` for interactive SQL and analytics

The intended data lifecycle is:
1. raw input lands in `bronze`
2. cleaned and standardized data moves to `silver`
3. business-ready outputs are published to `gold`

That flow should remain stable even if the implementation changes later.

## Repository Layout

```text
.
|- .env.example
|- docker-compose.yml
|- Makefile
|- README.md
|- infra/
|  |- spark/
|  |  `- conf/
|  |     `- spark-defaults.conf
|  `- trino/
|     `- catalog/
|        `- iceberg.properties
|- lakehouse/
|  |- bronze/
|  |- silver/
|  `- gold/
|- sample/
|  `- moltbook_top1000_posts.xlsx
`- scripts/
   `- extract_moltbook_sample.ps1
```

## Directory Responsibilities

`infra/`
Stores engine configuration that should be versioned and reviewed like code.

`lakehouse/bronze/`
Raw or near-raw data. Prefer append-only writes and minimal business logic here.

`lakehouse/silver/`
Cleaned, typed, standardized data. Null handling, column naming, deduplication, and schema normalization belong here.

`lakehouse/gold/`
Business-facing datasets for analysis, reporting, or downstream consumption.

`sample/`
Small input data used to validate the repository setup and operating flow.

`scripts/`
Small operational scripts. These should stay practical and task-specific.

## Running The Stack

1. Copy `.env.example` to `.env`.
2. Start the local services:

```powershell
docker compose up -d
```

3. Verify the main endpoints:
- MinIO console: `http://localhost:9001`
- Trino: `http://localhost:8080`
- Iceberg REST catalog: `http://localhost:8181`

You can also use:

```powershell
make up
make down
```

## Sample Data Flow

The repository includes one sample workbook:
- [sample/moltbook_top1000_posts.xlsx](C:\Users\Admin\spark\sample\moltbook_top1000_posts.xlsx)

The script below reads that workbook and writes derived outputs into the local lakehouse directories:
- `lakehouse/bronze/`
- `lakehouse/silver/`
- `lakehouse/gold/`

Run it with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/extract_moltbook_sample.ps1
```

or:

```powershell
make extract
```

This script exists to validate the repository shape and the basic ETL flow. It is not meant to define the final production implementation.

## Design Principles

- Keep infrastructure explicit and checked into the repository.
- Keep data layout stable even when pipeline code changes.
- Add new modules only when there is a real operational need.
- Avoid scaffolding that is not tied to an actual source, transform, or delivery requirement.

## Suggested Next Additions

Add new top-level areas only when they become necessary:
- `src/etl/` when you have repeated ingestion or transformation logic
- `sql/` when SQL transformations need to be managed separately
- `dbt/` when dbt is a confirmed part of the operating model
- `tests/` when pipeline logic is stable enough to justify regression protection

## Intentionally Omitted

The repository intentionally does not include:
- sample Python apps
- placeholder dbt projects
- toy transformation modules
- generated runtime artifacts
- test scaffolding without real pipeline coverage

The expected outcome is simple: someone opening this repository should immediately understand where infrastructure lives, where data lands, how to run the stack, and where to extend it next.
