# Practice Question Bank

Generated from the PDFs in `math/`, `micro/`, and `game theory/`.

## Files

- `questions.json`: canonical question bank with provenance, domain/sub-domain, prompt, hint, solution, status, and quality flags.
- `practice-questions.frontend.json`: frontend-compatible projection of the canonical bank.
- `summary.json`: generated coverage summary by domain, status, and source.
- `../extracted_text/` and `../extracted_text_ocr/`: searchable intermediate text extracted from the PDFs.

## Rebuild

```sh
python3 scripts/extract_questions.py
python3 scripts/validate_questions.py
python3 scripts/build_asset.py --output question_bank/practice-questions.frontend.json
python3 scripts/audit_sources.py
```

The committed OCR text slices are generated artifacts. `scripts/ocr_image.swift` is a local helper for additional macOS Vision OCR passes when `pdftotext` is empty.

## Status Values

- `reviewed`: matched to a source-provided solution or answer.
- `draft`: extracted prompt with a generated hint and solution outline.
- `needs_source_check`: extracted from OCR/noisy context, refers to nearby theorem text, or may depend on figures/tables.

## Current Coverage

The current generated bank contains 897 questions:

- `math`: 406
- `micro`: 339
- `game_theory`: 152

By solution provenance:

- `source_solution`: 211 reviewed/source-backed solutions from Varian selected answers and Osborne-Rubinstein solution-manual matches.
- `generated_outline`: 686 generated hints and solution outlines.

By status:

- `reviewed`: 211
- `draft`: 370
- `needs_source_check`: 316

The generated bank covers the clean ECON 6170 math notes, math lecture notes, Johnsonbaugh-Pfaffenberger foundations exercises through core analysis/topology chapters, Simon-Blume extractable exercises, Varian exercises, Kreps problems, targeted OCR extraction of Mas-Colell chapter 2 exercises, Osborne-Rubinstein exercises, and targeted OCR extraction of Fudenberg-Tirole chapter 1 exercises.

Skipped or deferred sources are listed in `summary.json`. The main blockers are empty `pdftotext` output for Mas-Colell and Tirole and noisy segmentation in Sydsaeter-Hammond-Seierstad-Strom.
