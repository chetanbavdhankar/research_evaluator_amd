from __future__ import annotations

import json
import unittest

from speccurve_l0.agentic_planner import build_planning_prompt, plan_reproduction_workflow
from speccurve_l0.agentic_schema import ReproductionWorkflowPlan
from speccurve_l0.agentic_verifier import verify_reproduction_plan


PAPER_TEXT = """
Title: Training Program Effects on Earnings

We estimate whether the job training program increased real earnings in 1978 for treated
participants relative to comparable nonparticipants. The dataset combines treated program
records with comparison records and includes age, education, prior earnings, treatment, and
1978 earnings. The main estimate uses regression adjustment, but the result depends on
covariate choice, common support, and matching method.
"""


class FakePlanningClient:
    def __init__(self, payload: dict):
        self.payload = payload
        self.messages: list[dict[str, str]] = []
        self.schema: dict = {}

    def chat_json(self, messages: list[dict[str, str]], schema: dict, max_retries: int = 3) -> str:
        self.messages = messages
        self.schema = schema
        return json.dumps(self.payload)


def valid_plan_payload() -> dict:
    quote = "job training program increased real earnings in 1978"
    return {
        "paper_title": "Training Program Effects on Earnings",
        "target_claim": "The training program increased 1978 real earnings for treated participants.",
        "claim_quote": quote,
        "dataset_requirements": [
            "treated program records",
            "comparison records",
            "age, education, prior earnings, treatment, and 1978 earnings",
        ],
        "environment": ["Python 3.11", "tabular statistics stack", "sandboxed subprocess runner"],
        "workflow_steps": [
            {
                "step_id": "S1",
                "agent_role": "reader",
                "action_type": "read_paper",
                "goal": "Extract claims, data requirements, methods, and reported metrics.",
                "inputs": ["paper text"],
                "outputs": ["paper-understanding.json"],
                "verifier_checks": ["claim_quote_grounded", "required_fields_present"],
                "sandbox_required": False,
            },
            {
                "step_id": "S2",
                "agent_role": "data",
                "action_type": "acquire_data",
                "goal": "Acquire or flag the treated and comparison records.",
                "inputs": ["paper-understanding.json"],
                "outputs": ["dataset-card.json"],
                "verifier_checks": ["source_exists", "hashes_recorded"],
                "sandbox_required": True,
            },
            {
                "step_id": "S3",
                "agent_role": "environment",
                "action_type": "prepare_environment",
                "goal": "Create a reproducible environment for the analysis.",
                "inputs": ["paper-understanding.json"],
                "outputs": ["environment-lock.json"],
                "verifier_checks": ["dependencies_parse", "no_secret_values"],
                "sandbox_required": True,
            },
            {
                "step_id": "S4",
                "agent_role": "preprocessor",
                "action_type": "preprocess_data",
                "goal": "Normalize columns and construct the analysis table.",
                "inputs": ["dataset-card.json"],
                "outputs": ["processed-dataset.json"],
                "verifier_checks": ["schema_matches_plan", "row_count_recorded"],
                "sandbox_required": True,
            },
            {
                "step_id": "S5",
                "agent_role": "analyzer",
                "action_type": "run_analysis",
                "goal": "Run the primary regression-adjusted estimate.",
                "inputs": ["processed-dataset.json"],
                "outputs": ["primary-results.json"],
                "verifier_checks": ["metric_names_match", "results_parse"],
                "sandbox_required": True,
            },
            {
                "step_id": "S6",
                "agent_role": "robustness",
                "action_type": "run_robustness",
                "goal": "Run AMD-accelerated sensitivity checks over matching and covariate choices.",
                "inputs": ["processed-dataset.json", "primary-results.json"],
                "outputs": ["robustness-surface.json"],
                "verifier_checks": ["specs_valid", "mi300x_benchmark_attached"],
                "sandbox_required": True,
            },
            {
                "step_id": "S7",
                "agent_role": "verifier",
                "action_type": "verify_results",
                "goal": "Compare reported, reproduced, and robustness results.",
                "inputs": ["primary-results.json", "robustness-surface.json"],
                "outputs": ["verification-report.json"],
                "verifier_checks": ["no_overclaiming", "artifact_hashes_present"],
                "sandbox_required": False,
            },
            {
                "step_id": "S8",
                "agent_role": "reporter",
                "action_type": "write_report",
                "goal": "Write the evidence report from artifacts.",
                "inputs": ["verification-report.json"],
                "outputs": ["final-report.md"],
                "verifier_checks": ["public_copy_lint", "artifact_links_resolve"],
                "sandbox_required": False,
            },
        ],
        "robustness_dimensions": [
            {
                "name": "covariate set",
                "rationale": "The paper says the result depends on covariate choice.",
                "values": ["base", "demographics", "prior earnings"],
                "source_quote": "depends on covariate choice",
            },
            {
                "name": "matching method",
                "rationale": "The paper identifies matching method as a sensitivity axis.",
                "values": ["nearest neighbor", "IPW", "coarsened exact matching"],
                "source_quote": "matching method",
            },
        ],
        "expected_artifacts": [
            "workflow-plan.json",
            "dataset-card.json",
            "result-table.json",
            "robustness-surface.json",
            "final-report.md",
        ],
        "stop_conditions": [
            "missing data source or inaccessible code",
            "unsafe generated code",
            "unverifiable claim quote",
            "missing result metric",
        ],
        "human_intervention_flags": ["data unavailable", "license unclear"],
    }


class AgenticWorkflowTest(unittest.TestCase):
    def test_fake_llm_plan_passes_verification(self) -> None:
        client = FakePlanningClient(valid_plan_payload())
        plan = plan_reproduction_workflow(PAPER_TEXT, client)
        report = verify_reproduction_plan(plan, PAPER_TEXT)
        self.assertTrue(report.passed, report.to_dict())
        self.assertGreaterEqual(report.score, 0.82)
        self.assertIn("run_robustness", {step.action_type for step in plan.workflow_steps})
        self.assertIn("workflow_steps", client.schema.get("properties", {}))

    def test_missing_sandbox_for_execution_fails(self) -> None:
        payload = valid_plan_payload()
        payload["workflow_steps"][1]["sandbox_required"] = False
        plan = ReproductionWorkflowPlan.from_dict(payload)
        report = verify_reproduction_plan(plan, PAPER_TEXT)
        self.assertFalse(report.passed)
        self.assertTrue(any("sandboxing" in failure for failure in report.failures))

    def test_schema_rejects_unexpected_keys(self) -> None:
        payload = valid_plan_payload()
        payload["confidence_vibes"] = "high"
        with self.assertRaises(ValueError):
            ReproductionWorkflowPlan.from_dict(payload)

    def test_planning_prompt_prioritizes_verifiability(self) -> None:
        prompt = build_planning_prompt(PAPER_TEXT)
        self.assertIn("resettable", prompt)
        self.assertIn("rewardable", prompt)
        self.assertIn("AMD MI300X", prompt)
        self.assertIn("Return the workflow plan as JSON", prompt)


if __name__ == "__main__":
    unittest.main()
