from __future__ import annotations

from typing import Any, Callable

from .agent_runtime import run_agent_turn
from .autonomy import AutonomyPolicy, policy_from_level, validate_tool_requests
from .model_runtime import ModelRuntime, runtime_from_env
from .reporting import render_report
from .schemas import AgentOutput, RunManifest, RunResult, ToolCall, TraceEvent, new_run_id, utc_now
from .tools import (
    build_evidence_bundle,
    generate_code_data_plan,
    parse_paper,
    plan_experiment,
    resolve_arxiv,
    resolve_datasets,
    resolve_doi,
    resolve_github,
    score_reproducibility,
)


DEMO_PAPER = """# Demo Paper: Robust Claims Need Reproducible Evidence

This paper claims that a new research workflow improves reproducibility audits.
The method uses a staged agent protocol with a verifier and deterministic tools.
The data section says the demo fixture includes paper text, local evidence, and
tool-generated scorecards. The code section says reproduction scripts should run
inside a sandbox before any external publication.
"""


def run_research_audit(
    paper_text: str = DEMO_PAPER,
    *,
    runtime: ModelRuntime | None = None,
    autonomy_level: int | str = 2,
    allow_network: bool | None = None,
    event_callback: Callable[[TraceEvent], None] | None = None,
) -> RunResult:
    runtime = runtime or runtime_from_env()
    policy = policy_from_level(autonomy_level, allow_network_override=allow_network)
    health = runtime.health()
    run_id = new_run_id()
    manifest = RunManifest(
        run_id=run_id,
        status="running",
        model_id=health.model_id,
        model_base_url=health.base_url,
        autonomy_level=policy.manifest_label,
    )
    trace: list[TraceEvent] = []
    agents: list[AgentOutput] = []
    tools: list[ToolCall] = []
    artifacts: dict[str, Any] = {
        "autonomy_policy": {
            "level": policy.level,
            "label": policy.label,
            "allow_network": policy.allow_network,
            "allow_code_planning": policy.allow_code_planning,
            "allow_verifier_repair": policy.allow_verifier_repair,
        },
        "agent_model_artifacts": {},
    }

    def emit(event_type: str, actor: str, message: str, **payload: object) -> None:
        event = TraceEvent(run_id, event_type, actor, message, dict(payload))
        trace.append(event)
        if event_callback is not None:
            event_callback(event)

    def agent_turn(
        agent_id: str,
        context: dict[str, Any],
        default_tool_requests: list[dict[str, Any]],
        fallback_summary: str,
        next_state: str,
    ) -> AgentOutput:
        output, model_artifact = run_agent_turn(
            runtime,
            agent_id=agent_id,
            run_id=run_id,
            context=context,
            default_tool_requests=default_tool_requests,
            fallback_summary=fallback_summary,
            next_state=next_state,
        )
        artifacts["agent_model_artifacts"].setdefault(agent_id, []).append(model_artifact)
        emit(
            "agent_model_call",
            agent_id,
            "Agent produced a model-backed structured turn.",
            context_keys=model_artifact["context_keys"],
            rationale=model_artifact["rationale"],
            tool_requests=output.tool_requests,
        )
        return output

    def validate(agent_output: AgentOutput) -> list[str]:
        approved, blocked = validate_tool_requests(agent_output.agent_id, agent_output.tool_requests, policy)
        emit(
            "tool_request_validation",
            "orchestrator",
            f"Validated {len(agent_output.tool_requests)} tool request(s) from {agent_output.agent_id}.",
            approved=approved,
            blocked=blocked,
        )
        return [str(decision["tool_id"]) for decision in approved]

    def blocked_tool(tool_id: str, reason: str) -> ToolCall:
        return ToolCall(tool_id, "blocked", reason, {"evidence": [], "errors": [reason]})

    emit("run_started", "orchestrator", "Created run manifest.", manifest=manifest.to_dict())
    emit("model_health", "model_runtime", health.detail, ok=health.ok)

    planner = agent_turn(
        "planner",
        {"paper_text": paper_text, "autonomy_policy": artifacts["autonomy_policy"]},
        [],
        "Planned reader, retriever, auditor, experiment planner, code/data, verifier, report.",
        "paper_understanding",
    )
    planner.status = "ok"
    agents.append(planner)
    emit("agent_output", "planner", planner.summary, next_state=planner.next_recommended_state)

    reader = agent_turn(
        "paper_reader",
        {"paper_text": paper_text, "planner": planner.to_dict()},
        [{"tool_id": "parse_paper", "purpose": "extract paper claims and identifiers"}],
        "Requested paper parsing for structured claims, identifiers, and section hints.",
        "evidence_retrieval",
    )
    approved_reader_tools = validate(reader)
    paper_tool = (
        parse_paper(run_id, paper_text)
        if "parse_paper" in approved_reader_tools
        else blocked_tool("parse_paper", "parse_paper blocked by autonomy policy")
    )
    tools.append(paper_tool)
    artifacts["paper_understanding"] = paper_tool.output
    reader.status = "ok" if paper_tool.status == "ok" else "blocked"
    reader.summary = (
        f"Extracted {len(paper_tool.output.get('claims', []))} claims and section hints."
        if paper_tool.status == "ok"
        else paper_tool.summary
    )
    reader.claims = paper_tool.output.get("claims", [])
    reader.evidence_refs = [claim["source_ref"] for claim in reader.claims]
    agents.append(reader)
    emit("tool_call", "parse_paper", paper_tool.summary, output=paper_tool.output)
    emit("agent_output", "paper_reader", reader.summary, claims=reader.claims)

    resolver_calls = _run_evidence_retrieval(
        run_id=run_id,
        paper=paper_tool.output,
        policy=policy,
        agent_turn=agent_turn,
        validate=validate,
        emit=emit,
        tools=tools,
        agents=agents,
        blocked_tool=blocked_tool,
    )
    evidence_tool = build_evidence_bundle(run_id, resolver_calls)
    tools.append(evidence_tool)
    artifacts["evidence_bundle"] = evidence_tool.output
    emit("tool_call", "evidence_bundle", evidence_tool.summary, output=evidence_tool.output)

    audit_tool, auditor = _run_auditor(
        run_id,
        paper_tool.output,
        evidence_tool.output,
        agent_turn,
        validate,
        emit,
    )
    tools.append(audit_tool)
    artifacts["audit_scorecard"] = audit_tool.output
    agents.append(auditor)
    emit("tool_call", "score_reproducibility", audit_tool.summary, output=audit_tool.output)
    emit("agent_output", "reproducibility_auditor", auditor.summary)

    experiment_tool, experimenter = _run_experiment_planner(
        run_id,
        audit_tool.output,
        agent_turn,
        validate,
        emit,
    )
    tools.append(experiment_tool)
    artifacts["experiment_plan"] = experiment_tool.output
    agents.append(experimenter)
    emit("tool_call", "experiment_planner", experiment_tool.summary, output=experiment_tool.output)
    emit("agent_output", "experiment_planner", experimenter.summary)

    code_tool, code_agent = _run_code_data_agent(
        run_id,
        paper_tool.output,
        policy,
        agent_turn,
        validate,
        emit,
        blocked_tool,
    )
    tools.append(code_tool)
    artifacts["code_data_plan"] = code_tool.output
    agents.append(code_agent)
    emit("tool_call", "code_data_planner", code_tool.summary, output=code_tool.output)
    emit("agent_output", "code_data_agent", code_agent.summary)

    if audit_tool.output.get("gaps") and policy.allow_verifier_repair:
        repair_output = agent_turn(
            "verifier_critic",
            {
                "audit_scorecard": audit_tool.output,
                "evidence_bundle": evidence_tool.output,
                "repair_cycle": 1,
            },
            [{"tool_id": "repair_evidence_retrieval", "purpose": "send unresolved gaps back"}],
            "Verifier requested one evidence-retrieval repair pass.",
            "evidence_retrieval",
        )
        approved_repair = validate(repair_output)
        if "repair_evidence_retrieval" in approved_repair:
            emit(
                "verifier_repair_requested",
                "verifier_critic",
                "Verifier sent unresolved gaps back to the evidence retriever.",
                gaps=audit_tool.output.get("gaps", []),
            )
            repair_calls = _run_repair_retrieval(
                run_id=run_id,
                paper=paper_tool.output,
                gaps=audit_tool.output.get("gaps", []),
                policy=policy,
                agent_turn=agent_turn,
                validate=validate,
                emit=emit,
                tools=tools,
                blocked_tool=blocked_tool,
            )
            if repair_calls:
                resolver_calls.extend(repair_calls)
                evidence_tool = build_evidence_bundle(run_id, resolver_calls)
                tools.append(evidence_tool)
                artifacts["evidence_bundle"] = evidence_tool.output
                emit("tool_call", "evidence_bundle", evidence_tool.summary, output=evidence_tool.output)
                audit_tool, auditor = _run_auditor(
                    run_id,
                    paper_tool.output,
                    evidence_tool.output,
                    agent_turn,
                    validate,
                    emit,
                    repair_cycle=1,
                )
                tools.append(audit_tool)
                artifacts["audit_scorecard"] = audit_tool.output
                agents.append(auditor)
                emit("tool_call", "score_reproducibility", audit_tool.summary, output=audit_tool.output)
                emit("agent_output", "reproducibility_auditor", auditor.summary)

    blocked = audit_tool.output["decision"] != "pass"
    verifier = agent_turn(
        "verifier_critic",
        {
            "audit_scorecard": audit_tool.output,
            "evidence_bundle": evidence_tool.output,
            "code_data_plan": code_tool.output,
        },
        [],
        (
            "Verifier decision: degraded. Final report must disclose unresolved evidence gaps."
            if blocked
            else "Verifier decision: pass. Claims are supported by current artifacts."
        ),
        "reporting",
    )
    verifier.status = "ok"
    verifier.summary = (
        "Verifier decision: degraded. Final report must disclose unresolved evidence gaps."
        if blocked
        else "Verifier decision: pass. Claims are supported by current artifacts."
    )
    verifier.uncertainties = audit_tool.output["gaps"] if blocked else []
    agents.append(verifier)
    emit("agent_output", "verifier_critic", verifier.summary, blocked=blocked)

    reporter = agent_turn(
        "report_agent",
        {
            "manifest": manifest.to_dict(),
            "audit_scorecard": audit_tool.output,
            "verifier": verifier.to_dict(),
        },
        [{"tool_id": "render_markdown_report", "purpose": "render verified report"}],
        "Requested final report rendering from verified artifacts.",
        "complete",
    )
    validate(reporter)
    reporter.status = "ok"
    reporter.summary = "Rendered final audit report from verified artifacts."
    agents.append(reporter)
    emit("agent_output", "report_agent", reporter.summary)

    manifest.status = "complete"
    manifest.completed_at = utc_now()
    render_tool = ToolCall(
        "render_markdown_report",
        "ok",
        "Rendered final markdown report.",
        {"format": "markdown", "length": 0},
    )
    tools.append(render_tool)
    emit("tool_call", "render_markdown_report", render_tool.summary, output=render_tool.output)
    emit("run_complete", "orchestrator", "Run completed with visible trace and report.")
    report = render_report(manifest, agents, tools, trace)
    render_tool.output["length"] = len(report)

    return RunResult(manifest, trace, agents, tools, artifacts, report)


