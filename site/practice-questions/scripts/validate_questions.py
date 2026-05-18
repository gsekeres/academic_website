#!/usr/bin/env python3
"""Validate the canonical practice question bank."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ALLOWED_DOMAINS = {"math", "micro", "game_theory"}
ALLOWED_DIFFICULTIES = {"warmup", "core", "advanced", "exam"}
ALLOWED_STATUSES = {"draft", "reviewed", "needs_source_check", "flag_review"}
ALLOWED_CONTEXT = {"full", "nearby_theorem", "prompt_only", "needs_source_check", "bad_ocr"}
ALLOWED_POLICIES = {"generated_outline", "source_solution", "full_solution", "structured_hint_only", "flag_review"}
REQUIRED_TOP = {
    "id",
    "main_domain",
    "sub_domain",
    "title",
    "difficulty",
    "source",
    "prompt",
    "hint",
    "solution",
    "status",
}
REQUIRED_SOURCE = {"family", "file", "text_file", "page", "line", "locator"}


class FragmentSafetyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script":
            self.errors.append("contains script tag")
        for name, value in attrs:
            if name.lower().startswith("on"):
                self.errors.append(f"contains event handler {name}")
            if value and re.search(r"javascript\s*:", value, flags=re.I):
                self.errors.append(f"contains javascript URL in {name}")


def load_json(path: Path) -> list[dict]:
    with path.open() as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("top-level JSON value must be an array")
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"item {i} is not an object")
    return data


def validate_fragment(value: object, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: must be a nonempty string")
        return
    parser = FragmentSafetyParser()
    try:
        parser.feed(value)
    except Exception as exc:  # HTMLParser is forgiving; this is defensive.
        errors.append(f"{label}: HTML parse failed: {exc}")
    errors.extend(f"{label}: {err}" for err in parser.errors)


def normalized_prompt(prompt_text: str, prompt_html: str) -> str:
    raw = prompt_text or re.sub(r"<[^>]+>", " ", prompt_html)
    return re.sub(r"\W+", "", raw.lower())[:500]


def validate(path: Path) -> list[str]:
    data = load_json(path)
    errors: list[str] = []
    seen_ids: set[str] = set()
    seen_prompts: dict[str, str] = {}

    for index, q in enumerate(data):
        prefix = f"item {index}"
        missing = sorted(k for k in REQUIRED_TOP if not q.get(k))
        if missing:
            errors.append(f"{prefix}: missing required fields {missing}")
            continue

        qid = q["id"]
        if not isinstance(qid, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", qid):
            errors.append(f"{prefix}: id is not kebab-case: {qid!r}")
        if qid in seen_ids:
            errors.append(f"{prefix}: duplicate id {qid}")
        seen_ids.add(qid)

        if q["main_domain"] not in ALLOWED_DOMAINS:
            errors.append(f"{qid}: invalid main_domain {q['main_domain']!r}")
        if q["difficulty"] not in ALLOWED_DIFFICULTIES:
            errors.append(f"{qid}: invalid difficulty {q['difficulty']!r}")
        if q["status"] not in ALLOWED_STATUSES:
            errors.append(f"{qid}: invalid status {q['status']!r}")
        if q.get("context_quality") and q["context_quality"] not in ALLOWED_CONTEXT:
            errors.append(f"{qid}: invalid context_quality {q['context_quality']!r}")
        if q.get("solution_policy") and q["solution_policy"] not in ALLOWED_POLICIES:
            errors.append(f"{qid}: invalid solution_policy {q['solution_policy']!r}")

        if not isinstance(q.get("sub_domain"), str) or not q["sub_domain"].strip():
            errors.append(f"{qid}: sub_domain must be nonempty")
        if not isinstance(q.get("title"), str) or len(q["title"].strip()) < 3:
            errors.append(f"{qid}: title is too short")

        source = q.get("source")
        if not isinstance(source, dict):
            errors.append(f"{qid}: source must be an object")
        else:
            missing_source = sorted(k for k in REQUIRED_SOURCE if not source.get(k))
            if missing_source:
                errors.append(f"{qid}: missing source fields {missing_source}")
            source_file = ROOT / str(source.get("file", ""))
            text_file = ROOT / str(source.get("text_file", ""))
            if not source_file.exists():
                errors.append(f"{qid}: source.file does not exist: {source_file}")
            if not text_file.exists():
                errors.append(f"{qid}: source.text_file does not exist: {text_file}")
            elif text_file.stat().st_size == 0:
                errors.append(f"{qid}: source.text_file is empty: {text_file}")
            if not isinstance(source.get("page"), int) or source.get("page", 0) <= 0:
                errors.append(f"{qid}: source.page must be a positive integer")
            if not isinstance(source.get("line"), int) or source.get("line", 0) <= 0:
                errors.append(f"{qid}: source.line must be a positive integer")

        for field in ("prompt", "hint", "solution"):
            validate_fragment(q.get(field), f"{qid}.{field}", errors)

        norm = normalized_prompt(str(q.get("prompt_text", "")), str(q.get("prompt", "")))
        if len(norm) < 20:
            errors.append(f"{qid}: normalized prompt is too short")
        elif norm in seen_prompts:
            errors.append(f"{qid}: duplicate prompt with {seen_prompts[norm]}")
        else:
            seen_prompts[norm] = qid

        if q["status"] == "reviewed" and q.get("solution_policy") not in {"source_solution", "full_solution"}:
            errors.append(f"{qid}: reviewed items must have source_solution or full_solution policy")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=str(ROOT / "question_bank" / "questions.json"))
    args = parser.parse_args()
    path = Path(args.path)
    errors = validate(path)
    if errors:
        print(f"validation failed for {path}: {len(errors)} error(s)", file=sys.stderr)
        for err in errors[:200]:
            print(f"- {err}", file=sys.stderr)
        if len(errors) > 200:
            print(f"... {len(errors) - 200} more", file=sys.stderr)
        return 1
    print(f"validated {len(load_json(path))} questions in {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
