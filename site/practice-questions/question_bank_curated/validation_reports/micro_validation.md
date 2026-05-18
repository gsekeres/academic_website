# Micro Curated Draft Validation

Validator: Codex

Validated file: `question_bank_curated/drafts/micro_curated.jsonl`

## Summary

- Accepted: 35
- Revise: 1
- Rejected: 0

## Important Fixes

- Corrected the Robinson Crusoe equilibrium calculation in `micro-equilibrium-robinson-crusoe-001`: the wage is `\(\sqrt{3}/2\)`, labor is `\(1/3\)`, leisure is `\(2/3\)`, consumption/output is `\(1/\sqrt{3}\)`, and profit is `\(1/(2\sqrt{3})\)`.
- Clarified the competitive zero-profit convention in `micro-information-lemons-market-002`; the `\(k=3\)` case has full trade at price `\(3/2\)`.
- Removed inconsistent "strict" WARP wording and retitled `micro-revealed-preference-warp-003` to avoid claiming strict affordability where the example uses equal budgets.
- Tightened the quasilinear boundary-case explanation in `micro-consumer-quasilinear-demand-001`.

## Revise

- `micro-equilibrium-second-welfare-counterexample-001`: the finite example proves that no single price/wealth pair makes both nonzero bundles uniquely optimal at the same wealth, but each efficient bundle can be supported separately. It therefore does not establish the stated convexity/supporting-prices learning objective.

## Validation Notes

All accepted records were independently solved for self-containedness, HTML-displayable LaTeX formatting, and substantive correctness of the full solution. Validation metadata was updated with `independent_solver` and `validated_by` set to `Codex`.