def _run_evidence_retrieval(
    *,
    run_id: str,
    paper: dict[str, Any],
    policy: AutonomyPolicy,
    agent_turn: Callable[..., AgentOutput],
    validate: Callable[[AgentOutput], list[str]],
    emit: Callable[..., None],
    tools: list[ToolCall],
    agents: list[AgentOutput],
    blocked_tool: Callable[[str, str], ToolCall],
) -> list[ToolCall]:
    retriever = agent_turn(
        "evidence_retriever",
        {"paper_understanding": paper},
        [
            {"tool_id": "arxiv_resolver", "purpose": "verify arXiv identity"},
            {"tool_id": "doi_resolver", "purpose": "verify DOI metadata"},
            {"tool_id": "github_resolver", "purpose": "resolve code repository"},
            {"tool_id": "dataset_resolver", "purpose": "resolve public datasets"},
        ],
        "Requested live source resolvers for paper identity, code, and datasets.",
        "audit_scoring",
    )
    approved = validate(retriever)
    resolver_map: dict[str, Callable[[], ToolCall]] = {
        "arxiv_resolver": lambda: resolve_arxiv(run_id, paper, allow_network=policy.allow_network),
        "doi_resolver": lambda: resolve_doi(run_id, paper, allow_network=policy.allow_network),
        "github_resolver": lambda: resolve_github(run_id, paper, allow_network=policy.allow_network),
        "dataset_resolver": lambda: resolve_datasets(run_id, paper, allow_network=policy.allow_network),
    }
    calls = []
    for tool_id, factory in resolver_map.items():
        call = (
            factory()
            if tool_id in approved
            else blocked_tool(tool_id, f"{tool_id} blocked by autonomy policy")
        )
        calls.append(call)
        tools.append(call)
        emit("tool_call", tool_id, call.summary, output=call.output)
    retriever.status = "ok"
    retriever.summary = "Evidence retriever requested and received resolver outputs."
    retriever.evidence_refs = [
        item["evidence_id"] for call in calls for item in call.output.get("evidence", [])
    ]
    retriever.uncertainties = [
        call.summary for call in calls if call.status in {"blocked", "failed", "missing", "skipped"}
    ]
    agents.append(retriever)
    emit("agent_output", "evidence_retriever", retriever.summary)
    return calls


