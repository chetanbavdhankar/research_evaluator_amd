from __future__ import annotations

import re
from collections import Counter

from .agentic_schema import ReproductionWorkflowPlan, VerificationReport


REQUIRED_ACTIONS = {
    "read_paper",
    "acquire_data",
    "prepare_environment",
    "preprocess_data",
    "run_analysis",
    "run_robustness",
    "verify_results",
    "write_report",
}

EXECUTABLE_ACTIONS = {
    "acquire_data",
    "prepare_environment",
    "preprocess_data",
    "run_analysis",
    "run_robustness",
}

FORBIDDEN_CERTAINTY = (
    "proves " + "the paper",
    "proves " + "the claim",
    "truth " + "verdict",
    "fr" + "aud",
    "guaranteed reproduction",
)


def verify_reproduction_plan(
    plan: ReproductionWorkflowPlan,
    paper_text: str,
    min_score: float = 0.82,
) -> VerificationReport:
    checks: list[str] = []
    failures: list[str] = []
    warnings: list[str] = []

    checks.append("claim_quote_grounded")
    if not _quote_grounded(plan.claim_quote, paper_text):
        failures.append("claim_quote is not grounded in the supplied paper text")

    checks.append("required_action_coverage")
    actions = {step.action_type for step in plan.workflow_steps}
    missing_actions = sorted(REQUIRED_ACTIONS - actions)
    if missing_actions:
        failures.append(f"workflow is missing required action types: {', '.join(missing_actions)}")

    checks.append("sandbox_for_executable_steps")
    unsafe_steps = [
        step.step_id
        for step in plan.workflow_steps
        if step.action_type in EXECUTABLE_ACTIONS and not step.sandbox_required
    ]
    if unsafe_steps:
        failures.append(f"executable steps must require sandboxing: {', '.join(unsafe_steps)}")

    checks.append("verifier_checks_present")
    unverifiable_steps = [step.step_id for step in plan.workflow_steps if not step.verifier_checks]
    if unverifiable_steps:
        failures.append(f"steps without verifier checks: {', '.join(unverifiable_steps)}")

    checks.append("robustness_dimensions_grounded")
    if len(plan.robustness_dimensions) < 2:
        failures.append("plan needs at least two robustness dimensions")
    ungrounded_dimensions = [
        dimension.name
        for dimension in plan.robustness_dimensions
        if dimension.source_quote and not _quote_grounded(dimension.source_quote, paper_text)
    ]
    if ungrounded_dimensions:
        warnings.append(
            "some robustness dimensions are weakly grounded: "
            + ", ".join(ungrounded_dimensions)
        )

    checks.append("artifact_contract")
    required_artifact_terms = ("workflow", "dataset", "result", "report")
    artifact_text = " ".join(plan.expected_artifacts).lower()
    for term in required_artifact_terms:
        if term not in artifact_text:
            failures.append(f"expected_artifacts should include a {term} artifact")

    checks.append("stop_conditions")
    stop_text = " ".join(plan.stop_conditions).lower()
    for term in ("missing data", "unsafe", "unverifiable"):
        if term not in stop_text:
            failures.append(f"stop_conditions should mention {term}")

    checks.append("overclaim_language")
    plan_text = str(plan.to_dict()).lower()
    for phrase in FORBIDDEN_CERTAINTY:
        if phrase in plan_text:
            failures.append(f"forbidden overclaim language: {phrase}")

    checks.append("action_balance")
    counts = Counter(step.action_type for step in plan.workflow_steps)
    if counts["run_analysis"] > 3 or counts["run_robustness"] > 3:
        warnings.append("workflow may be over-weighted toward execution without enough verification")

    score = _score(checks, failures, warnings)
    return VerificationReport(
        passed=not failures and score >= min_score,
        score=score,
        checks=tuple(checks),
        failures=tuple(failures),
        warnings=tuple(warnings),
    )


def _score(checks: list[str], failures: list[str], warnings: list[str]) -> float:
    if not checks:
        return 0.0
    penalty = 0.16 * len(failures) + 0.04 * len(warnings)
    return max(0.0, min(1.0, 1.0 - penalty))


def _quote_grounded(quote: str, source_text: str) -> bool:
    quote = " ".join(quote.split())
    source = " ".join(source_text.split())
    if not quote:
        return False
    if quote in source:
        return True
    quote_tokens = _tokens(quote)
    source_tokens = set(_tokens(source))
    if len(quote_tokens) < 5:
        return all(token in source_tokens for token in quote_tokens)
    overlap = sum(1 for token in quote_tokens if token in source_tokens)
    return overlap / len(quote_tokens) >= 0.72


def _tokens(value: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]+", value.lower())
