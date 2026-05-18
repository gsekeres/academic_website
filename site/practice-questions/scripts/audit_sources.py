#!/usr/bin/env python3
"""Audit source extraction coverage and generated question counts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_DIRS = [ROOT / "extracted_text", ROOT / "extracted_text_ocr"]
QUESTIONS = ROOT / "question_bank" / "questions.json"


PATTERNS = {
    "econ_exercise": re.compile(r"(?m)^Exercise\s+\d+"),
    "osborne_exercise": re.compile(r"(?m)^\?\s*Exercise\s+\d+\.\d+"),
    "varian_item": re.compile(r"(?m)^\s*\d{1,2}\.\d{1,2}\.\s+"),
    "kreps_problem": re.compile(r"(?m)^■\s*\*?\d{1,2}\.\d{1,2}\.\s+"),
}


def count_markers(text: str) -> dict[str, int]:
    return {name: len(pattern.findall(text)) for name, pattern in PATTERNS.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", default=str(QUESTIONS))
    args = parser.parse_args()

    generated_by_text: dict[str, int] = {}
    qpath = Path(args.questions)
    if qpath.exists():
        with qpath.open() as fh:
            for item in json.load(fh):
                text_file = item.get("source", {}).get("text_file")
                if text_file:
                    generated_by_text[text_file] = generated_by_text.get(text_file, 0) + 1

    rows = []
    text_paths = []
    for directory in TEXT_DIRS:
        if directory.exists():
            text_paths.extend(sorted(directory.glob("*.txt")))

    for path in text_paths:
        text = path.read_text(errors="replace")
        rel = str(path.relative_to(ROOT))
        markers = count_markers(text)
        rows.append(
            {
                "text_file": rel,
                "bytes": path.stat().st_size,
                "generated": generated_by_text.get(rel, 0),
                **markers,
            }
        )

    print(json.dumps(rows, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