def _run_repair_retrieval(
    *,
    run_id: str,
    paper: dict[str, Any],
    gaps: list[str],
    policy: AutonomyPolicy,
    agent_turn: Callable[..., AgentOutput],
    validate: Callable[[AgentOutput], list[str]],
    emit: Callable[..., None],
    tools: list[ToolCall],
    blocked_tool: Callable[[str, str], ToolCall],
) -> list[ToolCall]:
    requested = []
    gap_text = " ".join(gaps).lower()
    if "arxiv" in gap_text or "doi" in gap_text or "paper identity" in gap_text:
        requested.extend(
            [
                {"tool_id": "arxiv_resolver", "purpose": "repair paper identity"},
                {"tool_id": "doi_resolver", "purpose": "repair paper identity"},
            ]
        )
    if "github" in gap_text or "repository" in gap_text:
        requested.append({"tool_id": "github_resolver", "purpose": "repair repository evidence"})
    if "dataset" in gap_text or "license" in gap_text:
        requested.append({"tool_id": "dataset_resolver", "purpose": "repair dataset evidence"})
    if not requested:
        return []

    repair_retriever = agent_turn(
        "evidence_retriever",
        {"paper_understanding": paper, "verifier_gaps": gaps, "repair_cycle": 1},
        requested,
        "Ran a targeted evidence-retrieval repair pass requested by the verifier.",
        "audit_scoring",
    )
    approved = validate(repair_retriever)
    factories: dict[str, Callable[[], ToolCall]] = {
        "arxiv_resolver": lambda: resolve_arxiv(run_id, paper, allow_network=policy.allow_network),
        "doi_resolver": lambda: resolve_doi(run_id, paper, allow_network=policy.allow_network),
        "github_resolver": lambda: resolve_github(run_id, paper, allow_network=policy.allow_network),
        "dataset_resolver": lambda: resolve_datasets(run_id, paper, allow_network=policy.allow_network),
    }
    calls = []
    for request in requested:
        tool_id = request["tool_id"]
        call = (
            factories[tool_id]()
            if tool_id in approved
            else blocked_tool(tool_id, f"{tool_id} repair blocked by autonomy policy")
        )
        calls.append(call)
        tools.append(call)
        emit("tool_call", tool_id, call.summary, output=call.output, repair_cycle=1)
    emit("agent_output", "evidence_retriever", repair_retriever.summary, repair_cycle=1)
    return calls


