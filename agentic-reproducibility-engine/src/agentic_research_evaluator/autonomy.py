from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AutonomyPolicy:
    level: int
    label: str
    allow_network: bool
    allow_code_planning: bool
    allow_verifier_repair: bool

    @property
    def manifest_label(self) -> str:
        return f"L{self.level}: {self.label}"


POLICIES = {
    0: AutonomyPolicy(
        level=0,
        label="local trace only",
        allow_network=False,
        allow_code_planning=False,
        allow_verifier_repair=False,
    ),
    1: AutonomyPolicy(
        level=1,
        label="agent analysis, no network",
        allow_network=False,
        allow_code_planning=False,
        allow_verifier_repair=False,
    ),
    2: AutonomyPolicy(
        level=2,
        label="live evidence, read-only tools",
        allow_network=True,
        allow_code_planning=False,
        allow_verifier_repair=False,
    ),
    3: AutonomyPolicy(
        level=3,
        label="autonomous audit with verifier repair",
        allow_network=True,
        allow_code_planning=True,
        allow_verifier_repair=True,
    ),
}


TOOL_REGISTRY: dict[str, dict[str, Any]] = {
    "parse_paper": {"side_effect": "read_local"},
    "arxiv_resolver": {"side_effect": "read_network"},
    "doi_resolver": {"side_effect": "read_network"},
    "github_resolver": {"side_effect": "read_network"},
    "dataset_resolver": {"side_effect": "read_network"},
    "evidence_bundle": {"side_effect": "write_local"},
    "score_reproducibility": {"side_effect": "write_local"},
    "experiment_planner": {"side_effect": "write_local"},
    "code_data_planner": {"side_effect": "code_plan"},
    "render_markdown_report": {"side_effect": "write_local"},
    "repair_evidence_retrieval": {"side_effect": "orchestration"},
    "run_python_sandbox": {"side_effect": "execute_code"},
}


def policy_from_level(
    autonomy_level: int | str | None,
    *,
    allow_network_override: bool | None = None,
) -> AutonomyPolicy:
    level = _coerce_level(autonomy_level)
    policy = POLICIES[level]
    if allow_network_override is None:
        return policy
    return AutonomyPolicy(
        level=policy.level,
        label=policy.label,
        allow_network=policy.allow_network and allow_network_override,
        allow_code_planning=policy.allow_code_planning,
        allow_verifier_repair=policy.allow_verifier_repair,
    )


def validate_tool_requests(
    agent_id: str,
    tool_requests: list[dict[str, Any]],
    policy: AutonomyPolicy,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    approved = []
    blocked = []
    for request in tool_requests:
        tool_id = str(request.get("tool_id", "")).strip()
        metadata = TOOL_REGISTRY.get(tool_id)
        if not metadata:
            blocked.append(_decision(agent_id, request, False, "unknown tool"))
            continue

        side_effect = metadata["side_effect"]
        allowed = (
            side_effect in {"read_local", "write_local"}
            or (side_effect == "read_network" and policy.allow_network)
            or (side_effect == "code_plan" and policy.allow_code_planning)
            or (side_effect == "orchestration" and policy.allow_verifier_repair)
        )
        reason = "approved by autonomy policy" if allowed else f"blocked {side_effect}"
        decision = _decision(agent_id, request, allowed, reason)
        if allowed:
            approved.append(decision)
        else:
            blocked.append(decision)
    return approved, blocked


def _decision(
    agent_id: str,
    request: dict[str, Any],
    approved: bool,
    reason: str,
) -> dict[str, Any]:
    return {
        "agent_id": agent_id,
        "tool_id": request.get("tool_id"),
        "approved": approved,
        "reason": reason,
        "request": request,
    }


def _coerce_level(value: int | str | None) -> int:
    if value is None:
        return 2
    if isinstance(value, int):
        return max(0, min(3, value))
    text = str(value).strip()
    if text.isdigit():
        return max(0, min(3, int(text)))
    if text.lower().startswith("l") and len(text) > 1 and text[1].isdigit():
        return max(0, min(3, int(text[1])))
    return 2

