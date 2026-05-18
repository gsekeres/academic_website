# Qual Micro Validation

Generated from `game theory/Microeconomics_Qualifying_Exam_Answer_Key/main.tex`.

## Accepted Records

- Accepted 30 subpart-level JSONL records in `question_bank_curated/drafts/qual_micro_curated.jsonl`.
- Dates covered: May 2025 and September 2024 Retake.
- Source family: Microeconomics Qualifying Exam Answer Key.
- Every record uses `source.type="qualifying_exam"`, `source.family="Microeconomics Qualifying Exam Answer Key"`, and `source.file="game theory/Microeconomics_Qualifying_Exam_Answer_Key/main.tex"`.
- Every record includes `source.exam_date`, `source.year`, `source.original_question`, `source.part`, and top-level tags including `Q Exam`, the exam date, question number, and part label.

## Accepted Coverage

- May 2025 Question 1: parts A, B, C split into output supply and unconditional input demand, and D.
- May 2025 Question 2: parts A, B, C, and D.
- May 2025 Question 3: parts A, B1, B2, B3, and B4.
- May 2025 Question 4: parts A, B, D, E split into beliefs and mixed PBE, and F.
- September 2024 Retake Question 1: parts A, B, and C.
- September 2024 Retake Question 2: parts A and B.
- September 2024 Retake Question 3: parts A, B, C, D, and E.

## Validation Notes

- Production theory records were independently checked for binding constraints, first-order conditions, exponent algebra, cost substitution, and Hotelling's lemma sign.
- Minimal-work records were independently checked using feasible-set inclusion, a recomputed counterexample with `m(p,1)=p^2`, and standard expenditure homogeneity when utility is independent of work.
- Bertrand records were independently checked by enumerating price-order deviations, weakly undominated equilibrium logic, the no-pure-equilibrium undercutting argument, and the open-set nonattainment argument.
- Noisy-leader game records were independently checked using strict dominance, backward induction, Bayes' rule, follower indifference, leader indifference, and deviation incentives.
- Expected-utility records were independently checked from expected log utility. The fractional-investment record uses the right derivative at zero rather than relying on the source's incomplete closed-form condition.
- Auction records were independently checked under the stated two-unit payment rules.
- Consumer-theory records were independently checked for supremum formulation, compactness and Weierstrass existence, budget exhaustion, strict-quasiconcavity uniqueness, and the failure of the lattice condition for direct Milgrom-Shannon use.

## Skipped Categories

- May 2025 Question 3(c): skipped because the mixed-uniform Bertrand construction needs a careful uniform-in-price bound on `eta` beyond the source answer.
- May 2025 Question 4(c): skipped because it is primarily a diagram/modeling prompt; the payoff and signal structure needed for later parts is restated in accepted text records.
- May 2025 Question 5: skipped because the source answer explicitly states low confidence.
- September 2024 Retake Question 4: skipped because the pure Bayesian-equilibrium enumeration is lengthy and should be audited separately before conversion.
- September 2024 Retake Question 5: skipped because several answer slots are empty or only partially developed.
- July 2024 Retake and older exams: skipped in this pass after reaching a 30-record accepted batch from the most complete recent sections.

## Command Log

- Final validation command: `python3 question_bank_curated/scripts/validate_curated_bank.py --accepted-only question_bank_curated/drafts/qual_micro_curated.jsonl`
