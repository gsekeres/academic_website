# Curated Practice Question Bank

This directory is intentionally separate from `question_bank/`. The original bank is a raw source index; this bank is an editorially curated set of self-contained PhD-level practice questions.

## Quality Bar

Every accepted question must be answerable by a student who has not been reading the source textbook. A valid record needs:

- a standalone question statement;
- explicit preliminaries, definitions, notation, and assumptions;
- a complete worked solution;
- clear prerequisites and learning objective;
- a source anchor or external inspiration note;
- independent validation notes.
- HTML-displayable text with LaTeX math delimiters.

Reject questions that depend on missing surrounding text, undefined symbols, inaccessible diagrams, OCR fragments, or solution sketches that do not prove the result.

## Family and Variant Model

Questions are organized by families. A family has one canonical version and may have several variants that are pedagogically useful.

Useful variant types:

- `canonical`
- `numeric_parameters`
- `assumption_change`
- `proof_variant`
- `counterexample_variant`
- `application_variant`
- `comparative_statics_variant`
- `interpretation_variant`

Near-duplicates are allowed only when they help drill a concept or expose a meaningful change in assumptions.

## JSONL Draft Format

Draft files in `drafts/` are JSON Lines. Each line is one question record:

```json
{
  "id": "micro-consumer-cobb-douglas-demand-001",
  "cluster_id": "micro-consumer-cobb-douglas-demand",
  "variant_of": null,
  "variant_type": "canonical",
  "title": "Marshallian Demand with Cobb-Douglas Preferences",
  "main_domain": "micro",
  "subdomain": "consumer_theory",
  "difficulty": "medium",
  "prerequisites": ["budget sets", "utility maximization", "Lagrange multipliers"],
  "learning_objective": "Derive Marshallian demand and indirect utility from a smooth utility maximization problem.",
  "preliminaries": "All prices are strictly positive and wealth is positive. A Marshallian demand solves max_x u(x) subject to p x <= w.",
  "question": "Full standalone prompt.",
  "solution": "Complete worked solution.",
  "source": {
    "type": "local_textbook",
    "family": "Varian Microeconomic Analysis",
    "file": "micro/Varian - Microeconomic Analysis.pdf",
    "locator": "chapter or topic anchor",
    "notes": "Inspired by the source topic, rewritten to be self-contained."
  },
  "validation": {
    "writer": "agent or editor name",
    "independent_solver": "agent or editor name",
    "validated_by": "agent or editor name",
    "status": "accepted",
    "notes": "Short correctness and clarity note."
  }
}
```

The integrated file is `curated_questions.json`; drafts stay available for audit.

## HTML and LaTeX Formatting

Question text is stored as plain strings intended for HTML rendering. Use LaTeX delimiters for all mathematical notation:

- inline math: `\\(x_i \\ge 0\\)`;
- display math: `\\[\\max_{x \\in X} f(x)\\]`;
- avoid raw Unicode mathematical symbols when a LaTeX command is clearer;
- avoid raw HTML tags inside `question`, `preliminaries`, and `solution`;
- write paragraphs as normal text separated by blank lines.

The frontend should render these fields with a MathJax/KaTeX-compatible renderer after HTML escaping the surrounding text.
