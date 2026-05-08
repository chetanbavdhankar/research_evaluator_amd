from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import product
from typing import Literal

OutcomeTransform = Literal["raw", "log1p"]
SampleFilter = Literal["none", "common_support_re75", "positive_prior_earnings", "age_18_45"]
Estimator = Literal["ols", "ridge_1e-6", "psm_1nn", "ipw_att", "mahalanobis_1nn", "cem_att"]
PropensityModel = Literal["none", "logit_l2", "probit_gradient"]
SupportRule = Literal[
    "none",
    "common_support_pscore",
    "caliper_0.05",
    "trim_0.05_0.95",
    "clip_0.02_0.98",
]


@dataclass(frozen=True)
class Spec:
    spec_id: str
    outcome: str
    treatment: str
    covariates: tuple[str, ...]
    outcome_transform: OutcomeTransform
    sample_filter: SampleFilter
    estimator: Estimator
    propensity_model: PropensityModel
    support_rule: SupportRule
    rationale: str

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["covariates"] = list(self.covariates)
        return data


def generate_spec_grid(max_specs: int | None = None) -> list[Spec]:
    covariate_sets = [
        ("age", "educ"),
        ("age", "educ", "black", "hispan"),
        ("age", "educ", "married", "nodegree"),
        ("age", "educ", "black", "hispan", "married", "nodegree"),
        ("age", "educ", "re74", "re75", "u74", "u75"),
        (
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
        ),
    ]
    transforms: list[OutcomeTransform] = ["raw", "log1p"]
    filters: list[SampleFilter] = [
        "none",
        "common_support_re75",
        "positive_prior_earnings",
        "age_18_45",
    ]
    estimator_configs: list[tuple[Estimator, PropensityModel, SupportRule]] = [
        ("ols", "none", "none"),
        ("ridge_1e-6", "none", "none"),
        ("psm_1nn", "logit_l2", "none"),
        ("psm_1nn", "logit_l2", "common_support_pscore"),
        ("psm_1nn", "logit_l2", "caliper_0.05"),
        ("psm_1nn", "probit_gradient", "none"),
        ("psm_1nn", "probit_gradient", "common_support_pscore"),
        ("psm_1nn", "probit_gradient", "caliper_0.05"),
        ("ipw_att", "logit_l2", "common_support_pscore"),
        ("ipw_att", "logit_l2", "trim_0.05_0.95"),
        ("ipw_att", "logit_l2", "clip_0.02_0.98"),
        ("ipw_att", "probit_gradient", "common_support_pscore"),
        ("ipw_att", "probit_gradient", "trim_0.05_0.95"),
        ("ipw_att", "probit_gradient", "clip_0.02_0.98"),
        ("mahalanobis_1nn", "none", "none"),
        ("cem_att", "none", "none"),
    ]

    specs: list[Spec] = []
    for index, (covariates, transform, sample_filter, estimator_config) in enumerate(
        product(covariate_sets, transforms, filters, estimator_configs),
        start=1,
    ):
        estimator, propensity_model, support_rule = estimator_config
        specs.append(
            Spec(
                spec_id=f"S{index:03d}",
                outcome="re78",
                treatment="treat",
                covariates=covariates,
                outcome_transform=transform,
                sample_filter=sample_filter,
                estimator=estimator,
                propensity_model=propensity_model,
                support_rule=support_rule,
                rationale=(
                    "Pre-declared LaLonde-style ATT specification over treatment, 1978 earnings, "
                    "baseline demographics, pre-treatment earnings, unemployment proxies, "
                    "matching, weighting, support, and outcome-scale choices."
                ),
            )
        )
    if max_specs is not None and len(specs) > max_specs:
        if max_specs <= 0:
            return []
        if max_specs == 1:
            return [specs[0]]
        step = (len(specs) - 1) / (max_specs - 1)
        return [specs[round(index * step)] for index in range(max_specs)]
    return specs


def invalid_spec_fixtures() -> list[dict[str, object]]:
    return [
        {
            "spec_id": "X001",
            "outcome": "re79",
            "treatment": "treat",
            "covariates": ["age", "educ"],
            "outcome_transform": "raw",
            "sample_filter": "none",
            "estimator": "ols",
            "propensity_model": "none",
            "support_rule": "none",
            "rationale": "Invalid claim mutation fixture.",
        },
        {
            "spec_id": "X002",
            "outcome": "re78",
            "treatment": "treat",
            "covariates": ["age", "educ", "re78"],
            "outcome_transform": "raw",
            "sample_filter": "none",
            "estimator": "ols",
            "propensity_model": "none",
            "support_rule": "none",
            "rationale": "Invalid outcome leakage fixture.",
        },
        {
            "spec_id": "X003",
            "outcome": "re78",
            "treatment": "treat",
            "covariates": ["age", "educ", "missing_column"],
            "outcome_transform": "raw",
            "sample_filter": "none",
            "estimator": "ols",
            "propensity_model": "none",
            "support_rule": "none",
            "rationale": "Invalid missing-column fixture.",
        },
        {
            "spec_id": "X004",
            "outcome": "re78",
            "treatment": "treat",
            "covariates": ["age", "educ"],
            "outcome_transform": "raw",
            "sample_filter": "drop_low_earners",
            "estimator": "ols",
            "propensity_model": "none",
            "support_rule": "none",
            "rationale": "Invalid undocumented exclusion fixture.",
        },
        {
            "spec_id": "X005",
            "outcome": "re78",
            "treatment": "treat",
            "covariates": ["age", "educ"],
            "outcome_transform": "raw",
            "sample_filter": "none",
            "estimator": "ipw_att",
            "propensity_model": "none",
            "support_rule": "none",
            "rationale": "Invalid weighting fixture without a propensity model.",
        },
    ]
