METADATA_PROMPT = """Extract the paper metadata.
Title, authors, venue, year, doi. You do not need to populate input_source or arxiv_id.
Source text (beginning of paper):
{text}
"""

SUMMARY_PROMPT = """Extract the paper summary (abstract, research question, domain, claimed contributions).
Source text:
{text}
"""

DATASETS_PROMPT = """Extract the dataset descriptions from the paper. Ensure to quote the paper where requested.
Source text:
{text}
"""

PREPROCESSING_PROMPT = """Extract the data preprocessing and wrangling pipeline.
Source text:
{text}
"""

METHODOLOGY_PROMPT = """Extract the methodology and analysis specification.
Source text:
{text}
"""

RESULTS_PROMPT = """Extract the quantitative and qualitative results.
Source text:
{text}
"""

CONCLUSIONS_PROMPT = """Extract the authors' conclusions as a list of strings.
Source text:
{text}
"""

CITATION_DEPS_PROMPT = """Identify any citation dependencies (methods/datasets used but not fully described, relying on citation).
Source text:
{text}
"""

AMBIGUITY_FLAGS_PROMPT = """Identify any ambiguities in the data, preprocessing, or hyperparameter gaps.
Source text:
{text}
"""

RISK_ASSESSMENT_PROMPT = """Assess the reproducibility risk of this paper based on the extracted artifact.
Return your assessment in the 'assessment' field.
Artifact:
{artifact}
"""
