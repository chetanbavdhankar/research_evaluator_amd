from research_repro.agents.base import BaseAgent
from research_repro.tools.llm_client import LLMClient
from research_repro.schemas.paper_knowledge import PaperKnowledgeArtifact
from research_repro.schemas.environment_spec import EnvironmentSpec
from research_repro.schemas.processed_dataset import ProcessedDatasetArtifact
from research_repro.agents.analyzer_models import AnalysisScript
from research_repro.phases.phase5_analysis_execution import prompts

class AnalyzerAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client, "analyzer")
        
    def generate_analysis_script(self, artifact: PaperKnowledgeArtifact, env_spec: EnvironmentSpec, processed: ProcessedDatasetArtifact) -> AnalysisScript:
        prompt = prompts.GENERATE_ANALYSIS_SCRIPT_PROMPT.format(
            artifact=artifact.model_dump_json(indent=2),
            env_spec=env_spec.model_dump_json(indent=2),
            processed=processed.model_dump_json(indent=2)
        )
        result, _ = self.run_structured(prompt, AnalysisScript, artifact.model_dump_json())
        return result
