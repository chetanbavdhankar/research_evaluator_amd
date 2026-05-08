from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal


ActionType = Literal[
    "read_paper",
    "acquire_data",
    "prepare_environment",
    "preprocess_data",
    "run_analysis",
    "run_robustness",
    "verify_results",
    "write_report",
]


WORKFLOW_PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "paper_title",
        "target_claim",
        "claim_quote",
        "dataset_requirements",
        "environment",
        "workflow_steps",
        "robustness_dimensions",
        "expected_artifacts",
        "stop_conditions",
        "human_intervention_flags",
    ],
    "additionalProperties": False,
    "properties": {
        "paper_title": {"type": "string"},
        "target_claim": {"type": "string"},
        "claim_quote": {"type": "string"},
        "dataset_requirements": {"type": "array", "items": {"type": "string"}},
        "environment": {"type": "array", "items": {"type": "string"}},
        "workflow_steps": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "step_id",
                    "agent_role",
                    "action_type",
                    "goal",
                    "inputs",
                    "outputs",
                    "verifier_checks",
                    "sandbox_required",
                ],
                "additionalProperties": False,
                "properties": {
                    "step_id": {"type": "string"},
                    "agent_role": {"type": "string"},
                    "action_type": {
                        "type": "string",
                        "enum": [
                            "read_paper",
                            "acquire_data",
                            "prepare_environment",
                            "preprocess_data",
                            "run_analysis",
                            "run_robustness",
                            "verify_results",
                            "write_report",
                        ],
                    },
                    "goal": {"type": "string"},
                    "inputs": {"type": "array", "items": {"type": "string"}},
                    "outputs": {"type": "array", "items": {"type": "string"}},
                    "verifier_checks": {"type": "array", "items": {"type": "string"}},
                    "sandbox_required": {"type": "boolean"},
                },
            },
        },
        "robustness_dimensions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "rationale", "values", "source_quote"],
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "rationale": {"type": "string"},
                    "values": {"type": "array", "items": {"type": "string"}},
                    "source_quote": {"type": "string"},
                },
            },
        },
        "expected_artifacts": {"type": "array", "items": {"type": "string"}},
        "stop_conditions": {"type": "array", "items": {"type": "string"}},
        "human_intervention_flags": {"type": "array", "items": {"type": "string"}},
    },
}


@dataclass(frozen=True)
class WorkflowStep:
    step_id: str
    agent_role: str
    action_type: ActionType
    goal: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    verifier_checks: tuple[str, ...]
    sandbox_required: bool

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "WorkflowStep":
        action_type = _required_str(value, "action_type")
        valid_actions = set(WORKFLOW_PLAN_SCHEMA["properties"]["workflow_steps"]["items"]["properties"]["action_type"]["enum"])
        if action_type not in valid_actions:
            raise ValueError(f"unknown action_type: {action_type}")
        return cls(
            step_id=_required_str(value, "step_id"),
            agent_role=_required_str(value, "agent_role"),
            action_type=action_type,  # type: ignore[arg-type]
            goal=_required_str(value, "goal"),
            inputs=tuple(_required_str_list(value, "inputs")),
            outputs=tuple(_required_str_list(value, "outputs")),
            verifier_checks=tuple(_required_str_list(value, "verifier_checks")),
            sandbox_required=_required_bool(value, "sandbox_required"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "agent_role": self.agent_role,
            "action_type": self.action_type,
            "goal": self.goal,
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
            "verifier_checks": list(self.verifier_checks),
            "sandbox_required": self.sandbox_required,
        }


@dataclass(frozen=True)
class RobustnessDimension:
    name: str
    rationale: str
    values: tuple[str, ...]
    source_quote: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "RobustnessDimension":
        return cls(
            name=_required_str(value, "name"),
            rationale=_required_str(value, "rationale"),
            values=tuple(_required_str_list(value, "values")),
            source_quote=_required_str(value, "source_quote"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "rationale": self.rationale,
            "values": list(self.values),
            "source_quote": self.source_quote,
        }


@dataclass(frozen=True)
class ReproductionWorkflowPlan:
    paper_title: str
    target_claim: str
    claim_quote: str
    dataset_requirements: tuple[str, ...]
    environment: tuple[str, ...]
    workflow_steps: tuple[WorkflowStep, ...]
    robustness_dimensions: tuple[RobustnessDimension, ...]
    expected_artifacts: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    human_intervention_flags: tuple[str, ...]

    @classmethod
    def from_json(cls, content: str) -> "ReproductionWorkflowPlan":
        try:
            value = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"workflow plan is not valid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError("workflow plan must be a JSON object")
        return cls.from_dict(value)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ReproductionWorkflowPlan":
        allowed = set(WORKFLOW_PLAN_SCHEMA["properties"])
        unexpected = sorted(set(value) - allowed)
        if unexpected:
            raise ValueError(f"unexpected workflow plan keys: {unexpected}")
        steps_value = _required_list(value, "workflow_steps")
        dimensions_value = _required_list(value, "robustness_dimensions")
        return cls(
            paper_title=_required_str(value, "paper_title"),
            target_claim=_required_str(value, "target_claim"),
            claim_quote=_required_str(value, "claim_quote"),
            dataset_requirements=tuple(_required_str_list(value, "dataset_requirements")),
            environment=tuple(_required_str_list(value, "environment")),
            workflow_steps=tuple(WorkflowStep.from_dict(_required_dict(item, "workflow_step")) for item in steps_value),
            robustness_dimensions=tuple(
                RobustnessDimension.from_dict(_required_dict(item, "robustness_dimension"))
                for item in dimensions_value
            ),
            expected_artifacts=tuple(_required_str_list(value, "expected_artifacts")),
            stop_conditions=tuple(_required_str_list(value, "stop_conditions")),
            human_intervention_flags=tuple(_required_str_list(value, "human_intervention_flags")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "paper_title": self.paper_title,
            "target_claim": self.target_claim,
            "claim_quote": self.claim_quote,
            "dataset_requirements": list(self.dataset_requirements),
            "environment": list(self.environment),
            "workflow_steps": [step.to_dict() for step in self.workflow_steps],
            "robustness_dimensions": [dimension.to_dict() for dimension in self.robustness_dimensions],
            "expected_artifacts": list(self.expected_artifacts),
            "stop_conditions": list(self.stop_conditions),
            "human_intervention_flags": list(self.human_intervention_flags),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class VerificationReport:
    passed: bool
    score: float
    checks: tuple[str, ...]
    failures: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "score": self.score,
            "checks": list(self.checks),
            "failures": list(self.failures),
            "warnings": list(self.warnings),
        }


def _required_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _required_list(value: dict[str, Any], key: str) -> list[Any]:
    item = value.get(key)
    if not isinstance(item, list):
        raise ValueError(f"{key} must be a list")
    return item


def _required_str_list(value: dict[str, Any], key: str) -> list[str]:
    items = _required_list(value, key)
    if not all(isinstance(item, str) and item.strip() for item in items):
        raise ValueError(f"{key} must be a list of non-empty strings")
    return [item.strip() for item in items]


def _required_str(value: dict[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return item.strip()


def _required_bool(value: dict[str, Any], key: str) -> bool:
    item = value.get(key)
    if not isinstance(item, bool):
        raise ValueError(f"{key} must be a boolean")
    return item
