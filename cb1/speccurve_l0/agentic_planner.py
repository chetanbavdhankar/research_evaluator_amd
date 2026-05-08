from __future__ import annotations

from typing import Protocol

from .agentic_schema import ReproductionWorkflowPlan, WORKFLOW_PLAN_SCHEMA


class JsonPlanningClient(Protocol):
    def chat_json(
        self,
        messages: list[dict[str, str]],
        schema: dict,
        max_retries: int = 3,
    ) -> str:
        ...


MISSION_PROMPT = """You are SpecCurve Agent, a Software 3.0 research reproduction planner.

Use the LLM for what it is good at: reading an unfamiliar paper and proposing a workflow.
Do not pretend that prose is evidence. Every claim, dataset requirement, and robustness
dimension must be grounded in quoted paper text when possible. Your output is consumed by
deterministic verifiers and sandbox executors.

Design goal:
- Construct a reproduction workflow for this empirical paper.
- Prefer resettable, efficient, rewardable steps.
- Plan code execution only inside a sandbox.
- Make AMD MI300X useful for batch robustness, bootstrap, permutation, or sensitivity work.
- If data/code is missing, record a human intervention flag instead of inventing access.
"""


def build_planning_prompt(paper_text: str) -> str:
    excerpt = paper_text[:24000]
    return f"""{MISSION_PROMPT}

Paper text:
<<<PAPER_TEXT
{excerpt}
PAPER_TEXT>>>

Return the workflow plan as JSON. Required behavior:
- Choose one target claim that could be reproduced or stress-tested.
- Include a direct quote for claim_quote.
- Include 6 to 10 workflow_steps.
- Include at least one run_robustness step.
- Include at least two robustness_dimensions unless the paper is clearly non-empirical.
- Include explicit verifier_checks for every executable step.
- Include stop_conditions for missing data, missing code, unsafe code, and unverifiable claims.
"""


def plan_reproduction_workflow(
    paper_text: str,
    client: JsonPlanningClient,
    max_retries: int = 3,
) -> ReproductionWorkflowPlan:
    messages = [{"role": "user", "content": build_planning_prompt(paper_text)}]
    content = client.chat_json(messages, WORKFLOW_PLAN_SCHEMA, max_retries=max_retries)
    return ReproductionWorkflowPlan.from_json(content)
