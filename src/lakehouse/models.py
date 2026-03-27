from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ExtractionSummary:
    rows: int
    columns: int
    distinct_authors: int
    distinct_submolts: int
    top_author: str
    top_author_sum_interactions: int
    bronze_jsonl: str
    silver_csv: str
    gold_csv: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
