# Phase 3: Environment Reconstruction

## Purpose

Before any code is written or executed, the computational environment in which the original research was conducted must be understood and reconstructed as faithfully as possible. A result that is reproducible in one environment may fail silently or produce different outputs in another due to library version differences, numerical precision issues, OS-level behavior, or hardware-dependent optimizations.

This phase takes the PKA from Phase 1 and constructs a precise specification of the execution environment required to replicate the paper's results. Where the paper provides explicit environment details, those are used directly. Where details are missing, a principled inference process is applied and all assumptions are documented.

---

## Core Principle: Environment as a First-Class Artifact

The environment is not a setup step — it is a reproducibility artifact in its own right. The inability to reconstruct an environment is a reproducibility failure just as much as the inability to reproduce a numerical result. Every decision made in this phase must be logged with its justification.

---

## What Constitutes the Environment

The environment has five layers, each of which must be addressed:

### Layer 1: Programming Language and Runtime
- Primary language used (Python, R, Julia, MATLAB, etc.)
- Runtime version (e.g., Python 3.8.12, R 4.1.2)
- Any secondary languages used (e.g., C extensions, shell scripts, SQL)

### Layer 2: Package and Library Dependencies
- All libraries and packages explicitly named in the paper
- Their versions, if specified
- Package manager used (pip, conda, CRAN, etc.)

### Layer 3: Hardware and Compute
- CPU vs GPU computation
- Specific GPU model if named (e.g., NVIDIA A100, V100, RTX 3090)
- Number of GPUs or nodes if specified
- RAM requirements if mentioned
- Approximate compute time reported (e.g., "trained for 48 hours")

### Layer 4: Operating System and System-Level Dependencies
- OS mentioned in the paper (Linux distribution, Windows, macOS)
- Any system-level libraries mentioned (e.g., CUDA version, cuDNN version, MKL)
- Container or virtualization tools mentioned (Docker, Singularity, conda environments)

### Layer 5: Reproducibility Aids
- Random seeds specified
- Determinism flags (e.g., `torch.backends.cudnn.deterministic = True`)
- Any frozen or pinned dependency files provided (requirements.txt, environment.yml, Pipfile.lock)

---

## Extraction from the PKA

### Explicit Information
Search the PKA systematically for:
- Version numbers attached to any library or tool name
- Hardware specifications in the experimental setup section
- Compute time and resource descriptions
- Any mention of Docker, conda, virtualenv, or similar
- GitHub links that may contain requirements files or Dockerfiles
- Appendix sections on computational resources (common in ML papers)
- Author-provided code repositories linked in the paper

### Implicit Information
Many papers do not fully specify their environment. Apply the following inference rules, documenting each as an assumption:

- If a deep learning framework is named (PyTorch, TensorFlow, JAX) and the paper was published in a specific year, infer the likely version range from the publication date and the API calls described or cited
- If CUDA is implied by GPU usage, infer the likely CUDA version from the GPU model and framework version
- If the paper uses a specific function or API that was introduced or deprecated in a known version, use this to bound the version range
- If a conda environment file or requirements.txt is found in an associated repository, treat it as authoritative

Every inference must be logged as an **Environment Assumption** with:
- What was inferred
- The reasoning behind the inference
- The confidence level (high / medium / low)
- The risk if the assumption is wrong

---

## Environment Reconstruction Strategy

### Step 1: Build the Dependency List
Compile a complete list of all libraries and tools needed, with versions where known. Separate into:
- **Confirmed:** version explicitly stated in paper or associated repository
- **Inferred:** version derived through the inference process above
- **Unknown:** library named but version cannot be determined

### Step 2: Resolve Conflicts and Compatibility
Check that the confirmed and inferred versions are mutually compatible. Common conflict points:
- Python version compatibility with library versions
- CUDA version compatibility with PyTorch/TensorFlow versions
- NumPy version compatibility with downstream libraries

If conflicts are detected, flag them as **Dependency Conflicts** and propose resolution strategies.

### Step 3: Construct the Environment Specification
Produce a concrete environment specification in one or more standard formats:
- `requirements.txt` for pip-based Python environments
- `environment.yml` for conda environments
- `Dockerfile` if containerization is appropriate or if the paper used Docker
- An equivalent specification for R (`renv.lock`) or other languages as appropriate

For all inferred versions, use the most conservative (oldest compatible) version within the inferred range to maximize compatibility.

### Step 4: Provision the Environment
On the target compute platform (in this case, the AMD virtual machine), instantiate the environment using the specification produced in Step 3. Verify:
- All packages install without errors
- All imports resolve correctly
- A minimal smoke test passes (import key libraries, check versions)

### Step 5: Hardware Alignment
Assess whether the available hardware matches what the paper used:
- If the paper used a GPU and the VM has a GPU available, verify driver and CUDA version compatibility
- If the paper used a specific GPU model not available, document the discrepancy and assess the likely impact on results (numerical differences, speed, memory constraints)
- If the paper used multi-GPU or distributed training, note that single-GPU replication may produce different results due to batch size scaling and gradient aggregation differences

Document all hardware discrepancies as **Hardware Gap Records** with impact assessment.

---

## Stochasticity and Determinism

Many computational environments introduce non-determinism that affects reproducibility. Address the following:

### Random Seeds
- Extract all random seeds mentioned in the paper
- If no seeds are mentioned, flag as **Missing Random Seed** — this means exact numerical reproducibility may be impossible
- Document which components use randomness: data splitting, model initialization, dropout, data augmentation, stochastic optimization

### Framework-Level Determinism
- Some frameworks (PyTorch, TensorFlow) have explicit determinism flags that must be set to guarantee reproducible results
- Even with these flags set, results may differ across hardware (CPU vs GPU) or across GPU architectures
- Document whether the paper's results are expected to be exactly reproducible or only statistically equivalent

### Defining the Reproducibility Target
Based on the above, define the reproducibility target for this replication:
- **Exact:** bit-for-bit identical outputs expected (rare, requires exact seeds, hardware, and framework versions)
- **Numerical:** results match within floating-point tolerance (e.g., within 1e-6)
- **Statistical:** results fall within a reasonable confidence interval around reported values (appropriate when exact seeds are not given)
- **Qualitative:** results support the same conclusions even if exact numbers differ (last resort when environment cannot be precisely reconstructed)

This target is passed to Phase 6 (Results Validation) as the benchmark for assessing reproducibility success.

---

## Output: Environment Specification Package

The output of this phase is an **Environment Specification Package** containing:

1. **Dependency manifest:** full list of libraries with confirmed/inferred/unknown versions
2. **Environment files:** requirements.txt, environment.yml, and/or Dockerfile
3. **Environment assumption log:** all inferences made, with reasoning and confidence
4. **Dependency conflict log:** any conflicts detected and how they were resolved
5. **Hardware gap records:** discrepancies between paper's hardware and available hardware
6. **Reproducibility target definition:** exact / numerical / statistical / qualitative, with justification
7. **Provisioning status:** confirmation that the environment was successfully instantiated on the target VM, or a list of failures

This package is consumed by Phase 4 and Phase 5. All code written in those phases must execute within the environment specified here.
