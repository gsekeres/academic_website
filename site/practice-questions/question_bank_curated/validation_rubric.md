# Validation Rubric

Use this rubric before accepting a question.

## Standalone Statement

- All objects are defined before use.
- All assumptions are explicit.
- The question does not require reading earlier textbook pages.
- Any theorem used in the solution is named and stated in the preliminaries or solution.
- Math notation uses HTML-displayable LaTeX delimiters: `\\(...\\)` inline and `\\[...\\]` for display equations.
- The text avoids raw HTML and avoids ambiguous OCR artifacts.

## Mathematical Correctness

- The solution proves every requested claim.
- Boundary cases are handled.
- First-order conditions are justified by the right regularity and constraint qualification assumptions.
- Equilibrium claims check every player's deviation incentives.
- Counterexamples satisfy the hypotheses and violate the claimed conclusion.

## Pedagogical Value

- The question has a clear learning objective.
- Variants differ for a reason: parameter change, assumption change, proof method, counterexample, application, or interpretation.
- The difficulty label is plausible for a PhD micro/math/game theory qualifier-prep audience.

## Source and Attribution

- Local textbook sources are used first when available.
- External sources such as MIT OpenCourseWare may be used when they fill a coverage gap.
- Source references are anchors for topic lineage, not copied prompts.

## Acceptance Decision

Set `validation.status` to:

- `accepted`: ready for final bank;
- `revise`: promising but needs rewrite;
- `rejected`: not suitable for curated bank.