def _run_auditor(
    run_id: str,
    paper: dict[str, Any],
    evidence: dict[str, Any],
    agent_turn: Callable[..., AgentOutput],
    validate: Callable[[AgentOutput], list[str]],
    emit: Callable[..., None],
    *,
    repair_cycle: int = 0,
) -> tuple[ToolCall, AgentOutput]:
    auditor = agent_turn(
        "reproducibility_auditor",
        {"paper_understanding": paper, "evidence_bundle": evidence, "repair_cycle": repair_cycle},
        [{"tool_id": "score_reproducibility", "purpose": "score evidence completeness"}],
        "Requested deterministic reproducibility scoring.",
        "experiment_or_robustness_planning",
    )
    approved = validate(auditor)
    audit_tool = (
        score_reproducibility(run_id, paper, evidence)
        if "score_reproducibility" in approved
        else ToolCall(
            "score_reproducibility",
            "blocked",
            "score_reproducibility blocked by autonomy policy",
            {"score": 0, "decision": "degraded", "gaps": ["score tool blocked"], "rubric": {}},
        )
    )
    auditor.status = "ok" if audit_tool.status == "ok" else "blocked"
    auditor.summary = f"Assigned reproducibility score {audit_tool.output['score']}/100."
    auditor.uncertainties = audit_tool.output["gaps"]
    return audit_tool, auditor


