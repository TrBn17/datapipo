from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatasetLayout:
    bronze_dir: Path
    silver_dir: Path
    gold_dir: Path

    @classmethod
    def for_dataset(cls, lakehouse_root: Path, dataset_name: str) -> "DatasetLayout":
        return cls(
            bronze_dir=lakehouse_root / "bronze" / dataset_name,
            silver_dir=lakehouse_root / "silver" / dataset_name,
            gold_dir=lakehouse_root / "gold" / dataset_name,
        )

    def ensure(self) -> None:
        for directory in (self.bronze_dir, self.silver_dir, self.gold_dir):
            directory.mkdir(parents=True, exist_ok=True)
