from research_repro.agents.base import BaseAgent
from research_repro.tools.llm_client import LLMClient
from research_repro.schemas.paper_knowledge import DatasetDescription
from research_repro.agents.sourcer_models import DatasetClassification, DownloadScript
from research_repro.phases.phase2_data_sourcing import prompts

class SourcingAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client, "sourcer")
        
    def classify_dataset(self, dataset: DatasetDescription) -> DatasetClassification:
        prompt = prompts.CLASSIFY_DATASET_PROMPT.format(
            name=dataset.name,
            description=dataset.description,
            source_type=dataset.source_type,
            links=", ".join(dataset.source_links),
            notes=dataset.notes or ""
        )
        # We don't have source text to verify against here except the dataset dump itself
        result, _ = self.run_structured(prompt, DatasetClassification, dataset.model_dump_json())
        return result
        
    def generate_download_script(self, dataset: DatasetDescription) -> DownloadScript:
        prompt = prompts.GENERATE_DOWNLOAD_SCRIPT_PROMPT.format(
            dataset_info=dataset.model_dump_json(indent=2)
        )
        result, _ = self.run_structured(prompt, DownloadScript, dataset.model_dump_json())
        return result
