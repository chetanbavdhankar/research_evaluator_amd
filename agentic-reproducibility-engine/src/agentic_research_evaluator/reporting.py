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

    paper = paper_tool.output
    audit = audit_tool.output
    evidence = evidence_tool.output
    experiment = experiment_tool.output
    code = code_tool.output

    paper_title = str(paper.get("title") or "Untitled paper")
    claims = paper.get("claims", [])
    document_hash = str(paper.get("document_hash") or "unavailable")
    score = audit.get("score", "unavailable")
    decision = audit.get("decision", audit_tool.status)

    gaps = audit.get("gaps", [])
    gap_lines = "\n".join(f"- {gap}" for gap in gaps) if gaps else "- No blocking gaps found."
    plan_lines = "\n".join(
        f"- {step}" for step in experiment.get("replication_plan", [])
    )
    if not plan_lines:
        plan_lines = "- No replication steps generated."
    command_lines = "\n".join(f"- `{command}`" for command in code.get("commands", []))
    if not command_lines:
        command_lines = "- No follow-up commands generated."
    resolver_lines = "\n".join(
        f"- `{name}`: `{status}`"
        for name, status in evidence.get("resolver_status", {}).items()
    )
    if not resolver_lines:
        resolver_lines = "- No resolver status available."
    evidence_lines = "\n".join(
        f"- `{item.get('source_type')}` {item.get('confidence')}: {item.get('locator')}"
        for item in evidence.get("evidence", [])[:10]
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

- Title: {paper_title}
- Claims extracted: {len(claims) if isinstance(claims, list) else 0}
- Document hash: `{document_hash}`

## Reproducibility Score

- Score: `{score}/100`
- Decision: `{decision}`

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

Sandbox required: `{code.get("sandbox_required", "unknown")}`

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
    return next(
        (tool for tool in reversed(tools) if tool.tool_id == tool_id),
        ToolCall(tool_id, "missing", f"{tool_id} did not run.", {}),
    )


def _last_agent(agents: list[AgentOutput], agent_id: str) -> AgentOutput:
    return next(
        (agent for agent in reversed(agents) if agent.agent_id == agent_id),
        AgentOutput(
            agent_id=agent_id,
            run_id=agents[-1].run_id if agents else "unknown",
            status="failed",
            summary=f"{agent_id} did not complete.",
        ),
    )
