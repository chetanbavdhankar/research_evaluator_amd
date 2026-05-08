from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

MIN_SCORE = 1e-4
MAX_SCORE = 1.0 - MIN_SCORE
_PROPENSITY_SCORE_CACHE: dict[tuple[tuple[int, ...], tuple[str, ...], str, str], list[float]] = {}


def estimate_matching_or_weighting(
    rows: list[dict[str, float]],
    spec: dict[str, Any],
) -> dict[str, Any]:
    estimator = str(spec["estimator"])
    if estimator == "psm_1nn":
        return _estimate_psm(rows, spec)
    if estimator == "ipw_att":
        return _estimate_ipw_att(rows, spec)
    if estimator == "mahalanobis_1nn":
        return _estimate_mahalanobis(rows, spec)
    if estimator == "cem_att":
        return _estimate_cem(rows, spec)
    raise ValueError(f"unsupported matching/weighting estimator: {estimator}")


def _estimate_psm(rows: list[dict[str, float]], spec: dict[str, Any]) -> dict[str, Any]:
    pairs = _rows_with_scores(rows, spec)
    pairs = _apply_score_support(pairs, str(spec.get("support_rule", "none")))
    treated = [(row, score) for row, score in pairs if row[spec["treatment"]] == 1.0]
    controls = [(row, score) for row, score in pairs if row[spec["treatment"]] == 0.0]
    _require_groups(treated, controls, spec)

    caliper = 0.05 if spec.get("support_rule") == "caliper_0.05" else None
    contributions: list[float] = []
    for treated_row, treated_score in treated:
        control_row, control_score = min(controls, key=lambda item: abs(item[1] - treated_score))
        if caliper is not None and abs(control_score - treated_score) > caliper:
            continue
        contributions.append(_outcome(treated_row, spec) - _outcome(control_row, spec))

    return _result_from_contributions(spec, contributions, n_controls=len(controls))


def _estimate_ipw_att(rows: list[dict[str, float]], spec: dict[str, Any]) -> dict[str, Any]:
    pairs = _rows_with_scores(rows, spec)
    pairs = _apply_score_support(pairs, str(spec.get("support_rule", "none")))
    treated = [(row, score) for row, score in pairs if row[spec["treatment"]] == 1.0]
    controls = [(row, score) for row, score in pairs if row[spec["treatment"]] == 0.0]
    _require_groups(treated, controls, spec)

    treated_values = [_outcome(row, spec) for row, _score in treated]
    control_values = [_outcome(row, spec) for row, _score in controls]
    control_scores = [
        _clip_score(score, 0.02, 0.98) if spec.get("support_rule") == "clip_0.02_0.98" else score
        for _row, score in controls
    ]
    control_weights = [score / (1.0 - score) for score in control_scores]
    control_weight_total = sum(control_weights)
    if control_weight_total <= 0:
        raise ValueError(f"spec {spec['spec_id']} has zero IPW control weight")

    treated_mean = sum(treated_values) / len(treated_values)
    weighted_control_mean = sum(
        weight * value for weight, value in zip(control_weights, control_values, strict=True)
    ) / control_weight_total
    estimate = treated_mean - weighted_control_mean
    treated_se = _variance(treated_values) / len(treated_values)
    control_ess = control_weight_total * control_weight_total / sum(
        weight * weight for weight in control_weights
    )
    control_variance = _weighted_variance(control_values, control_weights)
    standard_error = math.sqrt(max(0.0, treated_se + control_variance / max(1.0, control_ess)))
    return _effect_result(
        spec=spec,
        estimate=estimate,
        standard_error=standard_error,
        n=len(treated) + len(controls),
        n_treated=len(treated),
        n_controls=len(controls),
        matched_treated=len(treated),
        effective_control_n=control_ess,
    )


def _estimate_mahalanobis(rows: list[dict[str, float]], spec: dict[str, Any]) -> dict[str, Any]:
    covariates = list(spec["covariates"])
    standardized = _standardized_rows(rows, covariates)
    treated = [(row, vector) for row, vector in standardized if row[spec["treatment"]] == 1.0]
    controls = [(row, vector) for row, vector in standardized if row[spec["treatment"]] == 0.0]
    _require_groups(treated, controls, spec)

    contributions: list[float] = []
    for treated_row, treated_vector in treated:
        control_row, _control_vector = min(
            controls,
            key=lambda item: _squared_distance(treated_vector, item[1]),
        )
        contributions.append(_outcome(treated_row, spec) - _outcome(control_row, spec))

    return _result_from_contributions(spec, contributions, n_controls=len(controls))


