# Phase 5: Analysis and Method Execution

## Purpose

This phase takes the processed dataset from Phase 4, the environment from Phase 3, and the methodology extracted in Phase 1, and implements and executes the paper's analytical pipeline. This is where the actual scientific methods — machine learning models, statistical tests, algorithms, simulations — are run.

The goal is not to produce the best possible analysis. The goal is to reproduce the paper's analysis as faithfully as possible, including any methodological choices that may seem suboptimal in hindsight. Every implementation decision must be traceable to the PKA.

---

## Core Principle: Reproduce Intent, Not Just Mechanics

A paper describes what was done, but it rarely describes every implementation detail. This phase must distinguish between:

- **Mechanical replication:** implementing exactly the steps described
- **Intent replication:** understanding what the authors were trying to achieve and implementing it faithfully when the exact mechanics are underspecified

When mechanics are clear, follow them. When mechanics are ambiguous, reason about the authors' intent and implement accordingly — but document every such reasoning step explicitly.

---

## Pre-Execution Review

Before writing any analysis code, perform a full review of the methodology section of the PKA. Construct a complete execution plan:

### Execution Plan Structure
For each method or model described in the paper, document:

1. **Method name and type** (e.g., Random Forest classifier, OLS regression, t-SNE dimensionality reduction)
2. **Input:** which processed dataset or features it receives
3. **Configuration:** all hyperparameters, architecture details, or settings described
4. **Training / fitting procedure:** optimization algorithm, number of iterations, stopping criteria, batch size, learning rate schedule, etc.
5. **Evaluation procedure:** how the method is evaluated — which metric, on which split, with which averaging strategy
6. **Expected output:** what the paper reports as the result of this method (linked from the Results section of the PKA)
7. **Dependencies:** does this method depend on the output of another method? (e.g., a downstream classifier that uses embeddings from an upstream encoder)
8. **Citation status:** is this method fully described in the paper, or does it rely on a Citation Backstop from Phase 1?

If a method is flagged as a Citation Backstop, do not implement it. Surface the flag and the citation to the user and wait for resolution or instruction.

---

## Implementation Guidelines

### Modularity
Each method is implemented as a self-contained module or script. It accepts a clearly defined input (processed data, hyperparameters) and produces a clearly defined output (predictions, embeddings, test statistics, figures). No method should silently depend on global state.

### Hyperparameter Handling
All hyperparameters are defined in a single configuration object or file, not scattered through the code. This makes it trivial to audit which values were used and to modify them for sensitivity analysis.

If a hyperparameter is not specified in the paper:
- Use the library's default value
- Log it as a **Hyperparameter Default Record** with the specific value used and the library version it corresponds to
- Flag it as a potential source of discrepancy with the paper

### Baseline Methods
If the paper includes baseline comparisons, implement each baseline with the same rigor as the primary method. Do not use a convenient approximation unless the paper itself uses one.

### Evaluation Metric Implementation
Implement all evaluation metrics exactly as defined in the paper. Common pitfalls:
- Macro vs micro vs weighted averaging for multi-class classification metrics
- Whether AUC is computed per class or globally
- Whether RMSE uses population or sample standard deviation
- Exact definition of precision/recall at k for ranking tasks

If the metric definition is ambiguous, flag it as a **Metric Ambiguity Record** and implement the most common convention, documenting the choice.

---

## Execution Protocol

### Step 1: Smoke Test
Before running the full analysis, run a minimal version on a small data subset to verify:
- Code runs without errors in the reconstructed environment
- Inputs and outputs have the expected shapes and types
- All library functions resolve correctly

### Step 2: Full Execution
Run the complete analysis pipeline on the full processed dataset. During execution:
- Log intermediate outputs at each major step (e.g., training loss curves, intermediate metric values, embedding shapes)
- Log resource usage (time, memory, GPU utilization) for comparison against any compute estimates in the paper
- Capture all warnings and errors, even non-fatal ones

### Step 3: Output Capture
At the end of execution, capture and save:
- All final metric values
- All figures and visualizations produced
- Model weights or fitted parameters (if applicable)
- Any intermediate artifacts referenced in the paper (e.g., confusion matrices, feature importance rankings, cluster assignments)

