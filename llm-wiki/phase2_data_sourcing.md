# Phase 2: Data Sourcing and Acquisition

## Purpose

This phase takes the Data Description section of the Paper Knowledge Artifact (PKA) produced in Phase 1 and attempts to locate, access, and download the exact datasets used in the paper. The goal is to have the raw data — in its original, unprocessed form — available on the local system before any preprocessing or analysis begins.

This phase operates entirely from what is stated in the PKA. It does not make assumptions about data that was not described. If data cannot be located or accessed, it flags the issue precisely rather than substituting an alternative dataset.

---

## Core Principle: Exactness Over Approximation

The most common failure mode in reproducibility is using a similar but not identical dataset. A dataset from the same source but a different time period, version, or access point can produce meaningfully different results. This phase must prioritize exactness:

- The correct dataset, not a similar one
- The correct version or snapshot, not the latest
- The correct access method, not a convenient substitute

If exactness cannot be guaranteed, this must be flagged explicitly.

---

## Data Classification

The first step is to classify each dataset identified in the PKA into one of the following categories. This classification determines the acquisition strategy.

### Category A: Fully Specified Public Dataset
The paper provides enough information to identify and download the dataset unambiguously. This includes cases where a URL, DOI, repository name and version, or a well-known benchmark name is given.

Examples: "UCI Machine Learning Repository — Heart Disease dataset", "ImageNet ILSVRC 2012", a direct Zenodo DOI link.

### Category B: Partially Specified Public Dataset
The paper names a dataset but does not provide a direct access link, version, or enough detail to unambiguously identify it. The dataset is believed to be public but requires search to locate.

Examples: "we used the MIMIC-III clinical notes dataset" without further specification, "data was obtained from the World Bank Open Data portal."

### Category C: Author-Provided Dataset
The paper states that the dataset is provided by the authors, either as supplementary material, a GitHub repository, or an external link.

### Category D: Proprietary or Restricted Dataset
The dataset is not publicly available. It may require institutional access, a data sharing agreement, or direct contact with the authors.

### Category E: Custom-Generated Dataset
The authors collected or generated their own data from scratch — via web scraping, sensors, surveys, APIs, or simulations. The data is not available from any external source.

### Category F: Unspecified
The paper does not provide enough information to determine how to obtain the data.

Each dataset in the PKA must be assigned a category. Category D, E, and F datasets require human intervention flags.

---

## Acquisition Strategy by Category

### Category A: Fully Specified Public Dataset

1. Parse the URL, DOI, or repository reference from the PKA
2. Attempt automated download
3. Verify the download by checking file size, format, and basic schema against the PKA description
4. Log the exact download source, timestamp, and file hash (MD5 or SHA256) for provenance

### Category B: Partially Specified Public Dataset

1. Construct a search query from the dataset name and any contextual clues in the PKA (domain, size, time period, format)
2. Search across known repositories in priority order:
   - UCI Machine Learning Repository
   - Kaggle Datasets
   - Zenodo
   - Harvard Dataverse
   - OpenML
   - Hugging Face Datasets
   - GitHub (search for dataset name + paper title or authors)
   - Google Dataset Search
   - Domain-specific repositories (e.g., PhysioNet for medical, NOAA for climate, NASA for space)
3. For each candidate found, compare against PKA description: size, format, features, time range, source
4. If a confident match is found, proceed as Category A
5. If no confident match is found, or multiple plausible matches exist, flag as **Data Identification Ambiguity** and surface all candidates with their similarity assessment to the user

### Category C: Author-Provided Dataset

1. Check supplementary material of the paper (if PDF, check for embedded files or appendix links)
2. Search for the paper's associated GitHub repository (search by paper title, DOI, or authors)
3. Check author institutional pages or personal websites if referenced
4. Attempt automated download from any identified links
5. If links are broken or unavailable, flag as **Data Access Failure** with the original link and attempted access timestamp

### Category D: Proprietary or Restricted Dataset

1. Log the dataset name, the restriction type as described in the paper, and any access instructions mentioned
2. Flag as **Manual Intervention Required — Restricted Data**
3. Provide the user with:
   - The exact dataset name and description
   - Any access request process mentioned in the paper
   - Contact information for the authors if available
4. Pause this data stream and continue with any other datasets that are accessible

### Category E: Custom-Generated Dataset

1. Extract the full data generation description from the PKA
2. Assess whether the generation process can be automated:
   - If it involves a public API (e.g., Twitter API, a weather service), note the API and any parameters described
   - If it involves web scraping, note the target sources and any described methodology
   - If it involves physical sensors, lab equipment, or human annotation, flag as **Manual Intervention Required — Custom Data Generation**
3. For automatable generation processes, document the generation pipeline for Phase 4 to implement
4. Flag any parts of the generation process that are underspecified

### Category F: Unspecified

1. Flag as **Data Source Unknown**
2. Log the exact description of the data as given in the paper
3. Surface to the user with a request for clarification or manual sourcing

---

## Data Validation After Acquisition

Once data is downloaded or generated, validate it against the PKA description before passing it to Phase 3.

### Schema Validation
- Do the columns, fields, or features match what is described?
- Are the data types consistent with the description?
- Are the expected classes, labels, or target variables present?

### Size Validation
- Does the number of samples match the paper's description?
- If the paper reports a specific size (e.g., "50,000 images", "1.2 million records"), verify against the actual download
- Flag any discrepancy as a **Size Mismatch**

### Statistical Validation
- Compute basic descriptive statistics (mean, std, min, max, null counts) for numerical features
- Compare against any statistics reported in the paper
- Flag significant discrepancies

### Version Validation
- If the dataset is versioned, confirm the version matches what the paper specifies
- If the paper does not specify a version but multiple versions exist, flag as **Version Ambiguity** and document which version was downloaded

---

## Provenance Logging

For every dataset acquired, log:
- Source URL or access method
- Download timestamp
- File hash (MD5 or SHA256)
- File format and size
- Version or snapshot identifier if available
- Any discrepancies found during validation

This log is critical for reproducibility of the reproducibility itself — it must be possible for a third party to replicate exactly which data was used.

---

## Human Intervention Flags

The following conditions require surfacing to the user before the pipeline can proceed:

- **Manual Intervention Required — Restricted Data:** Dataset requires access agreement or institutional credentials
- **Manual Intervention Required — Custom Data Generation:** Data generation process cannot be automated
- **Data Identification Ambiguity:** Multiple candidate datasets found, cannot determine which is correct
- **Data Access Failure:** Download link is broken or returns an error
- **Size Mismatch:** Downloaded data differs significantly in size from paper description
- **Version Ambiguity:** Multiple versions of dataset exist and paper does not specify

When a flag is raised, the pipeline pauses that specific data stream and continues with any remaining datasets. The user is presented with a clear, actionable description of what is needed.

---

## Output

The output of this phase is a **Data Manifest** containing:

1. For each dataset: category classification, acquisition status, local file path, provenance log, validation results
2. A list of all human intervention flags with full context
3. A readiness assessment: which datasets are ready for Phase 3, which are blocked

The Data Manifest is consumed by Phase 3 (Environment Reconstruction) and Phase 4 (Data Processing Replication).
