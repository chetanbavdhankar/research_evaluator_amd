from research_repro.agents.base import BaseAgent
from research_repro.tools.llm_client import LLMClient
from research_repro.schemas.paper_knowledge import PaperKnowledgeArtifact
from research_repro.agents.environment_models import (
    InferredDependencies, HardwareMapping, ReproducibilityTargetResult, EnvironmentYaml
)
from research_repro.phases.phase3_environment import prompts

class EnvironmentAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client, "environment")
        
    def infer_dependencies(self, artifact: PaperKnowledgeArtifact) -> InferredDependencies:
        prompt = prompts.INFER_DEPENDENCIES_PROMPT.format(
            artifact=artifact.model_dump_json()
        )
        result, _ = self.run_structured(prompt, InferredDependencies, artifact.model_dump_json())
        return result
        
    def map_hardware(self, artifact: PaperKnowledgeArtifact, available_hardware: str) -> HardwareMapping:
        # Extract hardware info if any, otherwise pass entire methodology
        paper_hardware = "Unknown"
        # Dummy extraction for prompt
        prompt = prompts.MAP_HARDWARE_PROMPT.format(
            paper_hardware=paper_hardware,
            available_hardware=available_hardware
        )
        result, _ = self.run_structured(prompt, HardwareMapping, "")
        return result
        
    def determine_reproducibility_target(self, artifact: PaperKnowledgeArtifact) -> ReproducibilityTargetResult:
        prompt = prompts.DETERMINE_TARGET_PROMPT.format(
            artifact=artifact.model_dump_json()
        )
        result, _ = self.run_structured(prompt, ReproducibilityTargetResult, artifact.model_dump_json())
        return result
        
    def generate_environment_yml(self, dependencies: list, env_name: str) -> EnvironmentYaml:
        deps_str = "\n".join([f"- {d.name} {d.version if d.version else ''}" for d in dependencies])
        prompt = prompts.GENERATE_YAML_PROMPT.format(
            env_name=env_name,
            dependencies=deps_str
        )
        result, _ = self.run_structured(prompt, EnvironmentYaml, deps_str)
        return result
