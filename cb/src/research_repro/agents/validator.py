from research_repro.agents.base import BaseAgent
from research_repro.tools.llm_client import LLMClient
from research_repro.agents.validator_models import ValidationNarrative, ClaimAssessmentOutput, DiscrepancyExplanation
from research_repro.phases.phase6_results_validation import prompts

class ValidatorAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client, "validator")
        
    def evaluate_discrepancy(self, reported: str, reproduced: str, logs: str) -> DiscrepancyExplanation:
        prompt = prompts.EVALUATE_DISCREPANCY_PROMPT.format(
            reported_result=reported,
            reproduced_result=reproduced,
            audit_logs=logs
        )
        result, _ = self.run_structured(prompt, DiscrepancyExplanation, "discrepancy")
        return result
        
    def assess_claim(self, claim: str, results_summary: str) -> ClaimAssessmentOutput:
        prompt = prompts.ASSESS_CLAIM_PROMPT.format(
            claim=claim,
            results_summary=results_summary
        )
        result, _ = self.run_structured(prompt, ClaimAssessmentOutput, "claim")
        return result
        
    def generate_narrative(self, pka: str, comparisons: str, discrepancies: str, claims: str) -> ValidationNarrative:
        prompt = prompts.GENERATE_NARRATIVE_PROMPT.format(
            pka=pka,
            comparisons=comparisons,
            discrepancies=discrepancies,
            claims=claims
        )
        result, _ = self.run_structured(prompt, ValidationNarrative, "narrative")
        return result
