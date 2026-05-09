from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4


RunStatus = Literal["running", "complete", "blocked", "failed"]
AgentStatus = Literal["ok", "needs_tool", "blocked", "failed"]


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def new_run_id() -> str:
    return f"run_{uuid4().hex[:12]}"


@dataclass
class TraceEvent:
    run_id: str
    event_type: str
    actor: str
    message: str
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ToolCall:
    tool_id: str
    status: str
    summary: str
    output: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentOutput:
    agent_id: str
    run_id: str
    status: AgentStatus
    summary: str
    claims: list[dict[str, Any]] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    tool_requests: list[dict[str, Any]] = field(default_factory=list)
    uncertainties: list[str] = field(default_factory=list)
    next_recommended_state: str = "complete"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunManifest:
    run_id: str
    status: RunStatus
    model_id: str
    model_base_url: str
    autonomy_level: str
    created_at: str = field(default_factory=utc_now)
    completed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunResult:
    manifest: RunManifest
    trace: list[TraceEvent]
    agents: list[AgentOutput]
    tools: list[ToolCall]
    artifacts: dict[str, Any]
    report_markdown: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest": self.manifest.to_dict(),
            "trace": [event.to_dict() for event in self.trace],
            "agents": [agent.to_dict() for agent in self.agents],
            "tools": [tool.to_dict() for tool in self.tools],
            "artifacts": self.artifacts,
            "report_markdown": self.report_markdown,
        }

