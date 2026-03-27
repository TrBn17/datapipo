from __future__ import annotations

from collections import defaultdict
from typing import Any

from lakehouse.models import ExtractionSummary


def normalize_silver(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    silver_rows: list[dict[str, Any]] = []
    for row in rows:
        silver_rows.append(
            {
                "rank_upvotes": _to_int(row.get("rank_upvotes")),
                "upvotes": _to_int(row.get("upvotes")),
                "downvotes": _to_int(row.get("downvotes")),
                "score": _to_int(row.get("score")),
                "comment_count": _to_int(row.get("comment_count")),
                "total_interactions": _to_int(row.get("total_interactions")),
                "comment_upvote_ratio": _to_float(row.get("comment_upvote_ratio")),
                "id": row.get("id") or "",
                "post_url": row.get("post_url") or "",
                "author": row.get("author") or "",
                "submolt": row.get("submolt") or "",
                "created_at": row.get("created_at") or "",
                "title": row.get("title") or "",
                "content": row.get("content") or "",
                "title_len": _to_int(row.get("title_len")),
                "content_len": _to_int(row.get("content_len")),
                "first_link_url": row.get("first_link_url") or "",
                "link_domain": row.get("link_domain") or "",
                "extracted_at_utc": row.get("extracted_at_utc") or "",
                "rank_score": _to_int(row.get("rank_score")),
                "rank_comments": _to_int(row.get("rank_comments")),
                "rank_total_interactions": _to_int(row.get("rank_total_interactions")),
                "net_votes": _to_int(row.get("upvotes")) - _to_int(row.get("downvotes")),
                "engagement_count": _to_int(row.get("score")) + _to_int(row.get("comment_count")),
                "title_chars": len(row.get("title") or ""),
                "content_chars": len(row.get("content") or ""),
            }
        )
    return silver_rows


def aggregate_gold(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "author": "",
            "post_count": 0,
            "sum_upvotes": 0,
            "sum_comments": 0,
            "sum_interactions": 0,
            "best_score": 0,
        }
    )

    for row in rows:
        author = row["author"]
        bucket = grouped[author]
        bucket["author"] = author
        bucket["post_count"] += 1
        bucket["sum_upvotes"] += row["upvotes"]
        bucket["sum_comments"] += row["comment_count"]
        bucket["sum_interactions"] += row["total_interactions"]
        bucket["best_score"] = max(bucket["best_score"], row["score"])

    return sorted(grouped.values(), key=lambda item: item["sum_interactions"], reverse=True)


def build_summary(
    bronze_rows: list[dict[str, Any]],
    headers: list[str],
    silver_rows: list[dict[str, Any]],
    gold_rows: list[dict[str, Any]],
    bronze_jsonl: str,
    silver_csv: str,
    gold_csv: str,
) -> ExtractionSummary:
    top_author = gold_rows[0]["author"] if gold_rows else ""
    top_author_sum_interactions = gold_rows[0]["sum_interactions"] if gold_rows else 0

    return ExtractionSummary(
        rows=len(bronze_rows),
        columns=len(headers),
        distinct_authors=len({row["author"] for row in silver_rows}),
        distinct_submolts=len({row["submolt"] for row in silver_rows}),
        top_author=top_author,
        top_author_sum_interactions=top_author_sum_interactions,
        bronze_jsonl=bronze_jsonl,
        silver_csv=silver_csv,
        gold_csv=gold_csv,
    )


def _to_int(value: Any) -> int:
    if value in (None, ""):
        return 0
    return int(value)


def _to_float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)
