from research_repro.agents.base import BaseAgent
from research_repro.tools.llm_client import LLMClient
from research_repro.schemas.paper_knowledge import PaperKnowledgeArtifact
from research_repro.schemas.data_manifest import DataManifest
from research_repro.agents.data_processor_models import PreprocessingScript
from research_repro.phases.phase4_data_processing import prompts

class DataProcessorAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client, "data_processor")
        
    def generate_preprocessing_script(self, artifact: PaperKnowledgeArtifact, manifest: DataManifest) -> PreprocessingScript:
        prompt = prompts.GENERATE_PREPROCESSING_SCRIPT_PROMPT.format(
            artifact=artifact.model_dump_json(indent=2),
            manifest=manifest.model_dump_json(indent=2)
        )
        result, _ = self.run_structured(prompt, PreprocessingScript, artifact.model_dump_json())
        return result
