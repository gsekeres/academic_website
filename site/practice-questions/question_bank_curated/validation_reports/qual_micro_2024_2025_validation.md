# Qual Micro 2024-2025 Draft Validation

## Result

- Draft file: `question_bank_curated/drafts/qual_micro_2024_2025.jsonl`
- Source file: `game theory/Microeconomics_Qualifying_Exam_Answer_Key/main.tex`
- Dates covered: May 2025; September 2024 (Retake)
- Accepted records: 16
- Validation status: passed

## Accepted Coverage

May 2025:

- Question 1(a): conditional input demand
- Question 1(b): cost function
- Question 1(c): unconditional input demand
- Question 1(d): Hotelling's lemma input-price derivative
- Question 2(a): minimal-work problem
- Question 2(b): price monotonicity of minimal work
- Question 2(c): non-homogeneity counterexample
- Question 2(d): utility independent of hours

September 2024 (Retake):

- Question 1(a): positive expected return is not sufficient under log utility
- Question 1(b): necessary and sufficient acceptance condition
- Question 1(c): positive fractional investment
- Question 2(a): two-unit second-highest-bid auction counterexample
- Question 2(b): two-unit third-price auction truthfulness
- Question 3(a): consumer problem with possible nonattainment
- Question 3(b): existence under strictly positive prices
- Question 3(c): binding budget constraint

## Skipped Items

- May 2025 Question 3: skipped in this pass because the Bertrand problem has many nested subparts and would be better converted as a separate focused batch.
- May 2025 Question 4: skipped in this pass because the noisy-leader setup includes an extensive-form/game-tree drawing subpart; later subparts depend on that information structure.
- May 2025 Question 5: skipped because the source answer explicitly reports low confidence and uncertainty.
- September 2024 (Retake) Question 3(d)-(e): skipped to keep this batch within the requested target size after accepting the smaller self-contained consumer-choice subparts.
- September 2024 (Retake) Question 4: skipped because the Bayesian game equilibrium enumeration is lengthy and bundled across subparts in the source solution.
- September 2024 (Retake) Question 5: skipped because the source material is image-heavy and partly incomplete, including an omitted/commented solution.

## Validation Command

```bash
python3 question_bank_curated/scripts/validate_curated_bank.py --accepted-only question_bank_curated/drafts/qual_micro_2024_2025.jsonl
```

Output:

```text
validated 16 records
```

## Notes

- Each accepted record has `source.type="qualifying_exam"`, `source.family="Microeconomics Qualifying Exam Answer Key"`, `source.file="game theory/Microeconomics_Qualifying_Exam_Answer_Key/main.tex"`, `source.locator`, `source.exam_date`, `source.year`, `source.original_question`, and `source.part`.
- Shared assumptions were moved into `preliminaries`.
- Solutions were rewritten as validated standalone arguments rather than copied answer fragments.
- All accepted records use LaTeX delimiters and avoid raw HTML.
