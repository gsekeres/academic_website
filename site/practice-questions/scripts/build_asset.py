#!/usr/bin/env python3
"""Build the frontend-compatible practice question asset."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "question_bank" / "questions.json"
ASSET = ROOT.parent / "assets" / "practice-questions.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(CANONICAL))
    parser.add_argument("--output", default=str(ASSET))
    parser.add_argument("--include-drafts", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    validation = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_questions.py"), str(input_path)],
        check=False,
        text=True,
        capture_output=True,
    )
    if validation.returncode != 0:
        sys.stderr.write(validation.stderr)
        sys.stderr.write(validation.stdout)
        return validation.returncode

    with input_path.open() as fh:
        questions = json.load(fh)

    if not args.include_drafts:
        questions = [q for q in questions if q.get("status") != "flag_review"]

    asset_questions = []
    for q in questions:
        source = q.get("source", {})
        asset_questions.append(
            {
                "id": q["id"],
                "title": q["title"],
                "source_family": q.get("source_family") or source.get("family"),
                "main_domain": q["main_domain"],
                "sub_domain": q["sub_domain"],
                "difficulty": q["difficulty"],
                "topics": q.get("topics", []),
                "task_type": q.get("task_type"),
                "context_quality": q.get("context_quality"),
                "solution_policy": q.get("solution_policy"),
                "quality_flags": q.get("quality_flags", []),
                "status": q.get("status"),
                "source": source,
                "prompt": q["prompt"],
                "hint": q["hint"],
                "solution": q["solution"],
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(asset_questions, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {len(asset_questions)} questions to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