---

## Stochasticity and Multiple Runs

### Seeded Runs
If random seeds are specified in the PKA or Environment Specification Package, run the analysis exactly once with those seeds.

### Unseeded Runs
If no seeds are specified (flagged as Missing Random Seed in Phase 3), run the analysis multiple times (minimum three, recommended five or more) with different seeds and compute:
- Mean and standard deviation of each reported metric across runs
- Whether the results are stable (low variance) or sensitive to initialization (high variance)

This multi-run result set becomes the comparison target for Phase 6, rather than a single result.

### Stochastic Methods
For methods that are inherently stochastic even with fixed seeds (e.g., certain approximate inference methods, dropout at test time, Monte Carlo estimators), document the expected variance and assess whether the paper's reported results fall within it.

---

## Failure Recovery Protocol

Execution failures are expected. The protocol for handling them determines whether the replication can continue.

### Failure Classification

**Type 1 — Environment Failure:** The code cannot run because a library is missing, a version is incompatible, or a hardware resource is unavailable.
- Resolution: Return to Phase 3, update the environment, and re-execute
- If unresolvable: log as **Blocking Environment Failure** and surface to user

**Type 2 — Data Failure:** The code runs but crashes or produces invalid output due to unexpected data properties (e.g., a feature has a different range than expected, a required column is missing after preprocessing).
- Resolution: Return to Phase 4, investigate the preprocessing output, and correct
- If unresolvable: log as **Blocking Data Failure**

**Type 3 — Implementation Failure:** The code runs but produces outputs that are clearly wrong (e.g., accuracy of 0.0 or 1.0 when neither is expected, loss that increases monotonically, NaN values in outputs).
- Resolution: Review the implementation against the PKA, identify the discrepancy, correct and re-execute
- Common causes: wrong loss function, wrong metric averaging, inverted label encoding, data leakage
- If unresolvable: log as **Blocking Implementation Failure** with full diagnostic

**Type 4 — Convergence Failure:** An iterative method (e.g., gradient descent, EM algorithm, iterative solver) fails to converge within the described number of iterations or within a reasonable time budget.
- Resolution: Check learning rate, initialization, and hyperparameters against PKA
- If unresolvable: log as **Convergence Failure**, report the state at the last iteration, and continue to Phase 6 with the partial result

**Type 5 — Resource Failure:** The analysis exceeds available memory or time budget on the AMD VM.
- Resolution: Assess whether a smaller-scale version (reduced dataset, reduced model size) can produce comparable results, and if so, execute that with a clear flag
- Log as **Resource Constraint Failure** with the resource limit encountered

### Recovery Iteration Limit
If after three recovery attempts a failure persists, it is classified as **Unresolved**. The pipeline continues to Phase 6 with whatever outputs are available, and the unresolved failure is prominently surfaced in the final report.

---

## Sensitivity Analysis (Optional but Recommended)

After successful execution, if time permits, conduct a targeted sensitivity analysis:

- Vary the most impactful unspecified hyperparameters (those flagged as Hyperparameter Default Records) across a small range
- Measure the effect on the primary reported metric
- Report which hyperparameters the results are most sensitive to

This provides valuable context for interpreting any discrepancies found in Phase 6.

---

## Output: Analysis Results Package

The output of this phase is an **Analysis Results Package** containing:

1. **Primary results:** all metric values, figures, and outputs produced by the replication, organized by method and evaluation split
2. **Execution log:** a complete log of all steps executed, intermediate outputs, warnings, and errors
3. **Hyperparameter audit:** all Hyperparameter Default Records and their values
4. **Metric ambiguity records:** all cases where metric definitions were ambiguous and the resolution chosen
5. **Failure records:** all failures encountered, classified by type, with resolution status
6. **Multi-run statistics:** if unseeded runs were performed, the full distribution of results across seeds
7. **Sensitivity analysis results:** if conducted, the effect of hyperparameter variation on primary metrics
8. **Resource usage log:** time, memory, and GPU utilization for each major step

This package is consumed entirely by Phase 6.
