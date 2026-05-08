CLASSIFY_DATASET_PROMPT = """Classify the following dataset description into one of these categories:
A_public_specified: Fully specified public dataset (e.g. direct URL, exact HuggingFace/Kaggle name)
B_public_partial: Public but not fully specified (needs search)
C_author_provided: Author provided via GitHub/supplementary
D_proprietary: Proprietary or restricted
E_custom_generated: Custom generated via code/API/sensors
F_unspecified: Not enough info

Dataset description:
Name: {name}
Description: {description}
Source type: {source_type}
Links: {links}
Notes: {notes}
"""

GENERATE_DOWNLOAD_SCRIPT_PROMPT = """Generate a Python script to download this dataset to the directory specified by `DEST_DIR`.
You must define a constant `DEST_DIR` (e.g. from an env var or a hardcoded path placeholder) but in the code use `os.environ.get("DATA_DEST_DIR", ".")` to actually download.

Dataset:
{dataset_info}

Return the python code and any pip packages required (like `requests`, `datasets`, `kaggle`).
"""
