#!/usr/bin/env python3
"""Extract practice questions from local PDF text dumps into canonical JSON.

The script intentionally records provenance and confidence metadata. Some source
PDFs are cleanly text-extractable, while others are OCR-noisy or effectively
empty, so generated solutions are marked by policy/status instead of pretending
that every item is equally verified.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
TEXT_DIR = ROOT / "extracted_text"
OUT_DIR = ROOT / "question_bank"


@dataclass(frozen=True)
class SourceSpec:
    text_file: str
    pdf_file: str
    main_domain: str
    family: str
    parser: str
    sub_domain: str | None = None


SOURCES: list[SourceSpec] = [
    SourceSpec("1._Real_Sequences.txt", "math/1. Real Sequences.pdf", "math", "ECON 6170 notes", "econ_notes", "real_sequences"),
    SourceSpec("2._Euclidean_Topology.txt", "math/2. Euclidean Topology.pdf", "math", "ECON 6170 notes", "econ_notes", "euclidean_topology"),
    SourceSpec("3._Convexity.txt", "math/3. Convexity.pdf", "math", "ECON 6170 notes", "econ_notes", "convexity"),
    SourceSpec("4._Correspondences.txt", "math/4. Correspondences.pdf", "math", "ECON 6170 notes", "econ_notes", "correspondences"),
    SourceSpec("4a._More_on_Correspondences.txt", "math/4a. More on Correspondences.pdf", "math", "ECON 6170 notes", "econ_notes", "correspondences"),
    SourceSpec("5._Differentiation.txt", "math/5. Differentiation.pdf", "math", "ECON 6170 notes", "econ_notes", "differentiation"),
    SourceSpec("6._Static_Optimisation.txt", "math/6. Static Optimisation.pdf", "math", "ECON 6170 notes", "econ_notes", "static_optimization"),
    SourceSpec("7._Comparative_Statics.txt", "math/7. Comparative Statics.pdf", "math", "ECON 6170 notes", "econ_notes", "comparative_statics"),
    SourceSpec("8._Fixed_Point_Theorems.txt", "math/8. Fixed Point Theorems.pdf", "math", "ECON 6170 notes", "econ_notes", "fixed_point_theorems"),
    SourceSpec("9._Duality.txt", "math/9. Duality.pdf", "math", "ECON 6170 notes", "econ_notes", "duality"),
    SourceSpec("Lecture_Notes.txt", "math/Lecture Notes.pdf", "math", "math lecture notes", "econ_notes", None),
    SourceSpec(
        "Foundations_of_Mathematical_Analysis_Pure__Applied_--_cRichard_Johnsonbaugh_W__E__Pfaffenberger_M__Dekker_--_Monographs_and_textbooks_in_pure_and_--_isbn13_9780824769192_--_1bfe773f5a0a4144940ca86323dfaffe_--_Annas_Archive.txt",
        "math/Foundations of Mathematical Analysis (Pure & Applied -- cRichard Johnsonbaugh, W_ E_ Pfaffenberger_,M_ Dekker -- Monographs and textbooks in pure and -- isbn13 9780824769192 -- 1bfe773f5a0a4144940ca86323dfaffe -- Anna’s Archive.pdf",
        "math",
        "Johnsonbaugh-Pfaffenberger Foundations",
        "numbered_math",
        None,
    ),
    SourceSpec("Simon_Blume_-_Mathematics_for_Economists.txt", "math/Simon, Blume - Mathematics for Economists.pdf", "math", "Simon-Blume Mathematics for Economists", "simon_math", None),
    SourceSpec("Varian_-_Microeconomic_Analysis.txt", "micro/Varian - Microeconomic Analysis.pdf", "micro", "Varian Microeconomic Analysis", "varian", None),
    SourceSpec("Kreps_-_Microeconomic_Foundations.txt", "micro/Kreps - Microeconomic Foundations.pdf", "micro", "Kreps Microeconomic Foundations", "kreps", None),
    SourceSpec("mascolell_ch2_exercises_ocr.txt", "micro/Mas-Colell, et al. - Microeconomic Theory.pdf", "micro", "Mas-Colell-Whinston-Green OCR", "mascolell_ocr", "consumer_theory"),
    SourceSpec("osborne_rubinstein.txt", "game theory/osborne rubinstein.pdf", "game_theory", "Osborne-Rubinstein Game Theory", "osborne", None),
    SourceSpec("tirole_ch1_exercises_ocr.txt", "game theory/tirole-game.pdf", "game_theory", "Fudenberg-Tirole Game Theory OCR", "tirole_ocr", "normal_form_games"),
]

SKIPPED_SOURCE_NOTES = [
    {
        "pdf_file": "math/Prof Knut Sydsaeter, Prof Peter Hammond, Prof Atle Seierstad, Prof Arne Strom - Further Mathematics for Economic Analysis (2009).pdf",
        "text_file": "extracted_text/Prof_Knut_Sydsaeter_Prof_Peter_Hammond_Prof_Atle_Seierstad_Prof_Arne_Strom_-_Further_Mathematics_for_Economic_Analysis_2009.txt",
        "reason": "OCR is usable for reading but problem segmentation is too noisy for automated inclusion without manual review",
    },
    {
        "pdf_file": "micro/Mas-Colell, et al. - Microeconomic Theory.pdf",
        "text_file": "extracted_text/Mas-Colell_et_al._-_Microeconomic_Theory.txt",
        "reason": "pdftotext output is effectively empty; only chapter 2 exercise pages are included from OCR in extracted_text_ocr/mascolell_ch2_exercises_ocr.txt",
    },
    {
        "pdf_file": "game theory/tirole-game.pdf",
        "text_file": "extracted_text/tirole-game.txt",
        "reason": "pdftotext output is effectively empty; only chapter 1 exercise pages are included from OCR in extracted_text_ocr/tirole_ch1_exercises_ocr.txt",
    },
]


VARIAN_CHAPTERS = {
    1: ("micro", "production_technology"),
    2: ("micro", "profit_maximization"),
    3: ("micro", "profit_function"),
    4: ("micro", "cost_minimization"),
    5: ("micro", "cost_functions"),
    6: ("micro", "production_duality"),
    7: ("micro", "consumer_theory"),
    8: ("micro", "demand_and_slutsky"),
    9: ("micro", "aggregation"),
    10: ("micro", "welfare_measurement"),
    11: ("micro", "choice_under_uncertainty"),
    12: ("micro", "empirical_demand_and_technology"),
    13: ("micro", "competitive_markets"),
    14: ("micro", "monopoly_and_price_discrimination"),
    15: ("game_theory", "normal_form_games"),
    16: ("game_theory", "oligopoly_games"),
    17: ("micro", "general_equilibrium_exchange"),
    18: ("micro", "general_equilibrium_production"),
    19: ("micro", "asset_markets"),
    20: ("micro", "asset_markets"),
    21: ("micro", "equilibrium_analysis"),
    22: ("micro", "welfare_economics"),
    23: ("micro", "public_goods"),
    24: ("micro", "externalities"),
    25: ("micro", "information_economics"),
}

KREPS_CHAPTERS = {
    1: "choice_preference_utility",
    2: "preference_structure",
    3: "choice_under_uncertainty",
    4: "consumer_choice",
    5: "expected_utility",
    6: "risk_aversion",
    7: "producer_theory",
    8: "cost_and_duality",
    9: "competitive_markets",
    10: "welfare",
    11: "general_equilibrium",
    12: "equilibrium_existence",
    13: "social_choice",
    14: "externalities",
    15: "public_goods",
    16: "information_and_incomplete_markets",
}

FOUNDATIONS_CHAPTERS = {
    1: "sets",
    2: "functions",
    3: "real_numbers",
    4: "order_and_inequalities",
    5: "supremum_infimum",
    6: "induction",
    7: "algebraic_structures",
    8: "countability",
    9: "countability",
    10: "sequences",
    11: "sequences",
    12: "limits",
    13: "limits",
    14: "limits",
    15: "infinite_limits",
    16: "monotone_sequences",
    17: "subsequences",
    18: "bolzano_weierstrass",
    19: "cauchy_sequences",
    20: "series",
    21: "series",
    22: "topology",
    23: "continuity",
    24: "continuity",
    25: "differentiation",
    26: "differentiation",
    27: "riemann_integration",
    28: "riemann_integration",
    29: "sequences_and_topology",
    30: "taylor_and_optimization",
}

SIMON_CHAPTERS = {
    2: "calculus",
    5: "exponential_logarithmic_functions",
    6: "linear_models",
    7: "linear_systems",
    10: "vectors_and_geometry",
    11: "linear_algebra",
    12: "topology",
    19: "constrained_optimization",
    20: "homogeneous_functions",
    22: "welfare_theorems",
    23: "eigenvalues",
    24: "differential_equations",
    25: "differential_equations",
    26: "determinants",
    29: "sequences_and_topology",
    30: "taylor_and_optimization",
}

NUMBERED_ITEM_START = re.compile(r"(?m)^\s*(\d{1,2})\.(\d{1,2})\s+")
NUMBERED_SECTION_STOP = re.compile(
    r"(?m)^\s*(?:[0-9]+\.\s+[A-Za-z][A-Za-z ,'-]{0,80}|CHAPTER\s+\d+|Chapter\s+\d+|Selected Answers|Bibliographic Notes|Notes)\s*$"
)
NUMBERED_EXERCISE_WORDS = {
    "let",
    "prove",
    "show",
    "give",
    "find",
    "if",
    "suppose",
    "why",
    "true",
    "use",
    "deduce",
    "complete",
    "when",
    "where",
    "solve",
    "compute",
    "determine",
    "which",
    "formalize",
    "for",
    "transform",
    "consider",
    "verify",
    "is",
}


def osborne_subdomain(page_number: int) -> str:
    if page_number <= 28:
        return "normal_form_games"
    if page_number <= 64:
        return "mixed_strategies_and_rationalizability"
    if page_number <= 81:
        return "knowledge_and_common_knowledge"
    if page_number <= 114:
        return "extensive_games_perfect_information"
    if page_number <= 157:
        return "bargaining_and_repeated_games"
    if page_number <= 191:
        return "implementation_and_mechanism_design"
    if page_number <= 253:
        return "extensive_games_imperfect_information"
    if page_number <= 296:
        return "coalitional_games"
    return "bargaining_solutions"


def slugify(value: str, max_len: int = 70) -> str:
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    value = re.sub(r"-+", "-", value)
    return value[:max_len].strip("-") or "item"


def collapse_ws(text: str) -> str:
    text = text.replace("\x0c", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def plain_one_line(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\x0c", " ")).strip()


def to_html_fragment(text: str) -> str:
    text = collapse_ws(text)
    if not text:
        return "<p></p>"
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    out = []
    for para in paras:
        escaped = html.escape(para)
        escaped = escaped.replace("\n", "<br>")
        out.append(f"<p>{escaped}</p>")
    return "\n".join(out)


def page_for_offset(text: str, offset: int) -> int:
    return text.count("\x0c", 0, max(offset, 0)) + 1


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, max(offset, 0)) + 1


def clean_prompt(raw: str) -> str:
    lines = []
    for line in collapse_ws(raw).splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if re.fullmatch(r"-?\d+-", stripped):
            continue
        if re.match(r"^(ECON\s+\d+|Fall\s+\d{4}|Spring\s+\d{4})\b", stripped):
            continue
        if re.match(r"^[A-Z][A-Za-z ]+\s+\d+$", stripped):
            continue
        lines.append(stripped)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def title_from_prompt(prompt: str, locator: str) -> str:
    text = plain_one_line(prompt)
    text = re.sub(r"^(Exercise|Problem)\s+[\w.*-]+(?:\s*\([^)]*\))?\.\s*", "", text, flags=re.I)
    text = re.sub(r"^\?+\s*", "", text)
    text = text[:110].strip(" .")
    return text or locator


def has_enough_prompt_text(prompt: str) -> bool:
    norm = re.sub(r"\W+", "", prompt.lower())
    if len(norm) < 20:
        return False
    if re.fullmatch(r"exercise\d+prove(this|proposition|theorem|corollary)?\d*", norm):
        return False
    return True


def task_type(prompt: str) -> str:
    low = prompt.lower()
    if "tfu" in low or "true or false" in low or "true/false" in low:
        return "tfu"
    if any(k in low for k in ["compute", "calculate", "find the", "solve ", "derive"]):
        return "compute"
    if any(k in low for k in ["give an example", "show by example", "counterexample", "prove or disprove"]):
        return "counterexample"
    if any(k in low for k in ["formulate", "define", "state "]):
        return "model_formulation"
    if any(k in low for k in ["show that", "prove", "verify"]):
        return "prove"
    if any(k in low for k in ["explain", "what is", "what are", "why"]):
        return "conceptual_explain"
    return "general"


def difficulty(locator_num: int | None, prompt: str) -> str:
    low = prompt.lower()
    if any(k in low for k in ["advanced", "difficult", "theorem", "kakutani", "folk theorem", "implementation"]):
        return "advanced"
    if locator_num is not None and locator_num <= 3:
        return "warmup"
    if any(k in low for k in ["derive", "kkt", "envelope", "duality", "mixed", "sequential", "walrasian"]):
        return "advanced"
    return "core"


def context_quality(prompt: str, parser: str) -> str:
    low = prompt.lower()
    if parser in {"numbered_math", "simon_math"}:
        return "bad_ocr" if has_ocr_artifacts(prompt) else "prompt_only"
    if parser in {"osborne", "varian"}:
        return "prompt_only"
    if "prove proposition" in low or "prove theorem" in low or "prove corollary" in low or "prove this" in low:
        return "nearby_theorem"
    if len(prompt) < 50 or "figure" in low or "table" in low:
        return "needs_source_check"
    return "full"


def has_ocr_artifacts(prompt: str) -> bool:
    low = prompt.lower()
    artifacts = ["jim", "theorcm", "suh", "follawing", "gauw", "funclion", "0)", "¢", "::::", "th~"]
    return any(token in low for token in artifacts)


def generic_hint(prompt: str, sub_domain: str, ttype: str) -> str:
    low = prompt.lower()
    if "hint:" in low:
        hint = re.split(r"hint\s*:", prompt, flags=re.I, maxsplit=1)[1]
        return to_html_fragment("Use the source hint: " + plain_one_line(hint)[:500])
    if ttype == "tfu":
        return to_html_fragment("First decide whether the statement follows directly from the relevant definition. If not, look for the smallest counterexample: a two-point set, a simple sequence, or a two-action game often suffices.")
    if ttype == "counterexample":
        return to_html_fragment("Start with a low-dimensional example. In analysis use subsets of R or R^2; in micro use Cobb-Douglas, Leontief, or linear preferences/technologies; in games use a 2 by 2 payoff matrix.")
    if ttype == "compute":
        return to_html_fragment("Write down the defining equations first, then simplify algebraically. Check boundary cases and verify that any candidate satisfies the original constraints.")
    if ttype == "model_formulation":
        return to_html_fragment("List the players or objects, feasible choices, payoffs/preferences, and the equilibrium or optimality concept before doing any calculation.")
    if ttype == "prove":
        return to_html_fragment("Unpack the definitions and identify the theorem whose assumptions match the exercise. Prove each required implication separately.")
    if "duality" in sub_domain:
        return to_html_fragment("Write the primal object, form the Lagrangian or conjugate object, and use weak duality before checking conditions for equality.")
    return to_html_fragment("Identify the relevant definition from the section, translate the prompt into that notation, and then prove or compute the requested claim step by step.")


def generic_solution(prompt: str, main_domain: str, sub_domain: str, ttype: str, quality: str) -> str:
    base = []
    if ttype == "tfu":
        base.append("A complete solution should state True/False/Uncertain, then justify the answer from the definition or give a counterexample.")
        base.append("For a true statement, write the relevant epsilon, order, convexity, optimality, or equilibrium condition and show it holds for arbitrary objects satisfying the hypotheses. For a false statement, provide a concrete object satisfying the hypotheses but violating the conclusion.")
    elif ttype == "counterexample":
        base.append("Construct an example with the smallest possible dimension and verify both parts: the hypotheses hold and the proposed conclusion fails.")
        base.append("Do not rely on a picture alone; compute the relevant set, derivative, payoff comparison, or preference relation explicitly.")
    elif ttype == "compute":
        base.append("Set up the relevant equations, solve for the unknowns, and substitute back into the original problem to check feasibility.")
        base.append("If the problem is an optimization problem, also check second-order or concavity conditions and any boundary constraints.")
    elif ttype == "model_formulation":
        base.append("The solution begins by specifying the primitives of the model: feasible choices, information, preferences/payoffs, and the equilibrium or optimality concept.")
        base.append("After the model is stated, derive best responses or optimality conditions and characterize the requested solution set.")
    elif ttype == "prove":
        base.append("Use the definitions named in the prompt and prove the required implication directly.")
        base.append("If the exercise references a proposition or theorem, first restate the result from the surrounding source text, then verify each assumption and reproduce the key argument.")
    else:
        base.append("Translate the prompt into the notation of the surrounding section, identify the relevant definition or theorem, and then carry out the requested proof or computation.")

    if main_domain == "game_theory":
        base.append("For game-theory items, finish by checking all unilateral deviations or by verifying the stated dominance, rationalizability, or subgame-perfect condition.")
    elif main_domain == "micro":
        base.append("For microeconomics items, finish by checking feasibility, monotonicity/convexity/concavity assumptions, and the relevant comparative-static or duality condition.")
    elif main_domain == "math":
        base.append("For math items, make quantifiers explicit and avoid assuming compactness, continuity, convexity, or differentiability unless the prompt gives it.")

    if quality != "full":
        base.append(f"Source-context note: this item was extracted with context quality `{quality}`; compare the solution outline with the surrounding source text before treating it as final.")
    return to_html_fragment(" ".join(base))


def read_text_file(name: str) -> str:
    path = TEXT_DIR / name
    if not path.exists():
        path = ROOT / "extracted_text_ocr" / name
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def iter_econ_note_exercises(spec: SourceSpec, text: str) -> Iterable[dict]:
    pattern = re.compile(r"(?m)^Exercise\s+(\d+)(?:\s*\(([^)]*)\))?\.\s*")
    stops = re.compile(
        r"(?m)^(Exercise\s+\d+|Definition\s+\d+|Proposition\s+\d+|Theorem\s+\d+|Axiom\s+\d+|Remark\s+\d+|Example\s+\d+|Corollary\s+\d+|Lemma\s+\d+|Proof\.|[0-9]+(?:\.[0-9]+)+\s+[A-Z])"
    )
    matches = list(pattern.finditer(text))
    for i, match in enumerate(matches):
        next_start = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        stop_match = stops.search(text, match.end(), next_start)
        end = stop_match.start() if stop_match else next_start
        raw = text[match.start():end]
        prompt = clean_prompt(raw)
        if not has_enough_prompt_text(prompt):
            continue
        number = int(match.group(1))
        label = f"Exercise {number}"
        sub = spec.sub_domain or infer_subdomain_from_text(prompt)
        yield make_record(spec, text, match.start(), label, number, prompt, spec.main_domain, sub)


def iter_varian_exercises(spec: SourceSpec, text: str, answers: dict[str, str]) -> Iterable[dict]:
    start = text.find("\nExercises")
    end = text.find("\n                   ANSWERS")
    body = text[start:end if end != -1 else len(text)]
    pattern = re.compile(r"(?m)^\s*(\d{1,2})\.(\d{1,2})\.\s+")
    matches = list(pattern.finditer(body))
    for i, match in enumerate(matches):
        next_start = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        raw = body[match.start():next_start]
        if re.search(r"(?m)^\s*(CHAPTER|Chapter)\s+\d+", raw):
            raw = re.split(r"(?m)^\s*(CHAPTER|Chapter)\s+\d+", raw, maxsplit=1)[0]
        prompt = clean_prompt(raw)
        if not has_enough_prompt_text(prompt):
            continue
        chapter = int(match.group(1))
        number = int(match.group(2))
        main, sub = VARIAN_CHAPTERS.get(chapter, ("micro", "microeconomics"))
        label = f"{chapter}.{number}"
        rec = make_record(spec, text, start + match.start(), label, number, prompt, main, sub)
        if label in answers:
            rec["solution"] = to_html_fragment(f"Selected answer from source:\n\n{answers[label]}")
            rec["solution_policy"] = "source_solution"
            rec["status"] = "reviewed"
            rec["quality_flags"].append("matched_selected_answer")
        yield rec


def iter_kreps_problems(spec: SourceSpec, text: str) -> Iterable[dict]:
    cutoff = text.find("\nA1.")
    body = text[: cutoff if cutoff != -1 else len(text)]
    pattern = re.compile(r"(?m)^■\s*(\*)?(\d{1,2})\.(\d{1,2})\.\s+")
    matches = list(pattern.finditer(body))
    for i, match in enumerate(matches):
        next_start = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        raw = body[match.start():next_start]
        prompt = clean_prompt(raw)
        if not has_enough_prompt_text(prompt):
            continue
        chapter = int(match.group(2))
        number = int(match.group(3))
        sub = KREPS_CHAPTERS.get(chapter, "microeconomic_theory")
        label = f"{chapter}.{number}"
        rec = make_record(spec, text, match.start(), label, number, prompt, "micro", sub)
        if match.group(1):
            rec["quality_flags"].append("starred_problem_has_external_solution")
        yield rec


def looks_like_numbered_exercise(prompt: str) -> bool:
    first_line = plain_one_line(prompt).split(" ", 1)
    if len(first_line) < 2:
        return False
    rest = first_line[1].strip()
    if not rest:
        return False
    if rest.upper() == rest and len(rest) > 8:
        return False
    word = re.sub(r"[^A-Za-z]", "", rest.split()[0]).lower()
    return word in NUMBERED_EXERCISE_WORDS


def iter_numbered_math_exercises(spec: SourceSpec, text: str, answers: dict[str, str] | None = None) -> Iterable[dict]:
    answers = answers or {}
    if spec.parser == "simon_math":
        cut = text.rfind("Selected Answers")
        body_start = 0
        body_end = cut if cut > 0 else len(text)
        chapter_map = SIMON_CHAPTERS
    else:
        body_start = 0
        body_end = len(text)
        chapter_map = FOUNDATIONS_CHAPTERS

    body = text[body_start:body_end]
    matches = list(NUMBERED_ITEM_START.finditer(body))
    for i, match in enumerate(matches):
        next_start = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        raw = body[match.start():next_start]
        stop = NUMBERED_SECTION_STOP.search(raw, match.end() - match.start())
        if stop:
            raw = raw[: stop.start()]
        prompt = clean_prompt(raw)
        if not has_enough_prompt_text(prompt) or not looks_like_numbered_exercise(prompt):
            continue
        chapter = int(match.group(1))
        number = int(match.group(2))
        if spec.parser == "numbered_math" and chapter > 30:
            continue
        sub = chapter_map.get(chapter, infer_subdomain_from_text(prompt))
        offset = body_start + match.start()
        rec = make_record(spec, text, offset, f"{chapter}.{number}", number, prompt, "math", sub)
        if spec.parser == "numbered_math":
            rec["quality_flags"].append("ocr_extracted_math_text")
            if rec["status"] == "draft":
                rec["status"] = "needs_source_check"
        if spec.parser == "simon_math":
            rec["quality_flags"].append("partial_textbook_extraction")
            if f"{chapter}.{number}" in answers:
                rec["solution"] = to_html_fragment(f"Selected answer from source:\n\n{answers[f'{chapter}.{number}']}")
                rec["solution_policy"] = "source_solution"
                rec["status"] = "reviewed"
                rec["quality_flags"].append("matched_selected_answer")
        yield rec


def parse_numbered_answers(text: str, start_marker: str, end_marker: str | None = None) -> dict[str, str]:
    start = text.rfind(start_marker)
    if start < 0:
        return {}
    end = len(text)
    if end_marker:
        end_pos = text.find(end_marker, start)
        if end_pos > start:
            end = end_pos
    body = text[start:end]
    pattern = re.compile(r"(?m)^\s*(\d{1,2}\.\d{1,2})(?:\.[a-z])?\s+")
    matches = list(pattern.finditer(body))
    grouped: dict[str, list[str]] = {}
    for i, match in enumerate(matches):
        next_start = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        raw = clean_prompt(body[match.start():next_start])
        if not has_enough_prompt_text(raw):
            continue
        base = match.group(1)
        grouped.setdefault(base, []).append(raw)
    return {key: "\n\n".join(parts) for key, parts in grouped.items()}


def parse_osborne_solutions() -> dict[str, str]:
    text = read_text_file("Martin_J._Osborne_and_Ariel_Rubinstein_SOLUTIONS.txt")
    if not text:
        return {}
    pattern = re.compile(r"(?m)^(\d{2,3}\.\d+)\s*\(([^)]*)\)\s*")
    matches = list(pattern.finditer(text))
    solutions: dict[str, str] = {}
    for i, match in enumerate(matches):
        next_start = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        raw = text[match.start():next_start]
        raw = re.split(r"(?m)^?\s*(Chapter\s+\d+|References|Index)\b", raw, maxsplit=1)[0]
        cleaned = clean_prompt(raw)
        if len(cleaned) >= 20:
            solutions[match.group(1)] = cleaned
    return solutions


def iter_osborne_exercises(spec: SourceSpec, text: str, solutions: dict[str, str]) -> Iterable[dict]:
    pattern = re.compile(r"(?m)^\?\s*Exercise\s+(\d{2,3})\.(\d+)(?:\s*\(([^)]*)\))?\s+")
    matches = list(pattern.finditer(text))
    for i, match in enumerate(matches):
        next_start = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        raw = text[match.start():next_start]
        raw = re.split(r"(?m)^\s*(Notes|Bibliographic Notes|References)\b", raw, maxsplit=1)[0]
        prompt = clean_prompt(raw)
        if not has_enough_prompt_text(prompt):
            continue
        page_num = int(match.group(1))
        ex_num = int(match.group(2))
        sub = osborne_subdomain(page_num)
        label = f"{page_num}.{ex_num}"
        rec = make_record(spec, text, match.start(), label, ex_num, prompt, "game_theory", sub)
        sol = solutions.get(label)
        if sol:
            rec["hint"] = generic_hint(prompt, sub, rec["task_type"])
            rec["solution"] = to_html_fragment(sol)
            rec["status"] = "reviewed"
            rec["solution_policy"] = "source_solution"
            rec["quality_flags"].append("matched_solution_manual")
        yield rec


def ocr_page_for_offset(text: str, offset: int) -> int:
    markers = list(re.finditer(r"=== page-(\d+) ===", text[:offset]))
    if markers:
        return int(markers[-1].group(1))
    return page_for_offset(text, offset)


def iter_tirole_ocr_exercises(spec: SourceSpec, text: str) -> Iterable[dict]:
    pattern = re.compile(r"(?m)^Exercise\s+(\d+)\.(\d+)\**(?:\s*\(([^)]*)\))?\s*")
    matches = list(pattern.finditer(text))
    for i, match in enumerate(matches):
        next_start = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        raw = text[match.start():next_start]
        raw = re.split(r"(?m)^\s*(References|=== page-\d+ ===)\b", raw, maxsplit=1)[0]
        prompt = clean_prompt(raw)
        if not has_enough_prompt_text(prompt):
            continue
        chapter = int(match.group(1))
        number = int(match.group(2))
        label = f"{chapter}.{number}"
        rec = make_record(spec, text, match.start(), label, number, prompt, "game_theory", "normal_form_games")
        rec["source"]["text_file"] = f"extracted_text_ocr/{spec.text_file}"
        rec["source"]["page"] = ocr_page_for_offset(text, match.start())
        rec["status"] = "needs_source_check"
        rec["context_quality"] = "bad_ocr"
        rec["quality_flags"].append("ocr_extracted_scanned_pdf")
        yield rec


def iter_mascolell_ocr_exercises(spec: SourceSpec, text: str) -> Iterable[dict]:
    pattern = re.compile(r"(?m)^(\d+)\.([A-Za-z])[\.:]([0-9I]+)[^A-Za-z0-9\n]*\s*")
    matches = list(pattern.finditer(text))
    section_subdomains = {
        "D": "budget_sets",
        "E": "demand_functions",
        "F": "revealed_preference",
    }
    for i, match in enumerate(matches):
        next_start = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        raw = text[match.start():next_start]
        raw = re.split(r"(?m)^\s*(=== page-\d+ ===|SECTION\s+\d+|CHAPTER\s+\d+|References)\b", raw, maxsplit=1)[0]
        prompt = clean_prompt(raw)
        if not has_enough_prompt_text(prompt):
            continue
        chapter = int(match.group(1))
        section = match.group(2).upper()
        number_text = match.group(3).replace("I", "1")
        if chapter == 2 and section == "E" and number_text == "17":
            # OCR drops the crossbar in the printed "F" for this item.
            section = "F"
        try:
            number = int(number_text)
        except ValueError:
            number = None
        sub = section_subdomains.get(section, "consumer_theory")
        label = f"{chapter}.{section}.{number_text}"
        rec = make_record(spec, text, match.start(), label, number, prompt, "micro", sub)
        rec["source"]["text_file"] = f"extracted_text_ocr/{spec.text_file}"
        rec["source"]["page"] = ocr_page_for_offset(text, match.start())
        rec["status"] = "needs_source_check"
        rec["context_quality"] = "bad_ocr"
        rec["quality_flags"].append("ocr_extracted_scanned_pdf")
        yield rec


def infer_subdomain_from_text(prompt: str) -> str:
    low = prompt.lower()
    for key, sub in [
        ("sequence", "real_sequences"),
        ("sup", "real_sequences"),
        ("inf", "real_sequences"),
        ("open", "euclidean_topology"),
        ("closed", "euclidean_topology"),
        ("compact", "euclidean_topology"),
        ("convex", "convexity"),
        ("concave", "convexity"),
        ("correspondence", "correspondences"),
        ("differentia", "differentiation"),
        ("implicit", "differentiation"),
        ("lagrange", "static_optimization"),
        ("kkt", "static_optimization"),
        ("envelope", "comparative_statics"),
        ("supermodular", "comparative_statics"),
        ("fixed point", "fixed_point_theorems"),
        ("duality", "duality"),
    ]:
        if key in low:
            return sub
    return "math_for_economics"


def make_record(
    spec: SourceSpec,
    full_text: str,
    offset: int,
    locator: str,
    locator_num: int | None,
    prompt: str,
    main_domain: str,
    sub_domain: str,
) -> dict:
    ttype = task_type(prompt)
    quality = context_quality(prompt, spec.parser)
    qid = f"{slugify(main_domain)}-{slugify(sub_domain)}-{slugify(spec.family)}-{slugify(locator, 18)}"
    record = {
        "id": qid,
        "main_domain": main_domain,
        "sub_domain": sub_domain,
        "title": title_from_prompt(prompt, locator),
        "difficulty": difficulty(locator_num, prompt),
        "source_family": spec.family,
        "source": {
            "family": spec.family,
            "file": spec.pdf_file,
            "text_file": f"extracted_text/{spec.text_file}",
            "page": page_for_offset(full_text, offset),
            "line": line_for_offset(full_text, offset),
            "locator": locator,
        },
        "topics": topic_tags(main_domain, sub_domain, prompt),
        "task_type": ttype,
        "context_quality": quality,
        "solution_policy": "generated_outline",
        "prompt": to_html_fragment(prompt),
        "prompt_text": plain_one_line(prompt),
        "hint": generic_hint(prompt, sub_domain, ttype),
        "solution": generic_solution(prompt, main_domain, sub_domain, ttype, quality),
        "status": "draft" if quality in {"full", "prompt_only"} else "needs_source_check",
        "quality_flags": [],
    }
    if "figure" in prompt.lower() or "table" in prompt.lower():
        record["quality_flags"].append("may_depend_on_figure_or_table")
        record["status"] = "needs_source_check"
    if len(prompt) > 2500:
        record["quality_flags"].append("long_prompt_review_formatting")
    return record


def topic_tags(main_domain: str, sub_domain: str, prompt: str) -> list[str]:
    tags = [main_domain.replace("_", " "), sub_domain.replace("_", " ")]
    low = prompt.lower()
    for key, tag in [
        ("tfu", "true false uncertain"),
        ("true or false", "true false"),
        ("prove", "proof"),
        ("counterexample", "counterexample"),
        ("example", "examples"),
        ("lagrange", "lagrangian"),
        ("kkt", "kkt"),
        ("nash", "nash equilibrium"),
        ("dominant", "dominance"),
        ("mixed", "mixed strategies"),
        ("convex", "convexity"),
        ("compact", "compactness"),
        ("continu", "continuity"),
        ("duality", "duality"),
        ("envelope", "envelope theorem"),
        ("slutsky", "slutsky"),
    ]:
        if key in low and tag not in tags:
            tags.append(tag)
    return tags[:8]


def load_records() -> tuple[list[dict], dict]:
    records: list[dict] = []
    manifest = {
        "sources": [],
        "skipped_sources": [],
    }
    osborne_solutions = parse_osborne_solutions()
    varian_answers = parse_numbered_answers(
        read_text_file("Varian_-_Microeconomic_Analysis.txt"),
        "\x0c                   ANSWERS",
        "INDEX",
    )
    # The Simon-Blume selected-answer appendix OCR confuses labels such as
    # 2.11 with 2.1 I, so automatic answer matching is not reliable enough.
    simon_answers: dict[str, str] = {}

    for spec in SOURCES:
        text = read_text_file(spec.text_file)
        text_rel = f"extracted_text_ocr/{spec.text_file}" if spec.parser.endswith("_ocr") else f"extracted_text/{spec.text_file}"
        source_info = {
            "pdf_file": spec.pdf_file,
            "text_file": text_rel,
            "parser": spec.parser,
            "bytes": len(text.encode(errors="replace")),
            "records": 0,
        }
        if len(text.strip()) < 1000:
            source_info["reason"] = "text extraction too sparse"
            manifest["skipped_sources"].append(source_info)
            continue
        before = len(records)
        if spec.parser == "econ_notes":
            records.extend(iter_econ_note_exercises(spec, text))
        elif spec.parser == "varian":
            records.extend(iter_varian_exercises(spec, text, varian_answers))
        elif spec.parser == "kreps":
            records.extend(iter_kreps_problems(spec, text))
        elif spec.parser == "osborne":
            records.extend(iter_osborne_exercises(spec, text, osborne_solutions))
        elif spec.parser == "tirole_ocr":
            records.extend(iter_tirole_ocr_exercises(spec, text))
        elif spec.parser == "mascolell_ocr":
            records.extend(iter_mascolell_ocr_exercises(spec, text))
        elif spec.parser == "numbered_math":
            records.extend(iter_numbered_math_exercises(spec, text))
        elif spec.parser == "simon_math":
            records.extend(iter_numbered_math_exercises(spec, text, simon_answers))
        source_info["records"] = len(records) - before
        manifest["sources"].append(source_info)

    for note in SKIPPED_SOURCE_NOTES:
        note = dict(note)
        path = ROOT / note["text_file"]
        note["bytes"] = path.stat().st_size if path.exists() else 0
        manifest["skipped_sources"].append(note)

    deduped = []
    seen_ids: dict[str, int] = {}
    seen_prompts = set()
    for rec in records:
        normalized_prompt = re.sub(r"\W+", "", rec["prompt_text"].lower())[:300]
        if normalized_prompt in seen_prompts:
            continue
        seen_prompts.add(normalized_prompt)
        base_id = rec["id"]
        count = seen_ids.get(base_id, 0)
        if count:
            rec["id"] = f"{base_id}-{count + 1}"
        seen_ids[base_id] = count + 1
        deduped.append(rec)

    return deduped, manifest


def summarize(records: list[dict], manifest: dict) -> dict:
    by_domain: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for rec in records:
        by_domain[rec["main_domain"]] = by_domain.get(rec["main_domain"], 0) + 1
        by_status[rec["status"]] = by_status.get(rec["status"], 0) + 1
        src = rec["source"]["file"]
        by_source[src] = by_source.get(src, 0) + 1
    return {
        "total_questions": len(records),
        "by_domain": dict(sorted(by_domain.items())),
        "by_status": dict(sorted(by_status.items())),
        "by_source": dict(sorted(by_source.items())),
        "source_manifest": manifest,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(OUT_DIR / "questions.json"))
    parser.add_argument("--summary", default=str(OUT_DIR / "summary.json"))
    args = parser.parse_args()

    out_path = Path(args.out)
    summary_path = Path(args.summary)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    records, manifest = load_records()
    out_path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")
    summary_path.write_text(json.dumps(summarize(records, manifest), indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {len(records)} questions to {out_path}")
    print(f"wrote summary to {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
