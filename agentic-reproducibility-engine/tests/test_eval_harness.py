from agentic_research_evaluator.evals import load_cases, run_eval_suite


def test_eval_cases_are_versioned_and_loadable():
    cases = load_cases()

    assert len(cases) >= 3
    assert {case["id"] for case in cases} >= {
        "explicit_paper_offline_fail_closed",
        "underspecified_claims_no_placeholder_evidence",
        "autonomy_l1_blocks_external_and_code_tools",
    }


def test_agentic_reproducibility_eval_suite_passes_with_mock_runtime():
    report = run_eval_suite(k=1, runtime_mode="mock")

    assert report.passed
    assert report.pass_at_k == 1.0
    assert report.pass_caret_k == 1.0
