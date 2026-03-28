from __future__ import annotations

from pathlib import Path

from lakehouse.io.workbook import load_workbook_rows, resolve_input_path
from lakehouse.io.writers import write_csv, write_jsonl
from lakehouse.layout import DatasetLayout
from lakehouse.transforms.moltbook import aggregate_gold, build_summary, normalize_silver


def extract_moltbook_sample(project_root: Path, xlsx_path: Path, dataset_name: str = "moltbook") -> dict[str, object]:
    input_path = resolve_input_path(project_root, xlsx_path)
    layout = DatasetLayout.for_dataset(project_root / "lakehouse", dataset_name)
    layout.ensure()

    headers, rows = load_workbook_rows(input_path)

    silver_rows = normalize_silver(rows)
    gold_rows = aggregate_gold(silver_rows)

    bronze_path = layout.bronze_dir / "posts_top1000.jsonl"
    silver_path = layout.silver_dir / "posts_top1000.csv"
    gold_path = layout.gold_dir / "authors_summary.csv"

    write_jsonl(bronze_path, rows)
    write_csv(silver_path, silver_rows)
    write_csv(gold_path, gold_rows)

    summary = build_summary(
        bronze_rows=rows,
        headers=headers,
        silver_rows=silver_rows,
        gold_rows=gold_rows,
        bronze_jsonl=str(bronze_path),
        silver_csv=str(silver_path),
        gold_csv=str(gold_path),
    )
    return summary.to_dict()
