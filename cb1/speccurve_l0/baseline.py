from __future__ import annotations

from typing import Any

from .analysis import estimate_spec

BASELINE_SPEC = {
    "spec_id": "BASELINE_OLS",
    "outcome": "re78",
    "treatment": "treat",
    "covariates": [
        "age",
        "educ",
        "black",
        "hispan",
        "married",
        "nodegree",
        "re74",
        "re75",
        "u74",
        "u75",
    ],
    "outcome_transform": "raw",
    "sample_filter": "none",
    "estimator": "ols",
    "propensity_model": "none",
    "support_rule": "none",
    "rationale": "Canonical adjusted LaLonde-style baseline over demographics and prior earnings.",
}

MATCHING_BASELINE_SPEC = {
    "spec_id": "BASELINE_PSM_LOGIT",
    "outcome": "re78",
    "treatment": "treat",
    "covariates": [
        "age",
        "educ",
        "black",
        "hispan",
        "married",
        "nodegree",
        "re74",
        "re75",
        "u74",
        "u75",
    ],
    "outcome_transform": "raw",
    "sample_filter": "none",
    "estimator": "psm_1nn",
    "propensity_model": "logit_l2",
    "support_rule": "common_support_pscore",
    "rationale": "Paper-shaped propensity-score matching baseline for the NSW + PSID design.",
}


def run_baseline(rows: list[dict[str, float]]) -> dict[str, Any]:
    treated = [row["re78"] for row in rows if row["treat"] == 1.0]
    controls = [row["re78"] for row in rows if row["treat"] == 0.0]
    if not treated or not controls:
        raise ValueError("baseline requires treated and control rows")

    adjusted = estimate_spec(rows, BASELINE_SPEC)
    matching = estimate_spec(rows, MATCHING_BASELINE_SPEC)
    return {
        "baseline_id": "lalonde-att-baseline-v2",
        "unadjusted_att": sum(treated) / len(treated) - sum(controls) / len(controls),
        "adjusted_att": adjusted["estimate_att"],
        "adjusted_standard_error": adjusted["standard_error"],
        "adjusted_ci_low": adjusted["ci_low"],
        "adjusted_ci_high": adjusted["ci_high"],
        "matching_att": matching["estimate_att"],
        "matching_standard_error": matching["standard_error"],
        "matching_ci_low": matching["ci_low"],
        "matching_ci_high": matching["ci_high"],
        "matching_matched_treated": matching["matched_treated"],
        "treated_count": len(treated),
        "control_count": len(controls),
        "spec": BASELINE_SPEC,
        "matching_spec": MATCHING_BASELINE_SPEC,
    }
