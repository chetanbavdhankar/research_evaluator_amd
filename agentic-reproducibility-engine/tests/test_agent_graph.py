from agentic_research_evaluator.graph import run_research_audit
from agentic_research_evaluator.model_runtime import MockModelRuntime


TEST_PAPER = """# Denoising Diffusion Probabilistic Models

arXiv: 2006.11239
DOI: 10.48550/arXiv.2006.11239
Code: https://github.com/hojonathanho/diffusion
Data: CIFAR-10, LSUN, CelebA-HQ

The paper evaluates a diffusion-based generative modeling approach against image generation
benchmarks and reports sample quality, likelihood estimates, and ablation results.
"""


def test_run_contains_required_agents_and_trace():
    result = run_research_audit(TEST_PAPER, runtime=MockModelRuntime(), allow_network=False)

    agent_ids = {agent.agent_id for agent in result.agents}

    assert result.manifest.status == "complete"
    assert {
        "planner",
        "paper_reader",
        "evidence_retriever",
        "reproducibility_auditor",
        "experiment_planner",
        "code_data_agent",
        "verifier_critic",
        "report_agent",
    }.issubset(agent_ids)
    assert len(result.trace) >= 10
    assert any(event.event_type == "tool_call" for event in result.trace)
    assert any(event.event_type == "agent_model_call" for event in result.trace)
    assert any(event.event_type == "tool_request_validation" for event in result.trace)
    assert {
        "planner",
        "paper_reader",
        "evidence_retriever",
        "reproducibility_auditor",
        "experiment_planner",
        "code_data_agent",
        "verifier_critic",
        "report_agent",
    }.issubset(result.artifacts["agent_model_artifacts"])


def test_report_discloses_live_resolver_gap_without_placeholders():
    result = run_research_audit(TEST_PAPER, runtime=MockModelRuntime(), allow_network=False)

    assert "Verifier decision" in result.report_markdown
    assert "paper identity not verified by arXiv or DOI" in result.report_markdown
    assert "SpecCurve" not in result.report_markdown
    assert "demo_fixture" not in str(result.to_dict())
    assert "prepared-search" not in str(result.to_dict())


def test_unused_diffusion_paper_extracts_live_resolver_targets():
    result = run_research_audit(TEST_PAPER, runtime=MockModelRuntime(), allow_network=False)
    identifiers = result.artifacts["paper_understanding"]["identifiers"]

    assert identifiers["arxiv_ids"] == ["2006.11239"]
    assert identifiers["dois"] == ["10.48550/arxiv.2006.11239"]
    assert identifiers["github_repos"] == ["hojonathanho/diffusion"]
    assert identifiers["dataset_mentions"] == ["CIFAR-10", "LSUN", "CelebA-HQ"]


def test_autonomy_level_blocks_and_allows_tool_classes():
    low = run_research_audit(TEST_PAPER, runtime=MockModelRuntime(), autonomy_level=1)
    high = run_research_audit(TEST_PAPER, runtime=MockModelRuntime(), autonomy_level=3, allow_network=False)

    low_status = low.artifacts["evidence_bundle"]["resolver_status"]
    assert low_status["arxiv_resolver"] == "blocked"
    assert next(tool for tool in low.tools if tool.tool_id == "code_data_planner").status == "blocked"

    high_code_tool = next(tool for tool in high.tools if tool.tool_id == "code_data_planner")
    assert high_code_tool.status == "ok"
    assert any(event.event_type == "verifier_repair_requested" for event in high.trace)
