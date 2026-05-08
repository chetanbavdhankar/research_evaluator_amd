from research_repro.agents.base import BaseAgent
from research_repro.tools.llm_client import LLMClient
from research_repro.tools.document_types import ParsedPaper
from research_repro.schemas.paper_knowledge import (
    PaperMetadata, PaperSummary, DatasetDescription,
    PreprocessingStep, MethodSpecification, ResultRecord,
    PaperKnowledgeArtifact
)
from research_repro.schemas.common import CitationDependency, AmbiguityFlag
from research_repro.agents.reader_models import (
    DatasetDescriptionsList, PreprocessingStepList, MethodSpecificationList,
    ResultRecordList, StringList, CitationDependencyList, AmbiguityFlagList,
    RiskAssessment
)
from research_repro.phases.phase1_paper_comprehension import prompts

class ReaderAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client, "reader")

    def _get_text(self, parsed_paper: ParsedPaper, max_pages: int = None) -> str:
        pages = parsed_paper.pages
        if max_pages is not None:
            pages = pages[:max_pages]
        return "\n\n".join(pages)

    def extract_metadata(self, parsed_paper: ParsedPaper) -> PaperMetadata:
        text = self._get_text(parsed_paper, max_pages=2)
        prompt = prompts.METADATA_PROMPT.format(text=text)
        result, _ = self.run_structured(prompt, PaperMetadata, text)
        return result

    def extract_summary(self, parsed_paper: ParsedPaper) -> PaperSummary:
        text = self._get_text(parsed_paper, max_pages=3)
        prompt = prompts.SUMMARY_PROMPT.format(text=text)
        result, _ = self.run_structured(prompt, PaperSummary, text)
        return result

    def extract_datasets(self, parsed_paper: ParsedPaper) -> list[DatasetDescription]:
        text = self._get_text(parsed_paper)
        prompt = prompts.DATASETS_PROMPT.format(text=text)
        result, _ = self.run_structured(prompt, DatasetDescriptionsList, text)
        return result.items

    def extract_preprocessing_pipeline(self, parsed_paper: ParsedPaper) -> list[PreprocessingStep]:
        text = self._get_text(parsed_paper)
        prompt = prompts.PREPROCESSING_PROMPT.format(text=text)
        result, _ = self.run_structured(prompt, PreprocessingStepList, text)
        return result.items

    def extract_methodology(self, parsed_paper: ParsedPaper) -> list[MethodSpecification]:
        text = self._get_text(parsed_paper)
        prompt = prompts.METHODOLOGY_PROMPT.format(text=text)
        result, _ = self.run_structured(prompt, MethodSpecificationList, text)
        return result.items

    def extract_results(self, parsed_paper: ParsedPaper) -> list[ResultRecord]:
        text = self._get_text(parsed_paper)
        prompt = prompts.RESULTS_PROMPT.format(text=text)
        result, _ = self.run_structured(prompt, ResultRecordList, text)
        return result.items

    def extract_conclusions(self, parsed_paper: ParsedPaper) -> list[str]:
        text = self._get_text(parsed_paper)
        prompt = prompts.CONCLUSIONS_PROMPT.format(text=text)
        result, _ = self.run_structured(prompt, StringList, text)
        return result.items

    def detect_citation_dependencies(self, parsed_paper: ParsedPaper, methods: list[MethodSpecification]) -> list[CitationDependency]:
        text = self._get_text(parsed_paper)
        prompt = prompts.CITATION_DEPS_PROMPT.format(text=text)
        result, _ = self.run_structured(prompt, CitationDependencyList, text)
        return result.items

    def detect_ambiguity_flags(self, parsed_paper: ParsedPaper) -> list[AmbiguityFlag]:
        text = self._get_text(parsed_paper)
        prompt = prompts.AMBIGUITY_FLAGS_PROMPT.format(text=text)
        result, _ = self.run_structured(prompt, AmbiguityFlagList, text)
        return result.items

    def assess_reproducibility_risk(self, artifact_data: dict) -> str:
        prompt = prompts.RISK_ASSESSMENT_PROMPT.format(artifact=artifact_data)
        # Pass empty source text as this operates on the artifact
        result, _ = self.run_structured(prompt, RiskAssessment, "")
        return result.assessment
