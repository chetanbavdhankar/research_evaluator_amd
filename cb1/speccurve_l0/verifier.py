from __future__ import annotations

from typing import Any

ALLOWED_OUTCOME = "re78"
ALLOWED_TREATMENT = "treat"
ALLOWED_TRANSFORMS = {"raw", "log1p"}
ALLOWED_FILTERS = {"none", "common_support_re75", "positive_prior_earnings", "age_18_45"}
ALLOWED_ESTIMATORS = {"ols", "ridge_1e-6", "psm_1nn", "ipw_att", "mahalanobis_1nn", "cem_att"}
ALLOWED_PROPENSITY_MODELS = {"none", "logit_l2", "probit_gradient"}
ALLOWED_SUPPORT_RULES = {
    "none",
    "common_support_pscore",
    "caliper_0.05",
    "trim_0.05_0.95",
    "clip_0.02_0.98",
}
PROPENSITY_ESTIMATORS = {"psm_1nn", "ipw_att"}


def verify_spec(spec: dict[str, Any], dataset_columns: set[str]) -> dict[str, Any]:
    errors: list[str] = []

    outcome = spec.get("outcome")
    treatment = spec.get("treatment")
    covariates = list(spec.get("covariates", []))
    outcome_transform = spec.get("outcome_transform")
    sample_filter = spec.get("sample_filter")
    estimator = spec.get("estimator")
    propensity_model = spec.get("propensity_model", "none")
    support_rule = spec.get("support_rule", "none")

    if outcome != ALLOWED_OUTCOME:
        errors.append(f"outcome must stay locked to {ALLOWED_OUTCOME}")
    if treatment != ALLOWED_TREATMENT:
        errors.append(f"treatment must stay locked to {ALLOWED_TREATMENT}")
    if outcome_transform not in ALLOWED_TRANSFORMS:
        errors.append("outcome transform is not in the approved grid")
    if sample_filter not in ALLOWED_FILTERS:
        errors.append("sample filter is not in the approved grid")
    if estimator not in ALLOWED_ESTIMATORS:
        errors.append("estimator is not in the approved grid")
    if propensity_model not in ALLOWED_PROPENSITY_MODELS:
        errors.append("propensity model is not in the approved grid")
    if support_rule not in ALLOWED_SUPPORT_RULES:
        errors.append("support rule is not in the approved grid")
    if estimator in PROPENSITY_ESTIMATORS and propensity_model == "none":
        errors.append("matching/weighting estimator requires a declared propensity model")
    if estimator not in PROPENSITY_ESTIMATORS and propensity_model != "none":
        errors.append("propensity model is only allowed for propensity-based estimators")
    if estimator not in PROPENSITY_ESTIMATORS and support_rule != "none":
        errors.append("support rule is only allowed for propensity-based estimators")
    if estimator != "psm_1nn" and support_rule == "caliper_0.05":
        errors.append("caliper support is only allowed for propensity-score matching")
    if estimator != "ipw_att" and support_rule in {"trim_0.05_0.95", "clip_0.02_0.98"}:
        errors.append("trim or clipping support is only allowed for IPW")

    missing = [column for column in [outcome, treatment, *covariates] if column not in dataset_columns]
    if missing:
        errors.append(f"missing dataset columns: {', '.join(str(column) for column in missing)}")
    if outcome in covariates:
        errors.append("outcome leakage: outcome appears in covariates")
    if treatment in covariates:
        errors.append("treatment leakage: treatment appears in covariates")
    if len(covariates) != len(set(covariates)):
        errors.append("duplicate covariates are not allowed")

    return {
        "spec_id": spec.get("spec_id", "unknown"),
        "approved": not errors,
        "errors": errors,
        "spec": spec,
    }


def verify_specs(specs: list[dict[str, Any]], dataset_columns: set[str]) -> dict[str, list[dict[str, Any]]]:
    approved: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for spec in specs:
        result = verify_spec(spec, dataset_columns)
        if result["approved"]:
            approved.append(spec)
        else:
            rejected.append(result)
    return {"approved": approved, "rejected": rejected}
