# Phase 4: Data Processing Replication

## Purpose

This phase takes the raw data acquired in Phase 2 and the environment established in Phase 3, and faithfully replicates every preprocessing and data wrangling step described in the paper. The goal is to produce a processed dataset that is, to the highest degree possible, identical to what the original authors fed into their analysis.

This phase is the most detail-sensitive in the entire pipeline. A single omitted step, a wrong parameter, or an incorrect order of operations can silently corrupt every downstream result. Every decision must be traceable back to a specific statement in the PKA.

---

## Core Principle: Fidelity to the Paper, Transparency of Assumptions

The preprocessing code written in this phase must mirror the paper's described pipeline exactly. Where the paper is explicit, implement exactly that. Where the paper is ambiguous or silent, make the most reasonable assumption, document it clearly, and flag it for validation in Phase 6.

No preprocessing step should be added that is not described or clearly implied in the paper, even if it seems obviously beneficial. The goal is replication, not improvement.

---

## Preprocessing Pipeline Reconstruction

### Step 1: Extract the Ordered Pipeline from the PKA

From the PKA's Preprocessing Pipeline section, construct an ordered sequence of operations. For each operation, identify:

- **Operation type:** cleaning, transformation, encoding, filtering, splitting, augmentation, etc.
- **Input:** which data or features it operates on
- **Parameters:** any numerical thresholds, choices, or settings described
- **Output:** what the data looks like after this step
- **Traceability:** the exact sentence or passage in the PKA this is derived from

If the paper does not specify the order of operations, infer the most natural order (e.g., cleaning before transformation, splitting before normalization to prevent data leakage) and flag each inferred ordering as a **Pipeline Order Assumption**.

### Step 2: Identify Ambiguities Before Writing Code

Before writing any code, perform a full review of the extracted pipeline for ambiguities. Common categories:

**Parameter Gaps:** A step is described but a key parameter is not given. Example: "we removed outliers using the IQR method" — but the IQR multiplier (commonly 1.5 or 3.0) is not stated.

**Scope Gaps:** It is unclear which features or subsets of the data a step applies to. Example: "we normalized the features" — but it is not stated whether this means all features, only numerical ones, or a specific subset.

**Method Gaps:** A step is named but not defined. Example: "we applied standard preprocessing" — which is ambiguous. If this is a Citation Backstop case (method is cited to another paper), apply the backstop procedure from Phase 1.

**Sequence Gaps:** It is unclear whether a step happens before or after another. Example: both train/test splitting and normalization are described, but the order is not stated.

For each ambiguity, log a **Preprocessing Assumption Record** containing:
- The ambiguous step
- The assumption made
- The reasoning (e.g., "IQR multiplier of 1.5 is the conventional default")
- The sensitivity of downstream results to this assumption (high / medium / low)

### Step 3: Implement the Pipeline

Write code that implements each preprocessing step in sequence. The code must:

- Be modular: each step is a separate, clearly named function
- Be documented: each function has a docstring that quotes or paraphrases the relevant PKA passage
- Be logged: at each step, print or log the shape and basic statistics of the data before and after the transformation
- Be assertion-rich: include assertions that verify expected properties hold after each step (e.g., no null values after imputation, correct shape after filtering)
- Be parameterized: all numerical parameters are defined as named constants at the top of the script, not hardcoded inline

### Step 4: Handle Missing or Ambiguous Steps

When a step cannot be implemented because information is missing:

- Do not skip it silently
- Do not invent a replacement without flagging it
- Log a **Preprocessing Gap Record** with the step description, what is missing, and what assumption (if any) was made
- If the gap is severe enough that it invalidates downstream results, flag the entire pipeline as **Partially Replicable** and document exactly what is missing

---

## Specific Preprocessing Considerations

### Missing Value Handling
- What imputation strategy is described? (mean, median, mode, forward fill, model-based, deletion)
- Is it applied per feature, per row, or globally?
- Is there a threshold for missingness above which a row or column is dropped?

### Outlier Treatment
- Is it described? (many papers omit this)
- What method? (IQR, z-score, domain-specific rules)
- Is it applied before or after splitting?

### Train / Validation / Test Splitting
- Is the split described? (ratio, stratification, random vs time-based)
- Is a random seed given for the split? If not, flag as **Missing Split Seed** — this is a significant reproducibility risk
- Is k-fold cross-validation used? If so, how many folds, and is stratification applied?

### Normalization and Scaling
- Is it min-max normalization, z-score standardization, or something else?
- Is it fit on the training set and applied to validation/test (correct), or fit on the full dataset (data leakage risk to note)?
- If the paper does it incorrectly (e.g., fits on full data), replicate the incorrect behavior exactly and note it

### Encoding
- How are categorical variables encoded? (one-hot, ordinal, target encoding, embeddings)
- Are specific encodings described for specific features?

### Feature Engineering
- Are derived features described? Implement them exactly as described
- If a derived feature's formula is implied but not stated, flag as a **Feature Engineering Assumption**

### Data Augmentation
- Is augmentation described? (common in image, audio, and NLP tasks)
- What augmentation strategy? (flipping, rotation, noise addition, synonym replacement, etc.)
- Is augmentation applied only at training time or also at inference?
- Are augmentation parameters (e.g., rotation range, noise standard deviation) specified?

### Custom Dataset Construction
- If the authors built their own dataset from multiple sources, implement the joining and merging logic as described
- Flag any joins where the join key or merge strategy is not specified

---

## Stochasticity in Preprocessing

Any preprocessing step that involves randomness must be handled carefully:

- Set all random seeds as specified in the PKA or the Environment Specification Package
- If no seed is given for a specific random operation, use a documented default seed and log it as a **Stochastic Assumption**
- For operations that are inherently non-deterministic (e.g., certain parallel data loading operations), document the expected variance and whether it is expected to affect final results

---

## Failure Recovery

If any preprocessing step fails during execution:

### Failure Classification
- **Hard Failure:** The step cannot be completed at all (e.g., a required column is missing from the data, a library function does not exist in the installed version)
- **Soft Failure:** The step completes but produces unexpected output (e.g., more null values after imputation than expected, negative values in a feature that should be non-negative)

### Recovery Protocol
For Hard Failures:
1. Log the exact error with full stack trace
2. Identify the root cause: data issue, environment issue, or ambiguous implementation
3. Attempt one alternative interpretation if the paper allows it
4. If still failing, flag the step as **Unresolved** and document what would be needed to resolve it
5. Assess whether the pipeline can continue without this step or whether it is a blocking failure

For Soft Failures:
1. Log the unexpected output with before/after statistics
2. Assess whether the deviation is within acceptable bounds or indicates a fundamental issue
3. Continue the pipeline but flag the step in the Preprocessing Assumption Record with its anomaly

---

## Output: Processed Dataset and Preprocessing Audit

The output of this phase is:

1. **Processed dataset(s):** the data in the state it should be in immediately before the analysis phase, saved to disk in a clearly named, versioned file
2. **Train/validation/test splits:** saved as separate files if applicable
3. **Preprocessing code:** fully documented, modular, executable script(s)
4. **Preprocessing audit log:** a complete record of:
   - Each step executed, with before/after statistics
   - All Preprocessing Assumption Records
   - All Preprocessing Gap Records
   - All Stochastic Assumption Records
   - All Hard and Soft Failures with their resolution status
5. **Replicability assessment:** a summary judgment of how faithfully the preprocessing was replicated (fully faithful / partially faithful with documented gaps / substantially deviated)

This output is consumed entirely by Phase 5.