def _estimate_cem(rows: list[dict[str, float]], spec: dict[str, Any]) -> dict[str, Any]:
    control_bins: dict[tuple[object, ...], list[dict[str, float]]] = defaultdict(list)
    for row in rows:
        if row[spec["treatment"]] == 0.0:
            control_bins[_cem_key(row, list(spec["covariates"]))].append(row)

    contributions: list[float] = []
    for row in rows:
        if row[spec["treatment"]] != 1.0:
            continue
        controls = control_bins.get(_cem_key(row, list(spec["covariates"])), [])
        if not controls:
            continue
        control_mean = sum(_outcome(control, spec) for control in controls) / len(controls)
        contributions.append(_outcome(row, spec) - control_mean)

    return _result_from_contributions(
        spec,
        contributions,
        n_controls=sum(len(value) for value in control_bins.values()),
    )


def _rows_with_scores(
    rows: list[dict[str, float]],
    spec: dict[str, Any],
) -> list[tuple[dict[str, float], float]]:
    scores = estimate_propensity_scores(
        rows,
        covariates=list(spec["covariates"]),
        treatment=str(spec["treatment"]),
        model=str(spec.get("propensity_model", "none")),
    )
    return list(zip(rows, scores, strict=True))


def estimate_propensity_scores(
    rows: list[dict[str, float]],
    covariates: list[str],
    treatment: str,
    model: str,
) -> list[float]:
    if model == "none":
        raise ValueError("propensity scores require a declared propensity model")

    cache_key = (tuple(id(row) for row in rows), tuple(covariates), treatment, model)
    if cache_key in _PROPENSITY_SCORE_CACHE:
        return _PROPENSITY_SCORE_CACHE[cache_key]

    design = _standardized_design(rows, covariates)
    y = [row[treatment] for row in rows]
    if model == "logit_l2":
        beta = _fit_logit(design, y)
        scores = [_clip_score(_sigmoid(_dot(row, beta))) for row in design]
        _PROPENSITY_SCORE_CACHE[cache_key] = scores
        return scores
    if model == "probit_gradient":
        beta = _fit_probit(design, y)
        scores = [_clip_score(_normal_cdf(_dot(row, beta))) for row in design]
        _PROPENSITY_SCORE_CACHE[cache_key] = scores
        return scores
    raise ValueError(f"unknown propensity model: {model}")


def _fit_logit(design: list[list[float]], y: list[float]) -> list[float]:
    beta = [0.0] * len(design[0])
    learning_rate = 0.18
    l2 = 0.002
    for _ in range(360):
        gradient = [0.0] * len(beta)
        for row, actual in zip(design, y, strict=True):
            error = _sigmoid(_dot(row, beta)) - actual
            for index, value in enumerate(row):
                gradient[index] += error * value
        for index in range(len(beta)):
            penalty = l2 * beta[index] if index > 0 else 0.0
            beta[index] -= learning_rate * ((gradient[index] / len(design)) + penalty)
    return beta


def _fit_probit(design: list[list[float]], y: list[float]) -> list[float]:
    beta = [0.0] * len(design[0])
    learning_rate = 0.035
    l2 = 0.001
    for _ in range(420):
        gradient = [0.0] * len(beta)
        for row, actual in zip(design, y, strict=True):
            z = max(-7.0, min(7.0, _dot(row, beta)))
            p = _clip_score(_normal_cdf(z), 1e-5, 1.0 - 1e-5)
            density = max(1e-8, _normal_pdf(z))
            error = density * (p - actual) / max(1e-5, p * (1.0 - p))
            for index, value in enumerate(row):
                gradient[index] += error * value
        for index in range(len(beta)):
            penalty = l2 * beta[index] if index > 0 else 0.0
            beta[index] -= learning_rate * ((gradient[index] / len(design)) + penalty)
    return beta


def _apply_score_support(
    pairs: list[tuple[dict[str, float], float]],
    support_rule: str,
) -> list[tuple[dict[str, float], float]]:
    if support_rule in {"none", "caliper_0.05", "clip_0.02_0.98"}:
        return pairs
    if support_rule == "trim_0.05_0.95":
        return [(row, score) for row, score in pairs if 0.05 <= score <= 0.95]
    if support_rule == "common_support_pscore":
        treated = [score for row, score in pairs if row["treat"] == 1.0]
        controls = [score for row, score in pairs if row["treat"] == 0.0]
        if not treated or not controls:
            return []
        lower = max(min(treated), min(controls))
        upper = min(max(treated), max(controls))
        return [(row, score) for row, score in pairs if lower <= score <= upper]
    raise ValueError(f"unknown support rule: {support_rule}")


