# Qualifying Exam Import Audit

Source folder:

`game theory/Microeconomics_Qualifying_Exam_Answer_Key/`

Primary source:

`game theory/Microeconomics_Qualifying_Exam_Answer_Key/main.tex`

## Final Integrated Draft

The final qualifying-exam import used by the canonical bank is:

`question_bank_curated/drafts/qual_micro_integrated.jsonl`

It contains 74 accepted subpart-level records. Larger exam questions were split into smaller self-contained records, usually one record per part or subpart. Each record includes:

- `source.type: "qualifying_exam"`;
- `source.family: "Microeconomics Qualifying Exam Answer Key"`;
- `source.exam_date`;
- `source.year`;
- original question and part metadata where available;
- tags including `Q Exam`, exam date, question number, part, and year.

## Included Dates

- May 2025
- September 2024 (Retake)
- July 2024 (Retake)
- June 2024
- June 2023
- July 2022 (Retake)
- May 2022
- June 2021
- July 2019 (Retake)
- July 2018 (Retake)
- June 2018
- July 2017 (Retake)
- June 2017

## Exclusions

Records were skipped when the source answer was empty, partial, explicitly uncertain, figure-heavy, table-dependent, or required a long equilibrium reconstruction that was not independently validated in this pass.

The narrower file `qual_micro_2024_2025.jsonl` is kept as an audit draft but is not part of the final build because its high-quality records overlap with the broader recent-exam import in `qual_micro_curated.jsonl`.
