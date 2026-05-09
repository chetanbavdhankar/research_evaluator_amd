from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .graph import run_research_audit
from .model_runtime import MockModelRuntime, ModelRuntime, runtime_from_env
from .schemas import AgentOutput, RunResult, ToolCall, TraceEvent


REQUIRED_AGENT_SEQUENCE = [
    "planner",
    "paper_reader",
    "evidence_retriever",
    "reproducibility_auditor",
    "experiment_planner",
    "code_data_agent",
    "verifier_critic",
    "report_agent",
]

RESOLVER_TOOLS = [
    "arxiv_resolver",
    "doi_resolver",
    "github_resolver",
    "dataset_resolver",
]

REQUIRED_REPORT_SECTIONS = [
    "## Run",
    "## Paper Understanding",
    "## Reproducibility Score",
    "## Evidence Resolvers",
    "## Evidence Records",
    "## Gaps",
    "## Replication Plan",
    "## Code/Data Follow-Up",
    "## Verifier Decision",
    "## Trace Summary",
]

BANNED_PLACEHOLDERS = [
    "demo_fixture",
    "prepared-search",
    "placeholder evidence",
    "Agentic Engine demo report",
    "standalone-style library preview",
]


@dataclass
class CheckResult:
    category: str
    name: str
    passed: bool
    detail: str


@dataclass
class CaseAttempt:
    case_id: str
    attempt: int
    passed: bool
    checks: list[CheckResult] = field(default_factory=list)
    score: int | None = None
    decision: str | None = None
    run_id: str | None = None


@dataclass
class SuiteReport:
    suite: str
    cases: int
    attempts_per_case: int
    pass_at_k: float
    pass_caret_k: float
    passed: bool
    attempts: list[CaseAttempt]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["pass@k"] = payload.pop("pass_at_k")
        payload["pass^k"] = payload.pop("pass_caret_k")
        return payload


def default_cases_path() -> Path:
    return Path(__file__).resolve().parents[2] / "evals" / "agentic_audit_cases.json"


def load_cases(path: str | Path | None = None) -> list[dict[str, Any]]:
    cases_path = Path(path) if path else default_cases_path()
    with cases_path.open("r", encoding="utf-8") as handle:
        cases = json.load(handle)
    if not isinstance(cases, list):
        raise ValueError(f"Eval cases must be a JSON list: {cases_path}")
    return cases


def run_eval_suite(
    *,
    cases_path: str | Path | None = None,
    case_id: str | None = None,
    k: int = 1,
    runtime_mode: str = "mock",
) -> SuiteReport:
    if k < 1:
        raise ValueError("k must be >= 1")
    cases = load_cases(cases_path)
    if case_id:
        cases = [case for case in cases if case.get("id") == case_id]
        if not cases:
            raise ValueError(f"No eval case found for id: {case_id}")

    attempts: list[CaseAttempt] = []
    for case in cases:
        for attempt_number in range(1, k + 1):
            runtime = _runtime(runtime_mode)
            result = run_research_audit(
                case["paper_text"],
                runtime=runtime,
                autonomy_level=case.get("autonomy_level", 2),
                allow_network=case.get("allow_network"),
            )
            attempts.append(grade_case(case, result, attempt_number))

    grouped = _group_attempts(attempts)
    pass_at_k = sum(any(attempt.passed for attempt in group) for group in grouped.values()) / len(cases)
    pass_caret_k = sum(all(attempt.passed for attempt in group) for group in grouped.values()) / len(cases)
    return SuiteReport(
        suite="agentic-reproducibility",
        cases=len(cases),
        attempts_per_case=k,
        pass_at_k=pass_at_k,
        pass_caret_k=pass_caret_k,
        passed=pass_caret_k == 1.0,
        attempts=attempts,
    )


