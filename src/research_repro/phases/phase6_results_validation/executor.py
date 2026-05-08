import json
from pathlib import Path
from research_repro.config import AppConfig
from research_repro.schemas.paper_knowledge import PaperKnowledgeArtifact
from research_repro.schemas.analysis_results import AnalysisResultsPackage
from research_repro.schemas.reproducibility_report import ReproducibilityReport, ResultComparison, DiscrepancyAttribution, ClaimAssessment
from research_repro.tools.llm_client import LLMClient
from research_repro.agents.validator import ValidatorAgent
from research_repro.logging_setup import get_phase_logger
from research_repro.phases.phase1_paper_comprehension.executor import PhaseResult

def compare_metrics(reported_val: float, reproduced_val: float, target_type: str, tolerance: float) -> str:
    if target_type == "exact":
        return "match" if reported_val == reproduced_val else "significant_discrepancy"
    elif target_type == "numerical":
        if reported_val == 0:
            rel_diff = abs(reproduced_val)
        else:
            rel_diff = abs(reported_val - reproduced_val) / abs(reported_val)
            
        if rel_diff <= tolerance:
            return "match"
        elif rel_diff <= 0.01:
            return "close_match"
        elif rel_diff <= 0.1:
            return "moderate_discrepancy"
        else:
            return "significant_discrepancy"
    return "not_reproduced"

def run(pka_path: str, analysis_results_path: str, run_dir: Path, config: AppConfig) -> PhaseResult:
    logger = get_phase_logger(str(run_dir), 6, "executor")
    logger.info(f"Starting Phase 6 for {pka_path}")
    
    with open(pka_path, "r", encoding="utf-8") as f:
        pka = PaperKnowledgeArtifact.model_validate_json(f.read())
        
    with open(analysis_results_path, "r", encoding="utf-8") as f:
        analysis = AnalysisResultsPackage.model_validate_json(f.read())
        
    llm_client = LLMClient(config)
    validator = ValidatorAgent(llm_client)
    
    comparisons = []
    attributions = []
    
    # Flatten reproduced metrics
    reproduced_metrics = {}
    for execution in analysis.method_executions:
        metrics = execution.primary_outputs.get("metrics", [])
        for m in metrics:
            reproduced_metrics[m["name"]] = m["value"]
            
    # Deterministic Comparison
    for res in pka.results:
        rep_name = res.metric_name
        reported_val = res.reported_value
        
        reproduced_val = reproduced_metrics.get(rep_name)
        
        if reproduced_val is not None:
            diff = abs(reported_val - reproduced_val)
            rel = diff / abs(reported_val) if reported_val != 0 else diff
            
            cls_ = compare_metrics(reported_val, reproduced_val, "numerical", 1e-6) # Using numerical with tight tolerance
        else:
            cls_ = "not_reproduced"
            diff = None
            rel = None
            
        comp = ResultComparison(
            result_id=res.result_id,
            metric_name=rep_name,
            reported_value=reported_val,
            reproduced_value=reproduced_val,
            classification=cls_,
            absolute_difference=diff,
            relative_difference=rel
        )
        comparisons.append(comp)
        
        if cls_ not in ["match", "close_match", "not_reproduced"]:
            # Evaluate Discrepancy
            all_failures = []
            for execution in analysis.method_executions:
                all_failures.extend(execution.failures)
            logs = json.dumps([f.model_dump() for f in all_failures])
            explanation = validator.evaluate_discrepancy(str(reported_val), str(reproduced_val), logs)
            attributions.append(DiscrepancyAttribution(
                result_id=comp.result_id,
                candidate_causes=explanation.candidate_causes,
                most_likely_cause=explanation.most_likely_cause,
                classification=explanation.classification,
                notes=explanation.notes
            ))
                
    claim_assessments = []
    comp_summary = json.dumps([c.model_dump() for c in comparisons])
    
    for c in pka.conclusions:
        assessment = validator.assess_claim(c, comp_summary)
        claim_assessments.append(ClaimAssessment(
            claim_text=c,
            supporting_results=[],
            assessment=assessment.assessment,
            rationale=assessment.rationale
        ))
            
    # Narrative
    discrepancy_str = json.dumps([a.model_dump() for a in attributions])
    claims_str = json.dumps([c.model_dump() for c in claim_assessments])
    narrative = validator.generate_narrative(pka.model_dump_json(), comp_summary, discrepancy_str, claims_str)
    
    report_path = run_dir / "reproducibility_report.json"
    
    report = ReproducibilityReport(
        paper_artifact_path=pka_path,
        all_phase_outputs={
            "analysis": analysis_results_path
        },
        executive_summary=narrative.executive_summary,
        overall_score=narrative.overall_score,
        overall_score_justification=narrative.overall_score_justification,
        result_comparisons=comparisons,
        discrepancy_attributions=attributions,
        claim_assessments=claim_assessments,
        figure_comparisons=[],
        known_gaps=[],
        recommendations=narrative.recommendations,
        pdf_report_path="",
        json_report_path=str(report_path.resolve())
    )
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))
        
    return PhaseResult(
        status="complete",
        artifact_path=str(report_path.resolve()),
        flags_raised=[]
    )
