# Qual Micro 2014-2019 Draft Validation

Draft file: `question_bank_curated/drafts/qual_micro_2014_2019.jsonl`

Source: `game theory/Microeconomics_Qualifying_Exam_Answer_Key/main.tex`

## Result

- Accepted records: 18
- Validation status: passed
- Validation command: `python3 question_bank_curated/scripts/validate_curated_bank.py --accepted-only question_bank_curated/drafts/qual_micro_2014_2019.jsonl`
- Validator output: `validated 18 records`

## Accepted Coverage

- July 2019 (Retake): Question 4, Parts A-C
- July 2018 (Retake): Question 1, Parts A-C; Question 2, Parts A, B, C1, C2
- June 2018: Question 3, Parts A, B, E
- July 2017 (Retake): Question 1, Parts A-C
- June 2017: Question 1, Parts A, B1

Each accepted record was split at the subpart level, restates the needed setup, uses `source.type="qualifying_exam"`, `source.family="Microeconomics Qualifying Exam Answer Key"`, `source.file="game theory/Microeconomics_Qualifying_Exam_Answer_Key/main.tex"`, and includes `source.locator`, `source.exam_date`, `source.year`, `source.original_question`, and `source.part`.

## Skipped Categories

- Empty placeholders in the source, including blank question items.
- Figure-heavy records requiring inaccessible or nonportable game-tree diagrams.
- Source subparts with missing, placeholder, or partial answer-key solutions.
- Records whose source solution contained unresolved notes or claims that could not be accepted without a larger rewrite.
- Longer multi-part equilibrium questions not selected because the target was 10-24 smaller self-contained records.

## Validation Notes

The accepted records were independently checked for mathematical correctness, standalone notation, complete solutions, LaTeX delimiter usage, and absence of raw HTML. Records were marked `validation.status="accepted"` only after the independent solution check.
