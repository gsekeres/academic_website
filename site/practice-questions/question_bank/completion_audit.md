# Completion Audit

## Objective Restatement

Create a text-searchable practice-question bank from PDFs in `math/`, `micro/`, and `game theory/`, with JSON records classified by main domain and sub-domain, and with a hint and solution field for each generated question. Use multiple agent/checking passes and prioritize producing as many usable outputs as possible.

## Checklist

- Convert PDFs/text into searchable intermediates: satisfied by `extracted_text/` for all PDFs with `pdftotext`, plus targeted OCR slices in `extracted_text_ocr/`.
- Generate JSON question bank: satisfied by `question_bank/questions.json`.
- Include three domains: satisfied; `math`, `micro`, and `game_theory` are all present.
- Include main domain and sub-domain per question: validated for all 897 questions.
- Include hint and solution per question: validated nonempty for all 897 questions.
- Preserve source provenance: validated for all 897 questions with source PDF, text file, page, line, and locator.
- Provide frontend-compatible export: satisfied by `question_bank/practice-questions.frontend.json`.
- Provide rebuild/audit scripts: satisfied by `scripts/extract_questions.py`, `scripts/validate_questions.py`, `scripts/build_asset.py`, `scripts/audit_sources.py`, and `scripts/ocr_image.swift`.
- Run validation: `python3 scripts/validate_questions.py question_bank/questions.json` passes.

## Current Counts

- Total questions: 897
- Math: 406
- Micro: 339
- Game theory: 152

By status:

- Reviewed/source-backed: 211
- Draft: 370
- Needs source check: 316

By solution policy:

- Source solution: 211
- Generated outline: 686

## Limitations

- `generated_outline` records have generated solution outlines, not source-verified worked solutions.
- `needs_source_check` records came from OCR/noisy extraction, theorem-dependent prompts, or possible figure/table context.
- Mas-Colell and Tirole have only targeted OCR slices included because direct `pdftotext` output is effectively empty.
- Sydsaeter-Hammond-Seierstad-Strom was deferred because OCR text was readable but problem segmentation was too noisy for reliable automated import.
