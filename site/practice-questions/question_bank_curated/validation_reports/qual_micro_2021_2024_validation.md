# Qual Micro 2021-2024 Draft Validation

Source file: `game theory/Microeconomics_Qualifying_Exam_Answer_Key/main.tex`

Draft file: `question_bank_curated/drafts/qual_micro_2021_2024.jsonl`

## Result

- Accepted records: 26
- Validation status: passed
- Validation command:

```bash
python3 question_bank_curated/scripts/validate_curated_bank.py --accepted-only question_bank_curated/drafts/qual_micro_2021_2024.jsonl
```

Validator output:

```text
validated 26 records
```

## Coverage

- July 2024 (Retake): Question 1 parts A-C
- June 2024: Question 1 parts A-B; Question 2 parts A-C
- June 2023: Question 1; Question 2 part A; Question 5 parts D-E
- July 2022 (Retake): Question 1 parts A-B; Question 2 parts A-C
- May 2022: Question 2 parts A-C
- June 2021: Question 1 parts A-C; Question 3 parts A-C

## Skipped Categories

- Ambiguous or disputed answer-key records, including July 2024 (Retake) Question 2 where the source notes unresolved confusion.
- Image-heavy records requiring inaccessible or non-text game-tree interpretation, including May 2022 settlement-game parts.
- Partial or incomplete records, including prompts whose answer-key solution is only a sketch, missing graph, or not enough to validate independently.
- Long multi-part equilibrium-characterization records where complete self-contained conversion would exceed a smaller subpart record or require substantial reconstruction beyond the answer key.
- Records with apparent source inconsistencies that could not be repaired with high confidence from the text alone.

## Validation Notes

Each accepted record was rewritten as a standalone subpart-level prompt with the shared setup restated. Solutions were independently checked for algebra, boundary cases, and theorem use before setting `validation.status` to `accepted`. Source metadata includes `source.type`, `source.family`, `source.file`, `source.locator`, `source.exam_date`, `source.year`, `source.original_question`, and `source.part`.
