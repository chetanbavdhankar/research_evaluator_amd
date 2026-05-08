from __future__ import annotations

import math
from typing import Any

from .linear import fit_linear_model
from .matching import estimate_matching_or_weighting

MATCHING_WEIGHTING_ESTIMATORS = {"psm_1nn", "ipw_att", "mahalanobis_1nn", "cem_att"}


def apply_filter(rows: list[dict[str, float]], sample_filter: str) -> list[dict[str, float]]:
    if sample_filter == "none":
        return rows[:]
    if sample_filter == "positive_prior_earnings":
        return [row for row in rows if row["re74"] > 0 or row["re75"] > 0]
    if sample_filter == "age_18_45":
        return [row for row in rows if 18 <= row["age"] <= 45]
    if sample_filter == "common_support_re75":
        treated = [row["re75"] for row in rows if row["treat"] == 1.0]
        controls = [row["re75"] for row in rows if row["treat"] == 0.0]
        if not treated or not controls:
            return []
        lower = max(min(treated), min(controls))
        upper = min(max(treated), max(controls))
        return [row for row in rows if lower <= row["re75"] <= upper]
    raise ValueError(f"unknown sample filter: {sample_filter}")


def transform_outcome(value: float, transform: str) -> float:
    if transform == "raw":
        return value
    if transform == "log1p":
        return math.log1p(max(0.0, value))
    raise ValueError(f"unknown outcome transform: {transform}")


def design_matrix(rows: list[dict[str, float]], spec: dict[str, Any]) -> tuple[list[list[float]], list[float]]:
    covariates = list(spec["covariates"])
    design: list[list[float]] = []
    outcome: list[float] = []
    for row in rows:
        design.append([1.0, row[spec["treatment"]], *[row[column] for column in covariates]])
        outcome.append(transform_outcome(row[spec["outcome"]], spec["outcome_transform"]))
    return design, outcome


def estimate_spec(rows: list[dict[str, float]], spec: dict[str, Any]) -> dict[str, Any]:
    filtered = apply_filter(rows, str(spec["sample_filter"]))
    if len(filtered) < len(spec["covariates"]) + 8:
        raise ValueError(f"spec {spec['spec_id']} has too few rows after filtering")

    if spec["estimator"] in MATCHING_WEIGHTING_ESTIMATORS:
        return estimate_matching_or_weighting(filtered, spec)

    ridge = 1e-6 if spec["estimator"] == "ridge_1e-6" else 0.0
    design, outcome = design_matrix(filtered, spec)
    fit = fit_linear_model(design, outcome, ridge_lambda=ridge)
    beta = fit["beta"]
    standard_errors = fit["standard_errors"]
    estimate = float(beta[1])
    standard_error = float(standard_errors[1])
    ci_low = estimate - 1.96 * standard_error
    ci_high = estimate + 1.96 * standard_error

    return {
        "spec_id": spec["spec_id"],
        "estimate_att": estimate,
        "standard_error": standard_error,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "n": fit["n"],
        "outcome_transform": spec["outcome_transform"],
        "sample_filter": spec["sample_filter"],
        "estimator": spec["estimator"],
        "propensity_model": spec.get("propensity_model", "none"),
        "support_rule": spec.get("support_rule", "none"),
        "covariate_count": len(spec["covariates"]),
        "method_family": "outcome_model",
        "sign": "positive" if estimate > 0 else "negative" if estimate < 0 else "zero",
    }


def estimate_specs(rows: list[dict[str, float]], specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for spec in specs:
        results.append(estimate_spec(rows, spec))
    return results
