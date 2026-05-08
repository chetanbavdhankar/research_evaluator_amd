INFER_DEPENDENCIES_PROMPT = """Analyze the methodology and code descriptions to infer the required programming language, python version, and library dependencies.
For each dependency, state if it's confirmed (explicitly named with version) or inferred (derived from year/framework).

Artifact:
{artifact}
"""

MAP_HARDWARE_PROMPT = """Compare the hardware mentioned in the paper with the available hardware.
Paper Hardware:
{paper_hardware}

Available Hardware:
{available_hardware}
"""

DETERMINE_TARGET_PROMPT = """Determine the reproducibility target (exact, numerical, statistical, qualitative) based on the presence of random seeds, deterministic flags, and hardware differences.
Artifact:
{artifact}
"""

GENERATE_YAML_PROMPT = """Generate a valid conda `environment.yml` for the following dependencies.
Name the environment `{env_name}`.
Dependencies:
{dependencies}

Return ONLY the YAML content in the `yaml_content` field.
"""
