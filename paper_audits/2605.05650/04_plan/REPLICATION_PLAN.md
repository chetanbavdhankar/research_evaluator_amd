# Replication Plan (Tier 3: Blocked)

The replicability of this paper is currently limited (Tier 3) primarily due to gated data access and the absence of published analysis code. While the observational parameters and physical constants (e.g., slit width, exposure times, C_Halpha) are well-documented, the raw Keck/LRIS and HST data are withheld behind a 'contact the authors' policy. Furthermore, the data reduction relies on unspecified routines within the deprecated IRAF software, and the custom scripts used for the 1000-iteration Monte Carlo Gaussian emission line modeling are not provided. Independent replication would require negotiating data access and completely rewriting the spectral fitting pipeline from scratch.

## Gap Synthesis
['Data access is restricted; raw Keck/LRIS spectroscopy and HST imaging require mutually agreeable arrangements with the authors.', 'The specific IRAF tasks and parameters used for spectroscopic data reduction are not detailed.', 'Custom code for the multi-component Gaussian emission/absorption line modeling and Monte Carlo error estimation is missing.', 'The software environment and dependencies (other than IRAF) used for the analysis are completely unspecified.']

## Scorecard

- **data_accessibility**: 1/3

- **data_identifiability**: 1/3

- **method_specification**: 3/3

- **software_stack**: 1/3

- **code_availability**: 0/3

- **compute_footprint**: 3/3

- **dependency_closure**: 2/3

- **result_verifiability**: 2/3


> [!WARNING]
> Do not proceed without remediation. No code execution scaffold is generated for Tier 3 because critical components (data, code, or parameters) are entirely missing or gated.