def _run_experiment_planner(
    run_id: str,
    audit: dict[str, Any],
    agent_turn: Callable[..., AgentOutput],
    validate: Callable[[AgentOutput], list[str]],
    emit: Callable[..., None],
) -> tuple[ToolCall, AgentOutput]:
    experimenter = agent_turn(
        "experiment_planner",
        {"audit_scorecard": audit},
        [{"tool_id": "experiment_planner", "purpose": "turn gaps into replication plan"}],
        "Requested a replication plan from audit gaps.",
        "code_data_planning",
    )
    approved = validate(experimenter)
    experiment_tool = (
        plan_experiment(run_id, audit)
        if "experiment_planner" in approved
        else ToolCall(
            "experiment_planner",
            "blocked",
            "experiment_planner blocked by autonomy policy",
            {"replication_plan": [], "blocked_items": audit.get("gaps", [])},
        )
    )
    experimenter.status = "ok" if experiment_tool.status == "ok" else "blocked"
    experimenter.summary = "Designed a replication plan from known gaps and evidence state."
    return experiment_tool, experimenter


def _run_code_data_agent(
    run_id: str,
    paper: dict[str, Any],
    policy: AutonomyPolicy,
    agent_turn: Callable[..., AgentOutput],
    validate: Callable[[AgentOutput], list[str]],
    emit: Callable[..., None],
    blocked_tool: Callable[[str, str], ToolCall],
) -> tuple[ToolCall, AgentOutput]:
    code_agent = agent_turn(
        "code_data_agent",
        {"paper_understanding": paper, "autonomy_policy": policy.manifest_label},
        [
            {"tool_id": "code_data_planner", "purpose": "generate sandboxed follow-up commands"},
            {"tool_id": "run_python_sandbox", "purpose": "execute generated reproduction code"},
        ],
        "Requested sandbox-gated code/data planning.",
        "verification",
    )
    approved = validate(code_agent)
    if "code_data_planner" in approved:
        code_tool = generate_code_data_plan(run_id, paper)
        code_agent.status = "ok"
        code_agent.summary = "Generated sandbox-only follow-up commands."
    else:
        code_tool = blocked_tool("code_data_planner", "code_data_planner blocked by autonomy policy")
        code_tool.output.update({"commands": [], "sandbox_required": True})
        code_agent.status = "blocked"
        code_agent.summary = "Code/data planning was blocked by the selected autonomy level."
    if "run_python_sandbox" not in approved:
        emit(
            "tool_request_blocked",
            "orchestrator",
            "run_python_sandbox was not executed; code execution remains gated.",
        )
    return code_tool, code_agent
