#!/usr/bin/env python3
"""Build canonical curated JSON and frontend-compatible JSON from JSONL drafts."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: {exc}") from exc
    return records


def frontend_record(record: dict[str, Any]) -> dict[str, Any]:
    source = record.get("source", {})
    return {
        "id": record["id"],
        "cluster_id": record["cluster_id"],
        "variant_of": record.get("variant_of"),
        "variant_type": record["variant_type"],
        "title": record["title"],
        "main_domain": record["main_domain"],
        "subdomain": record["subdomain"],
        "source_family": source.get("family"),
        "difficulty": record["difficulty"],
        "topics": [record["main_domain"], record["subdomain"], record["variant_type"]],
        "prerequisites": record["prerequisites"],
        "learning_objective": record["learning_objective"],
        "preliminaries": record["preliminaries"],
        "question": record["question"],
        "solution": record["solution"],
    }


def build_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_domain = Counter(r["main_domain"] for r in records)
    by_subdomain = Counter(f"{r['main_domain']}/{r['subdomain']}" for r in records)
    by_source = Counter(r.get("source", {}).get("family", "unknown") for r in records)
    clusters: dict[str, list[str]] = defaultdict(list)
    for record in records:
        clusters[record["cluster_id"]].append(record["id"])
    return {
        "total_questions": len(records),
        "total_families": len(clusters),
        "by_domain": dict(sorted(by_domain.items())),
        "by_subdomain": dict(sorted(by_subdomain.items())),
        "by_source": dict(sorted(by_source.items())),
        "family_sizes": dict(sorted((k, len(v)) for k, v in clusters.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("drafts", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, default=Path("question_bank_curated/curated_questions.json"))
    parser.add_argument(
        "--frontend-out",
        type=Path,
        default=Path("question_bank_curated/practice-questions.curated.json"),
    )
    parser.add_argument("--summary-out", type=Path, default=Path("question_bank_curated/summary.json"))
    parser.add_argument("--accepted-only", action="store_true")
    args = parser.parse_args()

    records: list[dict[str, Any]] = []
    for draft in args.drafts:
        records.extend(load_jsonl(draft))
    if args.accepted_only:
        records = [r for r in records if r.get("validation", {}).get("status") == "accepted"]
    records.sort(key=lambda r: (r["main_domain"], r["subdomain"], r["cluster_id"], r["id"]))

    args.out.write_text(json.dumps(records, indent=2) + "\n")
    args.frontend_out.write_text(json.dumps([frontend_record(r) for r in records], indent=2) + "\n")
    args.summary_out.write_text(json.dumps(build_summary(records), indent=2) + "\n")
    print(f"built {len(records)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
