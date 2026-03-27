from __future__ import annotations

import argparse
import json
from pathlib import Path

from lakehouse.config import LocalPaths, RuntimeConfig
from lakehouse.pipelines.moltbook import extract_moltbook_sample


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="spark-lakehouse")
    subparsers = parser.add_subparsers(dest="command", required=True)

    config_parser = subparsers.add_parser("show-config", help="Print resolved runtime config")
    config_parser.add_argument(
        "--project-root",
        default=".",
        help="Project root used to resolve local paths",
    )

    extract_parser = subparsers.add_parser(
        "extract-moltbook",
        help="Extract the sample Moltbook workbook into bronze/silver/gold outputs",
    )
    extract_parser.add_argument(
        "--project-root",
        default=".",
        help="Project root used to resolve repository-relative paths",
    )
    extract_parser.add_argument(
        "--xlsx-path",
        default="sample/moltbook_top1000_posts.xlsx",
        help="Workbook path relative to project root unless absolute",
    )
    extract_parser.add_argument(
        "--dataset-name",
        default="moltbook",
        help="Dataset folder name inside bronze/silver/gold",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "show-config":
        project_root = Path(args.project_root).resolve()
        payload = {
            "paths": LocalPaths.from_project_root(project_root).__dict__,
            "runtime": RuntimeConfig.from_env().__dict__,
        }
        print(json.dumps(payload, indent=2, default=str))
        return 0

    if args.command == "extract-moltbook":
        project_root = Path(args.project_root).resolve()
        summary = extract_moltbook_sample(
            project_root=project_root,
            xlsx_path=Path(args.xlsx_path),
            dataset_name=args.dataset_name,
        )
        print(json.dumps(summary, indent=2, default=str))
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2
