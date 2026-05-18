#!/usr/bin/env python3
"""Apply mechanical normalization to curated JSONL drafts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def normalize(record: dict) -> dict:
    if record.get("difficulty") == "hard":
        record["difficulty"] = "advanced"

    if record.get("variant_type") != "canonical" and not record.get("variant_of"):
        record["variant_type"] = "canonical"
        record["variant_of"] = None

    validation = record.setdefault("validation", {})
    validation.setdefault("writer", "unknown")
    validation.setdefault("independent_solver", "pending")
    validation.setdefault("validated_by", "pending")
    validation.setdefault("status", "draft_written")
    validation.setdefault("notes", "Draft normalized mechanically; awaiting independent validation.")
    if validation.get("independent_solver") == "":
        validation["independent_solver"] = "pending"
    if validation.get("validated_by") == "":
        validation["validated_by"] = "pending"

    return record


def normalize_file(path: Path) -> int:
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    records = [normalize(record) for record in records]
    path.write_text("\n".join(json.dumps(record, ensure_ascii=True) for record in records) + "\n")
    return len(records)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    total = 0
    for path in args.paths:
        count = normalize_file(path)
        total += count
        print(f"normalized {count} records in {path}")
    print(f"normalized {total} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