def grade_case(case: dict[str, Any], result: RunResult, attempt: int = 1) -> CaseAttempt:
    expected = case.get("expected", {})
    checks: list[CheckResult] = []

    def check(category: str, name: str, passed: bool, detail: str) -> None:
        checks.append(CheckResult(category, name, bool(passed), detail))

    agents_by_id = _agents_by_id(result.agents)
    tools_by_id = _tools_by_id(result.tools)
    trace_by_type = _trace_by_type(result.trace)
    artifacts = result.artifacts
    scorecard = artifacts.get("audit_scorecard", {})
    evidence_bundle = artifacts.get("evidence_bundle", {})
    paper = artifacts.get("paper_understanding", {})

    _grade_orchestration(check, result, agents_by_id, tools_by_id, trace_by_type)
    _grade_model_artifacts(check, artifacts)
    _grade_planner(check, agents_by_id, artifacts)
    _grade_reader(check, agents_by_id, tools_by_id, paper, expected)
    _grade_retriever(check, agents_by_id, tools_by_id, evidence_bundle, expected)
    _grade_auditor(check, agents_by_id, tools_by_id, scorecard, expected)
    _grade_experimenter(check, agents_by_id, tools_by_id, artifacts, scorecard)
    _grade_code_data(check, agents_by_id, tools_by_id, expected)
    _grade_verifier(check, agents_by_id, scorecard, result.trace, expected)
    _grade_report(check, result, expected)
    _grade_overall_success(check, result, expected)

    return CaseAttempt(
        case_id=str(case["id"]),
        attempt=attempt,
        passed=all(item.passed for item in checks),
        checks=checks,
        score=scorecard.get("score"),
        decision=scorecard.get("decision"),
        run_id=result.manifest.run_id,
    )


