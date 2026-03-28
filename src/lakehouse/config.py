from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LocalPaths:
    project_root: Path
    lakehouse_root: Path
    sample_root: Path

    @classmethod
    def from_project_root(cls, project_root: Path) -> "LocalPaths":
        return cls(
            project_root=project_root,
            lakehouse_root=project_root / "lakehouse",
            sample_root=project_root / "sample",
        )


@dataclass(frozen=True)
class RuntimeConfig:
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    s3_endpoint: str
    s3_warehouse_bucket: str
    iceberg_catalog_uri: str
    trino_host: str
    trino_port: int
    duckdb_path: str

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        return cls(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin"),
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            s3_endpoint=os.getenv("S3_ENDPOINT", "http://localhost:9000"),
            s3_warehouse_bucket=os.getenv("S3_WAREHOUSE_BUCKET", "warehouse"),
            iceberg_catalog_uri=os.getenv("ICEBERG_CATALOG_URI", "http://localhost:8181"),
            trino_host=os.getenv("TRINO_HOST", "localhost"),
            trino_port=int(os.getenv("TRINO_PORT", "8080")),
            duckdb_path=os.getenv("DUCKDB_PATH", "var/duckdb/dev.duckdb"),
        )
