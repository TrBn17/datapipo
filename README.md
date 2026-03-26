# Local Lakehouse

Minimal local lakehouse baseline built around Iceberg.

## Purpose

This repository exists to provide a clean starting point for ETL and lakehouse work on a local machine.

It keeps only the core pieces that are useful from the beginning:
- local object storage
- Iceberg catalog
- query and processing engines
- a simple `bronze / silver / gold` data layout
- one small script for validating the flow on sample data

## Why This Repository Exists

Most early data repos become noisy too quickly: placeholder code, half-used frameworks, and sample modules that do not survive the first real pipeline.

This repository takes the opposite approach:
- keep the infrastructure explicit
- keep the data layout stable
- add pipeline code only when there is a real source and a real transformation to support

## Stack

- MinIO for S3-compatible local storage
- Iceberg REST catalog for table metadata
- Spark for ETL and table operations
- Trino for SQL access and ad hoc querying

## Repository Structure

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

## Data Layout

- `lakehouse/bronze/`: raw or near-raw input
- `lakehouse/silver/`: cleaned and standardized data
- `lakehouse/gold/`: analysis-ready or business-facing outputs

This layout is the main contract of the repository. Implementation details can change later, but this flow should remain stable.

## Usage

### 1. Configure environment

Copy `.env.example` to `.env`.

### 2. Start local services

```powershell
docker compose up -d
```

Or:

```powershell
make up
```

### 3. Verify services

- MinIO Console: `http://localhost:9001`
- Trino: `http://localhost:8080`
- Iceberg REST catalog: `http://localhost:8181`

### 4. Run the sample extraction

The sample workbook at [sample/moltbook_top1000_posts.xlsx](C:\Users\Admin\spark\sample\moltbook_top1000_posts.xlsx) can be processed with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/extract_moltbook_sample.ps1
```

Or:

```powershell
make extract
```

The script writes outputs into:
- `lakehouse/bronze/`
- `lakehouse/silver/`
- `lakehouse/gold/`

## Notes

- `infra/` stores engine configuration and should remain version-controlled.
- `scripts/` is for small operational scripts, not framework scaffolding.
- Add application code only when the actual ETL workflow is clear.
