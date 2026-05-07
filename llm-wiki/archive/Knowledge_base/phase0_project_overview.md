# Autonomous Research Reproducibility Engine
## Project Overview, Philosophy, and Objectives

---

## The Problem

Science advances by building on prior work. That foundation depends on one critical assumption: that published results are correct and reproducible. In practice, this assumption fails far more often than the scientific community is comfortable admitting.

The reproducibility crisis is well documented. Across fields — psychology, medicine, machine learning, economics, biology — a substantial fraction of published findings either cannot be reproduced at all or reproduce only partially. The causes are many: insufficient methodological detail in papers, undisclosed preprocessing choices, missing random seeds, proprietary data, environment-specific behavior, and in some cases, errors or selective reporting in the original work itself.

The cost of this is enormous. Researchers waste months building on results that do not hold. Practitioners deploy methods that do not generalize. Funding flows toward findings that cannot be independently verified. The cumulative effect is a drag on the pace of scientific progress that is almost entirely invisible because it happens in private — in failed lab replications, abandoned research directions, and quietly shelved projects.

The manual process of replicating a paper is slow, expensive, and requires deep expertise. A researcher attempting to reproduce another team's work must read the paper carefully, hunt for data across repositories, reconstruct a computational environment from incomplete descriptions, implement methods from ambiguous pseudocode, and then interpret discrepancies without knowing whether they are due to their own error or the original paper's. This process can take weeks and often produces no publishable output, giving researchers little incentive to do it systematically.

---

## The Motivation

This project is motivated by a simple conviction: the process of attempting to reproduce a scientific paper is itself a structured, well-defined workflow. It follows the same steps every time, regardless of the domain. It requires the same kinds of decisions, the same kinds of information extraction, and the same kinds of failure handling. If the process is structured, it can be automated.

The emergence of capable large language models that can read and reason about scientific text, combined with agentic systems that can use tools, write and execute code, search the web, and make decisions autonomously, makes this automation feasible for the first time. A system that can read a paper, locate its data, reconstruct its environment, implement its methods, run the analysis, and compare the outputs against reported results — end to end, with minimal human intervention — would represent a qualitative shift in the economics of reproducibility.

Such a system would make reproducibility cheap enough to do routinely rather than exceptionally. It would surface methodological gaps that are currently invisible. It would create a scalable mechanism for building trust in scientific results — or for identifying where that trust is not warranted.

This is what we are building.

---

## The Idea

The Autonomous Research Reproducibility Engine is a multi-agent system that takes a single input — a PDF, HTML page, or arXiv link to a research paper — and autonomously attempts to reproduce the results reported in that paper.

The system reads the paper, understands it as a structured scientific artifact, identifies the data used, locates and downloads that data, reconstructs the computational environment, implements the preprocessing pipeline, runs the analysis, and produces a structured report comparing its outputs to the paper's reported results.

Every step is designed to be:

**Autonomous:** The system makes decisions at each step based on what it extracts from the paper. Human intervention is requested only when the system hits a genuine blocker — restricted data, a missing method description, a hardware requirement it cannot meet — not as a routine part of the workflow.

**Transparent:** Every decision the system makes is logged. Every assumption is documented. Every discrepancy is attributed. A third party reading the system's output should be able to understand exactly what was done, why, and where the uncertainties lie.

**Honest:** The system does not paper over failures. If a result cannot be reproduced, it says so and explains why. If a method is underspecified, it flags it rather than hallucinating an implementation. If a discrepancy is unexplained, it says the discrepancy is unexplained. Accuracy of the assessment matters more than the appearance of success.

**Domain-agnostic:** The system is not built for machine learning papers, or for biology papers, or for economics papers. It is built for any paper that uses data. The pipeline — extract, source, reconstruct, preprocess, analyze, validate — is the same regardless of domain. Domain-specific knowledge is applied locally within each phase, not hardcoded into the architecture.

**Modular:** The pipeline is divided into six clearly separated phases, each with a well-defined input and output. This means failures are isolated, phases can be improved independently, and the system can be run partially — for example, stopping after Phase 1 to produce a structured paper summary, or running only Phases 1 through 3 to assess whether a paper is even reproducible before investing in full replication.

---

## The Six-Phase Pipeline

The system operates as a sequential pipeline of six phases. Each phase produces a structured artifact that is consumed by the next phase. No phase makes assumptions beyond what is contained in its inputs.

**Phase 1 — Paper Comprehension and Detail Extraction:** The system reads the paper and produces a structured, queryable knowledge artifact covering all sections, with deep extraction of data, preprocessing, methodology, and results. All ambiguities and citation dependencies are flagged.

**Phase 2 — Data Sourcing and Acquisition:** The system locates and downloads the datasets described in the paper from public repositories, author-provided links, or supplementary materials. It validates that the acquired data matches the paper's description and flags anything requiring manual intervention.

