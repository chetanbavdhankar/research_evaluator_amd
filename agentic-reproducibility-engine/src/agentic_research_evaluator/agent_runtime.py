from __future__ import annotations

import json
import re
from typing import Any

from .model_runtime import ModelRuntime
from .schemas import AgentOutput


AGENT_PROMPTS = {
    "planner": (
        "You are the Planner Agent. Decompose the audit into bounded states and request "
        "only tools needed for the next state."
    ),
    "paper_reader": (
        "You are the Paper Reader Agent. Extract claims, methods, datasets, software, "
        "and identifiers from the supplied artifact."
    ),
    "evidence_retriever": (
        "You are the Evidence Retriever Agent. Request source resolvers and explain "
        "which evidence is still missing."
    ),
    "reproducibility_auditor": (
        "You are the Reproducibility Auditor Agent. Assess the paper and evidence "
        "against a reproducibility rubric."
    ),
    "experiment_planner": (
        "You are the Experiment Planner Agent. Convert audit gaps into a bounded "
        "replication or robustness plan."
    ),
    "code_data_agent": (
        "You are the Code/Data Agent. Request only sandbox-safe code/data planning "
        "tools and identify any execution that must remain gated."
    ),
    "verifier_critic": (
        "You are the Verifier/Critic Agent. Attack unsupported claims, invalid source "
        "bindings, missing citations, and overclaiming. You may request repair routing."
    ),
    "report_agent": (
        "You are the Report Agent. Request report rendering and summarize only verified "
        "artifacts. Do not invent citations."
    ),
}


def run_agent_turn(
    runtime: ModelRuntime,
    *,
    agent_id: str,
    run_id: str,
    context: dict[str, Any],
    default_tool_requests: list[dict[str, Any]],
    fallback_summary: str,
    next_state: str,
) -> tuple[AgentOutput, dict[str, Any]]:
    system = _system_prompt(agent_id)
    user = json.dumps(
        {
            "run_id": run_id,
            "context": context,
            "available_default_tool_requests": default_tool_requests,
        },
        indent=2,
        default=str,
    )
    raw = runtime.chat(system=system, user=user[:20000], temperature=0.0)
    parsed = _parse_json_object(raw)
    summary = str(parsed.get("summary") or fallback_summary)
    rationale = str(parsed.get("rationale") or parsed.get("audit_rationale") or raw).strip()
    tool_requests = _normalize_tool_requests(
        parsed.get("tool_requests"),
        default_tool_requests,
    )
    uncertainties = _normalize_string_list(parsed.get("uncertainties"))
    output = AgentOutput(
        agent_id=agent_id,
        run_id=run_id,
        status="needs_tool" if tool_requests else "ok",
        summary=summary,
        tool_requests=tool_requests,
        uncertainties=uncertainties,
        next_recommended_state=str(parsed.get("next_recommended_state") or next_state),
    )
    artifact = {
        "agent_id": agent_id,
        "prompt": AGENT_PROMPTS[agent_id],
        "context_keys": list(context.keys()),
        "model_output": raw,
        "structured_output": parsed,
        "rationale": rationale[:4000],
        "tool_requests": tool_requests,
    }
    return output, artifact


def _system_prompt(agent_id: str) -> str:
    return f"""{AGENT_PROMPTS[agent_id]}

Return JSON only with this schema:
{{
  "summary": "one sentence",
  "rationale": "short audit rationale, not private chain-of-thought",
  "tool_requests": [{{"tool_id": "string", "purpose": "string"}}],
  "uncertainties": ["string"],
  "next_recommended_state": "string"
}}

Do not include hidden chain-of-thought. Do not claim tools have run; request tools
and let the orchestrator validate and execute them.
"""


def _parse_json_object(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, flags=re.DOTALL)
    if fenced:
        try:
            parsed = json.loads(fenced.group(1))
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(raw[start : end + 1])
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _normalize_tool_requests(
    value: Any,
    default_tool_requests: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    requested: list[dict[str, Any]] = []
    if not isinstance(value, list):
        return _merge_tool_requests(default_tool_requests, requested)
    for item in value:
        if isinstance(item, dict) and item.get("tool_id"):
            requested.append(item)
        elif isinstance(item, str):
            requested.append({"tool_id": item, "purpose": "model-requested"})
    return _merge_tool_requests(default_tool_requests, requested)


def _merge_tool_requests(
    required: list[dict[str, Any]],
    requested: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in [*required, *requested]:
        tool_id = str(item.get("tool_id", "")).strip()
        if not tool_id or tool_id in seen:
            continue
        normalized = dict(item)
        normalized["tool_id"] = tool_id
        merged.append(normalized)
        seen.add(tool_id)
    return merged


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]

