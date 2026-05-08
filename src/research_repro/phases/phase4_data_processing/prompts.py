GENERATE_PREPROCESSING_SCRIPT_PROMPT = """Generate a Python script to preprocess the data according to the paper's methodology.
You must use the datasets listed in the Data Manifest.
Assume the script will run in an isolated directory.
Save the final processed data to 'processed_data.csv' or an appropriate format.

Paper Knowledge Artifact:
{artifact}

Data Manifest:
{manifest}

Return ONLY the Python code and a list of assumptions made (if any parameter was ambiguous).
"""
