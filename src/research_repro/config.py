from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field
from typing import Literal

class LLMEndpointConfig(BaseModel):
    endpoint: str = "http://localhost:11434/v1"
    model: str = "qwen3.5:4b"
    api_key: str = "none"
    temperature: float = 0.0
    max_tokens: int = 4096

class GPUComputeConfig(BaseModel):
    endpoint: str = ""

class ExecutionConfig(BaseModel):
    subprocess_timeout_seconds: int = 1800
    max_memory_gb: int = 32

class ConcurrencyConfig(BaseModel):
    phase2_max_parallel_downloads: int = 4
    phase5_max_parallel_seeds: int = 3

class DiscrepancyThresholds(BaseModel):
    match: float = 1e-6
    close_match: float = 0.01
    moderate: float = 0.10

class FlagsConfig(BaseModel):
    max_seed_runs_when_unseeded: int = 5
    discrepancy_thresholds: DiscrepancyThresholds = DiscrepancyThresholds()

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    # Values loaded from environment variables
    llm_endpoint: str = "http://localhost:11434/v1"
    llm_model: str = "qwen3.5:4b"
    llm_api_key: str = "none"
    amd_compute_endpoint: str = ""
    
    # Run defaults
    paper_input: str = ""
    run_directory: str = ""
    mode: Literal["auto", "interactive"] = "auto"
    
    execution: ExecutionConfig = ExecutionConfig()
    concurrency: ConcurrencyConfig = ConcurrencyConfig()
    flags: FlagsConfig = FlagsConfig()
    
    @property
    def model(self) -> LLMEndpointConfig:
        return LLMEndpointConfig(
            endpoint=self.llm_endpoint,
            model=self.llm_model,
            api_key=self.llm_api_key,
            temperature=0.0,
            max_tokens=4096
        )

    @property
    def gpu_compute(self) -> GPUComputeConfig:
        return GPUComputeConfig(endpoint=self.amd_compute_endpoint)
