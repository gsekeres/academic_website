#!/usr/bin/env python3
"""Validate curated question JSON or JSONL files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_TOP = {
    "id",
    "cluster_id",
    "variant_type",
    "title",
    "main_domain",
    "subdomain",
    "difficulty",
    "prerequisites",
    "learning_objective",
    "preliminaries",
    "question",
    "solution",
    "source",
    "validation",
}

DOMAINS = {"math", "micro", "game_theory"}
DIFFICULTIES = {"warmup", "medium", "advanced", "exam"}
VARIANT_TYPES = {
    "canonical",
    "numeric_parameters",
    "assumption_change",
    "proof_variant",
    "counterexample_variant",
    "application_variant",
    "comparative_statics_variant",
    "interpretation_variant",
}

MATHY = re.compile(
    r"(\\\(|\\\[|[A-Za-z]_[A-Za-z0-9{]|\\max|\\min|\\sum|\\int|\\frac|\\alpha|\\beta|\\lambda|\\forall|\\exists)"
)
RAW_HTML = re.compile(
    r"</?(?:p|div|span|script|style|br|ul|ol|li|strong|em|a|h[1-6])(?:\s|>|/)",
    re.IGNORECASE,
)
BAD_UNICODE = re.compile(r"[∀∃≤≥≠→⇒⇔∈∉⊂⊆⊇∪∩×·αβγδλμπσ∞]")


def load_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text()
    if path.suffix == ".jsonl":
        records = []
        for i, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{i}: invalid JSONL: {exc}") from exc
            records.append(record)
        return records
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected top-level JSON array")
    return data


def validate_record(record: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    label = record.get("id") or f"record[{index}]"

    missing = sorted(k for k in REQUIRED_TOP if k not in record)
    if missing:
        errors.append(f"{label}: missing required fields {missing}")

    if record.get("main_domain") not in DOMAINS:
        errors.append(f"{label}: bad main_domain {record.get('main_domain')!r}")
    if record.get("difficulty") not in DIFFICULTIES:
        errors.append(f"{label}: bad difficulty {record.get('difficulty')!r}")
    if record.get("variant_type") not in VARIANT_TYPES:
        errors.append(f"{label}: bad variant_type {record.get('variant_type')!r}")

    for key in ["id", "cluster_id"]:
        value = record.get(key, "")
        if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
            errors.append(f"{label}: {key} must be kebab-case")

    if record.get("variant_type") == "canonical" and record.get("variant_of") not in (None, ""):
        errors.append(f"{label}: canonical records should not set variant_of")
    if record.get("variant_type") != "canonical" and not record.get("variant_of"):
        errors.append(f"{label}: non-canonical records must set variant_of")

    min_lengths = {"preliminaries": 40, "question": 20, "solution": 80}
    for key in ["preliminaries", "question", "solution"]:
        value = record.get(key)
        if not isinstance(value, str) or len(value.strip()) < min_lengths[key]:
            errors.append(f"{label}: {key} is too short or non-string")
            continue
        if RAW_HTML.search(value):
            errors.append(f"{label}: {key} contains raw HTML")
        if BAD_UNICODE.search(value):
            errors.append(f"{label}: {key} contains raw mathematical Unicode; use LaTeX")
        if MATHY.search(value) and ("\\(" not in value and "\\[" not in value):
            errors.append(f"{label}: {key} appears math-heavy but lacks LaTeX delimiters")

    prerequisites = record.get("prerequisites")
    if not isinstance(prerequisites, list) or not prerequisites or not all(isinstance(x, str) for x in prerequisites):
        errors.append(f"{label}: prerequisites must be a nonempty string list")

    source = record.get("source")
    if not isinstance(source, dict):
        errors.append(f"{label}: source must be an object")
    else:
        for key in ["type", "family", "locator", "notes"]:
            if not source.get(key):
                errors.append(f"{label}: source.{key} is required")

    validation = record.get("validation")
    if not isinstance(validation, dict):
        errors.append(f"{label}: validation must be an object")
    else:
        if validation.get("status") not in {"draft_written", "accepted", "revise", "rejected"}:
            errors.append(f"{label}: validation.status is invalid")
        if not validation.get("notes"):
            errors.append(f"{label}: validation.notes is required")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--accepted-only", action="store_true")
    args = parser.parse_args()

    all_records: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in args.paths:
        try:
            records = load_records(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            continue
        for i, record in enumerate(records, start=1):
            errors.extend(validate_record(record, i))
            if args.accepted_only and record.get("validation", {}).get("status") != "accepted":
                errors.append(f"{record.get('id', f'record[{i}]')}: record is not accepted")
        all_records.extend(records)

    ids = [r.get("id") for r in all_records]
    duplicates = sorted({x for x in ids if ids.count(x) > 1})
    if duplicates:
        errors.append(f"duplicate ids: {duplicates}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"validated {len(all_records)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