def render_text_report(report: SuiteReport) -> str:
    lines = [
        "EVAL REPORT: agentic-reproducibility",
        "=" * 43,
        f"Cases: {report.cases}",
        f"Attempts per case: {report.attempts_per_case}",
        f"pass@{report.attempts_per_case}: {report.pass_at_k:.2%}",
        f"pass^{report.attempts_per_case}: {report.pass_caret_k:.2%}",
        f"Status: {'PASS' if report.passed else 'FAIL'}",
        "",
    ]
    for attempt in report.attempts:
        status = "PASS" if attempt.passed else "FAIL"
        lines.append(
            f"[{status}] {attempt.case_id} attempt {attempt.attempt} "
            f"score={attempt.score} decision={attempt.decision} run={attempt.run_id}"
        )
        for check in attempt.checks:
            marker = "PASS" if check.passed else "FAIL"
            lines.append(f"  - {marker} {check.category}: {check.name} - {check.detail}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Agentic Reproducibility Engine evals.")
    parser.add_argument("--cases", default=None, help="Path to eval cases JSON.")
    parser.add_argument("--case", default=None, help="Run one eval case by id.")
    parser.add_argument("--k", type=int, default=1, help="Attempts per case for pass@k/pass^k.")
    parser.add_argument(
        "--runtime",
        choices=["mock", "env"],
        default="mock",
        help="Use deterministic mock runtime or runtime_from_env().",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    report = run_eval_suite(
        cases_path=args.cases,
        case_id=args.case,
        k=args.k,
        runtime_mode=args.runtime,
    )
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(render_text_report(report))
    return 0 if report.passed else 1


def _runtime(runtime_mode: str) -> ModelRuntime:
    if runtime_mode == "env":
        return runtime_from_env()
    return MockModelRuntime()


def _group_attempts(attempts: list[CaseAttempt]) -> dict[str, list[CaseAttempt]]:
    grouped: dict[str, list[CaseAttempt]] = {}
    for attempt in attempts:
        grouped.setdefault(attempt.case_id, []).append(attempt)
    return grouped


def _agents_by_id(agents: list[AgentOutput]) -> dict[str, list[AgentOutput]]:
    grouped: dict[str, list[AgentOutput]] = {}
    for agent in agents:
        grouped.setdefault(agent.agent_id, []).append(agent)
    return grouped


def _tools_by_id(tools: list[ToolCall]) -> dict[str, list[ToolCall]]:
    grouped: dict[str, list[ToolCall]] = {}
    for tool in tools:
        grouped.setdefault(tool.tool_id, []).append(tool)
    return grouped


def _trace_by_type(trace: list[TraceEvent]) -> dict[str, list[TraceEvent]]:
    grouped: dict[str, list[TraceEvent]] = {}
    for event in trace:
        grouped.setdefault(event.event_type, []).append(event)
    return grouped


def _last(mapping: dict[str, list[Any]], key: str) -> Any | None:
    values = mapping.get(key, [])
    return values[-1] if values else None


def _grade_orchestration(
    check: Any,
    result: RunResult,
    agents_by_id: dict[str, list[AgentOutput]],
    tools_by_id: dict[str, list[ToolCall]],
    trace_by_type: dict[str, list[TraceEvent]],
) -> None:
    check("overall", "manifest completes", result.manifest.status == "complete", result.manifest.status)
    check("overall", "required agents present", all(agent in agents_by_id for agent in REQUIRED_AGENT_SEQUENCE), ",".join(agents_by_id))
    check("overall", "required tools present", all(tool in tools_by_id for tool in ["parse_paper", "evidence_bundle", "score_reproducibility", "experiment_planner", "code_data_planner", "render_markdown_report"]), ",".join(tools_by_id))
    check("trace", "model calls emitted", len(trace_by_type.get("agent_model_call", [])) >= len(REQUIRED_AGENT_SEQUENCE), str(len(trace_by_type.get("agent_model_call", []))))
    check("trace", "tool calls emitted", len(trace_by_type.get("tool_call", [])) >= 6, str(len(trace_by_type.get("tool_call", []))))
    check("trace", "tool requests validated", len(trace_by_type.get("tool_request_validation", [])) >= 5, str(len(trace_by_type.get("tool_request_validation", []))))
    check("trace", "run completion event emitted", bool(trace_by_type.get("run_complete")), "run_complete present")


def _grade_model_artifacts(check: Any, artifacts: dict[str, Any]) -> None:
    model_artifacts = artifacts.get("agent_model_artifacts", {})
    for agent_id in REQUIRED_AGENT_SEQUENCE:
        entries = model_artifacts.get(agent_id, [])
        check(f"agent:{agent_id}", "model artifact captured", bool(entries), f"{len(entries)} artifact(s)")
        if not entries:
            continue
        artifact = entries[-1]
        check(f"agent:{agent_id}", "prompt recorded", bool(artifact.get("prompt")), "prompt is versioned in artifact")
        check(f"agent:{agent_id}", "context recorded", bool(artifact.get("context_keys")), ",".join(artifact.get("context_keys", [])))
        check(f"agent:{agent_id}", "tool request list recorded", isinstance(artifact.get("tool_requests"), list), "tool_requests is a list")


def _grade_planner(
    check: Any,
    agents_by_id: dict[str, list[AgentOutput]],
    artifacts: dict[str, Any],
) -> None:
    planner = _last(agents_by_id, "planner")
    policy = artifacts.get("autonomy_policy", {})
    check("agent:planner", "status ok", bool(planner and planner.status == "ok"), planner.status if planner else "missing")
    check("agent:planner", "routes to paper understanding", bool(planner and planner.next_recommended_state == "paper_understanding"), planner.next_recommended_state if planner else "missing")
    check("agent:planner", "autonomy policy in context", "level" in policy and "allow_network" in policy, str(policy))


def _grade_reader(
    check: Any,
    agents_by_id: dict[str, list[AgentOutput]],
    tools_by_id: dict[str, list[ToolCall]],
    paper: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    reader = _last(agents_by_id, "paper_reader")
    parse_tool = _last(tools_by_id, "parse_paper")
    claims = paper.get("claims", [])
    identifiers = paper.get("identifiers", {})
    min_claims = int(expected.get("min_claims", 1))
    check("agent:paper_reader", "parse tool succeeded", bool(parse_tool and parse_tool.status == "ok"), parse_tool.status if parse_tool else "missing")
    check("agent:paper_reader", "claims extracted", len(claims) >= min_claims, f"{len(claims)} >= {min_claims}")
    check("agent:paper_reader", "evidence refs align with claims", bool(reader and len(reader.evidence_refs) == len(reader.claims)), f"{len(reader.evidence_refs) if reader else 0} refs")
    for key, expected_values in expected.get("identifiers", {}).items():
        actual = identifiers.get(key, [])
        check("agent:paper_reader", f"identifier {key}", actual == expected_values, f"actual={actual}")


def _grade_retriever(
    check: Any,
    agents_by_id: dict[str, list[AgentOutput]],
    tools_by_id: dict[str, list[ToolCall]],
    evidence_bundle: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    retriever = _last(agents_by_id, "evidence_retriever")
    check("agent:evidence_retriever", "agent present", retriever is not None, "present" if retriever else "missing")
    for tool_id in RESOLVER_TOOLS:
        check("agent:evidence_retriever", f"{tool_id} called", bool(tools_by_id.get(tool_id)), f"{len(tools_by_id.get(tool_id, []))} call(s)")
    resolver_status = evidence_bundle.get("resolver_status", {})
    for tool_id, expected_status in expected.get("resolver_status", {}).items():
        actual_status = resolver_status.get(tool_id)
        check("agent:evidence_retriever", f"{tool_id} status", actual_status == expected_status, f"actual={actual_status}")
    check("agent:evidence_retriever", "missing evidence is explicit", isinstance(evidence_bundle.get("missing", []), list), str(evidence_bundle.get("missing", [])))


def _grade_auditor(
    check: Any,
    agents_by_id: dict[str, list[AgentOutput]],
    tools_by_id: dict[str, list[ToolCall]],
    scorecard: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    auditor = _last(agents_by_id, "reproducibility_auditor")
    audit_tool = _last(tools_by_id, "score_reproducibility")
    score = scorecard.get("score")
    decision = scorecard.get("decision")
    gaps = scorecard.get("gaps", [])
    check("agent:reproducibility_auditor", "agent present", auditor is not None, "present" if auditor else "missing")
    check("agent:reproducibility_auditor", "score tool ok", bool(audit_tool and audit_tool.status == "ok"), audit_tool.status if audit_tool else "missing")
    check("agent:reproducibility_auditor", "score bounded", isinstance(score, int) and 0 <= score <= 100, f"score={score}")
    check("agent:reproducibility_auditor", "decision matches expectation", decision == expected.get("decision"), f"actual={decision}")
    for gap in expected.get("required_gaps", []):
        check("agent:reproducibility_auditor", f"required gap: {gap}", gap in gaps, f"gaps={gaps}")
    check("agent:reproducibility_auditor", "rubric emitted", isinstance(scorecard.get("rubric"), dict) and bool(scorecard.get("rubric")), str(scorecard.get("rubric")))


def _grade_experimenter(
    check: Any,
    agents_by_id: dict[str, list[AgentOutput]],
    tools_by_id: dict[str, list[ToolCall]],
    artifacts: dict[str, Any],
    scorecard: dict[str, Any],
) -> None:
    experimenter = _last(agents_by_id, "experiment_planner")
    experiment_tool = _last(tools_by_id, "experiment_planner")
    plan = artifacts.get("experiment_plan", {}).get("replication_plan", [])
    blocked_items = artifacts.get("experiment_plan", {}).get("blocked_items", [])
    check("agent:experiment_planner", "agent present", experimenter is not None, "present" if experimenter else "missing")
    check("agent:experiment_planner", "tool ok", bool(experiment_tool and experiment_tool.status == "ok"), experiment_tool.status if experiment_tool else "missing")
    check("agent:experiment_planner", "replication plan nonempty", len(plan) >= 4, f"{len(plan)} step(s)")
    check("agent:experiment_planner", "carries audit gaps", blocked_items == scorecard.get("gaps", []), f"blocked={blocked_items}")


def _grade_code_data(
    check: Any,
    agents_by_id: dict[str, list[AgentOutput]],
    tools_by_id: dict[str, list[ToolCall]],
    expected: dict[str, Any],
) -> None:
    code_agent = _last(agents_by_id, "code_data_agent")
    code_tool = _last(tools_by_id, "code_data_planner")
    expected_status = expected.get("code_data_status")
    output = code_tool.output if code_tool else {}
    check("agent:code_data_agent", "agent present", code_agent is not None, "present" if code_agent else "missing")
    check("agent:code_data_agent", "tool status matches", bool(code_tool and code_tool.status == expected_status), code_tool.status if code_tool else "missing")
    check("agent:code_data_agent", "sandbox required", output.get("sandbox_required") is True, str(output))
    if expected_status == "ok":
        check("agent:code_data_agent", "commands generated", bool(output.get("commands")), str(output.get("commands")))
    if expected_status == "blocked":
        check("agent:code_data_agent", "commands blocked", not output.get("commands"), str(output.get("commands")))


def _grade_verifier(
    check: Any,
    agents_by_id: dict[str, list[AgentOutput]],
    scorecard: dict[str, Any],
    trace: list[TraceEvent],
    expected: dict[str, Any],
) -> None:
    verifier = _last(agents_by_id, "verifier_critic")
    gaps = scorecard.get("gaps", [])
    check("agent:verifier_critic", "agent present", verifier is not None, "present" if verifier else "missing")
    check("agent:verifier_critic", "explicit decision", bool(verifier and "Verifier decision" in verifier.summary), verifier.summary if verifier else "missing")
    if scorecard.get("decision") != "pass":
        check("agent:verifier_critic", "keeps unresolved gaps", bool(verifier and verifier.uncertainties == gaps), f"uncertainties={verifier.uncertainties if verifier else []}")
    repair_seen = any(event.event_type == "verifier_repair_requested" for event in trace)
    check("agent:verifier_critic", "repair loop expectation", repair_seen is bool(expected.get("expect_repair")), f"repair_seen={repair_seen}")


def _grade_report(check: Any, result: RunResult, expected: dict[str, Any]) -> None:
    report = result.report_markdown
    for section in REQUIRED_REPORT_SECTIONS:
        check("agent:report_agent", f"section {section}", section in report, "present" if section in report else "missing")
    for gap in expected.get("required_gaps", []):
        check("agent:report_agent", f"reports gap: {gap}", gap in report, "gap disclosed")
    for banned in BANNED_PLACEHOLDERS:
        check("safety", f"no banned placeholder: {banned}", banned not in report and banned not in str(result.to_dict()), "not found")
    check("agent:report_agent", "trace counts included", "Trace events:" in report and "Agent outputs:" in report and "Tool calls:" in report, "trace summary present")


def _grade_overall_success(check: Any, result: RunResult, expected: dict[str, Any]) -> None:
    scorecard = result.artifacts.get("audit_scorecard", {})
    evidence_bundle = result.artifacts.get("evidence_bundle", {})
    decision = scorecard.get("decision")
    gaps = scorecard.get("gaps", [])
    evidence_count = len(evidence_bundle.get("evidence", []))
    check("overall", "expected decision", decision == expected.get("decision"), f"actual={decision}")
    if gaps or evidence_count == 0:
        check("overall", "fail-closed on unresolved evidence", decision != "pass", f"decision={decision}; evidence={evidence_count}; gaps={len(gaps)}")
    check("overall", "audit artifact completeness", all(key in result.artifacts for key in ["paper_understanding", "evidence_bundle", "audit_scorecard", "experiment_plan", "code_data_plan"]), ",".join(result.artifacts))


if __name__ == "__main__":
    raise SystemExit(main())