**Phase 3 — Environment Reconstruction:** The system identifies the computational environment required — programming language, library versions, hardware, operating system — and provisions it on the target compute platform. It defines the reproducibility target (exact, numerical, statistical, or qualitative) based on how much environment information is available.

**Phase 4 — Data Processing Replication:** The system implements and executes every preprocessing and data wrangling step described in the paper, in order, on the acquired data. All assumptions are documented. All failures are classified and handled.

**Phase 5 — Analysis and Method Execution:** The system implements and runs the paper's analytical methods — models, statistical tests, algorithms — on the processed data. It captures all outputs, handles failures, and runs multiple seeds when determinism cannot be guaranteed.

**Phase 6 — Results Validation and Report Generation:** The system compares its outputs to the paper's reported results, assesses each claim, classifies discrepancies, and produces a structured reproducibility report.

---

## The Objective

The primary objective is to produce, from a single paper input, a reproducibility report that answers the following questions:

1. Can the results of this paper be independently reproduced?
2. If yes, how closely do the reproduced results match the reported ones?
3. If no, or only partially, what are the specific reasons — missing information, inaccessible data, undisclosed implementation choices, or genuine discrepancy?
4. What would be needed to close any remaining reproducibility gaps?

The secondary objective is to do this autonomously, at scale, and across domains — so that reproducibility assessment becomes a routine part of how science is evaluated, not an exceptional effort undertaken by a handful of dedicated labs.

The tertiary objective, embedded in the system's design, is to surface the information that papers systematically fail to report — seeds, exact library versions, preprocessing edge cases, hyperparameter defaults — and make that information visible, so that the scientific community can develop better norms around what constitutes a complete and reproducible paper.

---

## What This System Is Not

It is worth being explicit about the scope boundaries.

This system may or may not evaluate whether a paper's research question is interesting, whether its methods are state of the art, or whether its conclusions are scientifically significant. It assesses reproducibility, not quality.

This system may or may not detect fraud. A paper that fabricates results that happen to be reproducible from fabricated data would pass this system's validation. Reproducibility is a necessary but not sufficient condition for trustworthiness.

This system may or may not replace human peer review. It complements it by providing a systematic, automated check on one specific dimension — can the numbers be independently obtained — that human reviewers rarely have the time or resources to perform.

This system does not require the original authors' cooperation. It works from what is publicly available. Where cooperation would help — sharing data, sharing code, clarifying methods — the system identifies exactly what is needed and surfaces it as an actionable request.

---

## Design Principles

**Fail loudly, not silently.** The system surfaces every gap, assumption, and failure. It never resolves ambiguity by guessing without documenting the guess. A silent failure that produces a plausible-looking but wrong output is worse than an explicit failure that stops and asks for help.

**Trace everything.** Every output of the system can be traced back to a specific statement in the paper or a documented assumption. There are no black boxes in the reasoning chain.

**Prefer conservative assumptions.** When forced to make an assumption (e.g., which library version to use, which IQR multiplier to apply), the system prefers the most commonly used default rather than the one most likely to match the paper's result. This avoids the circularity of tuning the replication to fit the target.

**Graduated fidelity.** The system distinguishes between what the paper explicitly states, what can be reliably inferred, and what must be assumed. These three tiers of confidence are preserved throughout the pipeline and reflected in the final report.

**Human in the loop for genuine blockers only.** The system is designed to handle ambiguity autonomously wherever possible and to escalate to the human only when a genuine decision or resource that the system cannot provide is needed. The set of escalation points is well-defined and minimal.

---

## Technology Context

The system is built to run on AMD cloud infrastructure, using open-weight language models (Qwen or Gemma families) as the reasoning backbone for all agents. The choice of open-weight models is deliberate: it means the system can run entirely within a controlled compute environment, with no dependency on external API calls for core reasoning, and with full visibility into the models being used.

The multi-agent architecture is implemented such that each phase can run one or more agents, with agents within a phase collaborating through structured message passing and shared artifacts. The number of agents per phase is determined by implementation, not fixed by the architecture — the phase methodology documents define what needs to be done, not how many agents do it.

---

## How to Use This Document

This document is the entry point for understanding the project. Read it first.

The six phase methodology documents — phase1 through phase6 — provide the detailed operational specification for each stage of the pipeline. When building or extending the system, those documents define what each phase must accomplish, what its inputs and outputs are, and how it should handle failures and ambiguities.

The phase documents are written as methodology — they describe what a thorough human reviewer would do at each stage. When mapping this methodology to an agent implementation, the agent's instructions, tools, and decision logic should be derived directly from the relevant phase document.

The overall design intent is: read this file to understand what we are building and why. Read the phase files to understand how to build it.