def _standardized_design(rows: list[dict[str, float]], covariates: list[str]) -> list[list[float]]:
    if not rows:
        raise ValueError("propensity model requires rows")
    means: list[float] = []
    scales: list[float] = []
    for covariate in covariates:
        values = [row[covariate] for row in rows]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / max(1, len(values) - 1)
        means.append(mean)
        scales.append(math.sqrt(variance) or 1.0)
    return [[1.0, *[(row[covariate] - mean) / scale for covariate, mean, scale in zip(covariates, means, scales, strict=True)]] for row in rows]


def _standardized_rows(
    rows: list[dict[str, float]],
    covariates: list[str],
) -> list[tuple[dict[str, float], list[float]]]:
    design = _standardized_design(rows, covariates)
    return [(row, vector[1:]) for row, vector in zip(rows, design, strict=True)]


def _cem_key(row: dict[str, float], covariates: list[str]) -> tuple[object, ...]:
    key: list[object] = []
    for covariate in covariates:
        value = row[covariate]
        if covariate == "age":
            key.append(("age", int(value // 8)))
        elif covariate == "educ":
            key.append(("educ", 0 if value < 10 else 1 if value <= 12 else 2))
        elif covariate in {"re74", "re75"}:
            if value <= 0:
                bucket = 0
            elif value < 5000:
                bucket = 1
            elif value < 10000:
                bucket = 2
            else:
                bucket = 3
            key.append((covariate, bucket))
        else:
            key.append((covariate, int(round(value))))
    return tuple(key)


def _result_from_contributions(
    spec: dict[str, Any],
    contributions: list[float],
    n_controls: int,
) -> dict[str, Any]:
    if len(contributions) < 2:
        raise ValueError(f"spec {spec['spec_id']} has too few matched treated rows")
    estimate = sum(contributions) / len(contributions)
    standard_error = math.sqrt(max(0.0, _variance(contributions) / len(contributions)))
    return _effect_result(
        spec=spec,
        estimate=estimate,
        standard_error=standard_error,
        n=len(contributions) + n_controls,
        n_treated=len(contributions),
        n_controls=n_controls,
        matched_treated=len(contributions),
    )


def _effect_result(
    spec: dict[str, Any],
    estimate: float,
    standard_error: float,
    n: int,
    n_treated: int,
    n_controls: int,
    matched_treated: int,
    effective_control_n: float | None = None,
) -> dict[str, Any]:
    ci_low = estimate - 1.96 * standard_error
    ci_high = estimate + 1.96 * standard_error
    return {
        "spec_id": spec["spec_id"],
        "estimate_att": estimate,
        "standard_error": standard_error,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "n": n,
        "n_treated": n_treated,
        "n_controls": n_controls,
        "matched_treated": matched_treated,
        "effective_control_n": effective_control_n,
        "outcome_transform": spec["outcome_transform"],
        "sample_filter": spec["sample_filter"],
        "estimator": spec["estimator"],
        "propensity_model": spec.get("propensity_model", "none"),
        "support_rule": spec.get("support_rule", "none"),
        "covariate_count": len(spec["covariates"]),
        "method_family": "matching_weighting",
        "sign": "positive" if estimate > 0 else "negative" if estimate < 0 else "zero",
    }


def _require_groups(
    treated: list[Any],
    controls: list[Any],
    spec: dict[str, Any],
) -> None:
    if len(treated) < 2 or len(controls) < 2:
        raise ValueError(f"spec {spec['spec_id']} requires treated and control rows")


def _outcome(row: dict[str, float], spec: dict[str, Any]) -> float:
    value = row[str(spec["outcome"])]
    transform = str(spec["outcome_transform"])
    if transform == "raw":
        return value
    if transform == "log1p":
        return math.log1p(max(0.0, value))
    raise ValueError(f"unknown outcome transform: {transform}")


def _variance(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def _weighted_variance(values: list[float], weights: list[float]) -> float:
    weight_total = sum(weights)
    if weight_total <= 0:
        return 0.0
    mean = sum(weight * value for value, weight in zip(values, weights, strict=True)) / weight_total
    return sum(weight * (value - mean) ** 2 for value, weight in zip(values, weights, strict=True)) / weight_total


def _dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


def _squared_distance(left: list[float], right: list[float]) -> float:
    return sum((a - b) ** 2 for a, b in zip(left, right, strict=True))


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def _normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def _normal_pdf(value: float) -> float:
    return math.exp(-0.5 * value * value) / math.sqrt(2.0 * math.pi)


def _clip_score(value: float, lower: float = MIN_SCORE, upper: float = MAX_SCORE) -> float:
    return max(lower, min(upper, value))
