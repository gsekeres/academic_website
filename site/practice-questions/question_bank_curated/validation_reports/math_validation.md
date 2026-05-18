# Math Curated Draft Validation

Validator: GPT-5 Codex

Validated file: `question_bank_curated/drafts/math_curated.jsonl`

## Counts

- accepted: 38
- revise: 0
- rejected: 0

## Important Fixes

- Repaired `math-convex-closed-hull-counterexample-001`: the original hyperbola-only claim that `\((0,1)\)` lies in the convex-hull closure was false. Replaced it with the closed set `\(\{(0,0)\}\cup\{(x,y):x>0,\ xy=1\}\)` and a correct proof that `\((1,0)\)` is in the closure but not in the convex hull.
- Tightened `math-correspondence-budget-continuity-001` by making the eventual boundedness argument explicit and giving a concrete lower-hemicontinuity construction on the budget boundary.
- Clarified the direct sup-norm proof in `math-fixed-blackwell-bellman-001` so the lower and upper inequalities both follow from monotonicity plus nonnegative discounting.
- Normalized malformed literal newline escapes around display equations and restored affected LaTeX commands such as `\(\ne\)`, `\(\notin\)`, and `\(\nabla\)`.

## Decision Notes

All accepted records were independently checked for standalone assumptions, HTML-displayable LaTeX formatting, and substantive correctness of the full solution. Validation metadata was updated with `independent_solver` and `validated_by` set to `GPT-5 Codex`.
