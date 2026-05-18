#!/usr/bin/env python3
"""Apply mechanical normalization to curated JSONL drafts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

TEXT_FIELDS = ["preliminaries", "question", "solution"]

UNICODE_REPLACEMENTS = {
    "∀": r"\forall",
    "∃": r"\exists",
    "≤": r"\le",
    "≥": r"\ge",
    "≠": r"\ne",
    "→": r"\to",
    "⇒": r"\Rightarrow",
    "⇔": r"\Leftrightarrow",
    "∈": r"\in",
    "∉": r"\notin",
    "⊂": r"\subset",
    "⊆": r"\subseteq",
    "⊇": r"\supseteq",
    "∪": r"\cup",
    "∩": r"\cap",
    "×": r"\times",
    "·": r"\cdot",
    "α": r"\alpha",
    "β": r"\beta",
    "γ": r"\gamma",
    "δ": r"\delta",
    "λ": r"\lambda",
    "μ": r"\mu",
    "π": r"\pi",
    "σ": r"\sigma",
    "∞": r"\infty",
}


def normalize_text(value: str) -> str:
    for old, new in UNICODE_REPLACEMENTS.items():
        value = value.replace(old, new)
    return value


def normalize(record: dict) -> dict:
    if record.get("main_domain") == "game":
        record["main_domain"] = "game_theory"
    if record.get("main_domain") == "math_for_economics":
        record["main_domain"] = "math"

    if record.get("difficulty") == "hard":
        record["difficulty"] = "advanced"
    if record.get("difficulty") == "easy":
        record["difficulty"] = "warmup"

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

    for field in TEXT_FIELDS:
        if isinstance(record.get(field), str):
            record[field] = normalize_text(record[field])

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
