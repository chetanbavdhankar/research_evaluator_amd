from __future__ import annotations

from .schemas import AgentOutput, RunManifest, ToolCall, TraceEvent


def render_report(
    manifest: RunManifest,
    agents: list[AgentOutput],
    tools: list[ToolCall],
    trace: list[TraceEvent],
) -> str:
    verifier = _last_agent(agents, "verifier_critic")
    audit_tool = _last_tool(tools, "score_reproducibility")
    paper_tool = _last_tool(tools, "parse_paper")
    evidence_tool = _last_tool(tools, "evidence_bundle")
    experiment_tool = _last_tool(tools, "experiment_planner")
    code_tool = _last_tool(tools, "code_data_planner")

    gaps = audit_tool.output.get("gaps", [])
    gap_lines = "\n".join(f"- {gap}" for gap in gaps) if gaps else "- No blocking gaps found."
    plan_lines = "\n".join(
        f"- {step}" for step in experiment_tool.output.get("replication_plan", [])
    )
    command_lines = "\n".join(f"- `{command}`" for command in code_tool.output.get("commands", []))
    resolver_lines = "\n".join(
        f"- `{name}`: `{status}`"
        for name, status in evidence_tool.output.get("resolver_status", {}).items()
    )
    evidence_lines = "\n".join(
        f"- `{item.get('source_type')}` {item.get('confidence')}: {item.get('locator')}"
        for item in evidence_tool.output.get("evidence", [])[:10]
    )
    if not evidence_lines:
        evidence_lines = "- No external evidence records were resolved."

    return f"""# Agentic Research Audit Report

## Run

- Run id: `{manifest.run_id}`
- Status: `{manifest.status}`
- Model: `{manifest.model_id}`
- Model endpoint: `{manifest.model_base_url}`

## Paper Understanding

- Title: {paper_tool.output["title"]}
- Claims extracted: {len(paper_tool.output.get("claims", []))}
- Document hash: `{paper_tool.output["document_hash"]}`

## Reproducibility Score

- Score: `{audit_tool.output["score"]}/100`
- Decision: `{audit_tool.output["decision"]}`

## Evidence Resolvers

{resolver_lines}

## Evidence Records

{evidence_lines}

## Gaps

{gap_lines}

## Replication Plan

{plan_lines}

## Code/Data Follow-Up

{command_lines}

Sandbox required: `{code_tool.output.get("sandbox_required")}`

## Verifier Decision

{verifier.summary}

## Trace Summary

- Trace events: {len(trace)}
- Agent outputs: {len(agents)}
- Tool calls: {len(tools)}

This report is generated from run artifacts. It must not be represented as a
live Qwen/AMD run unless the manifest model endpoint and AMD proof artifacts
show that deployment.
"""


def _last_tool(tools: list[ToolCall], tool_id: str) -> ToolCall:
    return next(tool for tool in reversed(tools) if tool.tool_id == tool_id)


def _last_agent(agents: list[AgentOutput], agent_id: str) -> AgentOutput:
    return next(agent for agent in reversed(agents) if agent.agent_id == agent_id)
