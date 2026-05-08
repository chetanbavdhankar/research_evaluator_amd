GENERATE_ANALYSIS_SCRIPT_PROMPT = """Generate a Python script to execute the methodology described in the paper.
You must use the processed datasets.
Assume the script will run in an isolated directory.
Save the final evaluation metrics to 'results.json'.

Paper Knowledge Artifact:
{artifact}

Environment Spec:
{env_spec}

Processed Dataset:
{processed}

Return ONLY the Python code, along with any hyperparameters you assumed defaults for, and any metric ambiguities you resolved.
"""
