# Feature Contracts

Each feature is a contract between the wiki, LLM agents, deterministic code, demo, and judging criteria. Do not implement a feature until its acceptance criteria and failure cases are clear.

## F01 - Paper And Dataset Card

| Field | Contract |
|---|---|
| Purpose | Show exactly what public paper, dataset, and target claim are being analyzed. |
| Inputs | Paper title/authors/year, DOI or URL, dataset name/source/license, target claim, outcome, predictor, expected direction. |
| Outputs | Visible paper/dataset/claim panel plus machine-readable metadata. |
| User sees | One sentence claim, citation, dataset source, local freeze status, limitations. |
| LLM responsibility | Draft plain-language claim explanation from approved metadata only. |
| Deterministic code responsibility | Load metadata, validate required fields, show source/license/freeze status. |
| Acceptance criteria | Claim is one sentence; source is visible; dataset is public; local copy status is clear; no invented citation. |
| Failure cases | Vague claim, missing license, live-only data fetch, claim broader than dataset. |
| Demo proof | First screen shows paper, dataset, and claim in under 10 seconds. |
| Judging value | Presentation, Business Value. |

## F02 - Baseline Analysis

| Field | Contract |
|---|---|
| Purpose | Establish a deterministic reference before robustness testing. |
| Inputs | Processed dataset, baseline specification, reference result if available. |
| Outputs | Effect size, uncertainty, p-value or statistic, sample size, runtime, baseline JSON. |
| User sees | Baseline result and marker on robustness surface. |
| LLM responsibility | Explain baseline assumptions and documented deviations. |
| Deterministic code responsibility | Compute baseline, save outputs, enforce stable seeds where relevant. |
| Acceptance criteria | Runs deterministically; result can be explained; mismatch with paper is documented; output saved. |
| Failure cases | Cannot reproduce/approximate reference, unstable result, undocumented preprocessing. |
| Demo proof | Baseline appears before generated specs. |
| Judging value | Presentation, credibility, Business Value. |

## F03 - Specification Generator

| Field | Contract |
|---|---|
| Purpose | Create defensible variants of the target analysis. |
| Inputs | Dataset schema, target claim, allowed dimensions, forbidden variables, seed policy. |
| Outputs | JSON specification list with rationale and provenance. |
| User sees | Candidate count, approved/rejected counts after verification, spec detail view. |
| LLM responsibility | Suggest additional specs inside allowed dimensions and explain rationale. |
| Deterministic code responsibility | Generate rule-based grid, validate schema, deduplicate, cap scope. |
| Acceptance criteria | At least 50 valid specs for early MVP; path to 200+ final specs; no invented columns; claim unchanged. |
| Failure cases | Random combinations with no rationale, prose-only specs, invalid columns, hidden claim change. |
| Demo proof | Show one generated spec and why it is defensible. |
| Judging value | Originality, Application of Technology. |

## F04 - Verifier Agent

| Field | Contract |
|---|---|
| Purpose | Reject invalid or misleading analysis plans before execution. |
| Inputs | Spec JSON, dataset schema, target claim, verifier rules. |
| Outputs | Strict JSON status, rule hits, reasons, severity, suggested repair optional. |
| User sees | Approved/rejected counts and one rejected spec with reason. |
| LLM responsibility | Explain ambiguous rejections in plain language; never override hard rules. |
| Deterministic code responsibility | Enforce hard checks: missing columns, outcome leakage, claim change, invalid model, undocumented exclusion, small sample. |
| Acceptance criteria | Rejects at least three seeded invalid specs; returns strict JSON; rejected specs never reach GPU batch. |
| Failure cases | Approves outcome leakage, vague reasons, non-JSON response, false authority over statistics. |
| Demo proof | Live or replayed rejection of an intentionally bad spec. |
| Judging value | Originality, Presentation. |

## F05 - GPU Statistics Engine

| Field | Contract |
|---|---|
| Purpose | Execute approved specifications as a comparable CPU/GPU batch workload. |
| Inputs | Approved spec list, processed tensors, resampling settings, device config. |
| Outputs | Result table, runtime, throughput, device metadata, tolerance check, benchmark JSON. |
| User sees | Specs executed, run status, device, backend, runtime, throughput. |
| LLM responsibility | None for computation. May summarize logs after deterministic outputs exist. |
| Deterministic code responsibility | Run batched regressions/bootstrap/permutation/spec sweeps, log all results, detect CPU fallback. |
| Acceptance criteria | Uses PyTorch ROCm on MI300X; comparable CPU path exists; numerical outputs match within tolerance; logs speedup. |
| Failure cases | CPU fallback, unfair benchmark, manually edited results, missing hardware log. |
| Demo proof | AMD proof panel shows real hardware/run metadata. |
| Judging value | Application of Technology. |

## F06 - Robustness Surface

| Field | Contract |
|---|---|
| Purpose | Make result stability or sensitivity visible. |
| Inputs | Result table, baseline result, spec metadata, verifier decisions. |
| Outputs | Plot plus summary counters and selected sensitivity drivers. |
| User sees | Effect size, p-value or confidence, spec family, baseline marker, rejected-spec summary. |
| LLM responsibility | Explain visual pattern after deterministic summary is computed. |
| Deterministic code responsibility | Render data faithfully, compute cluster labels/counters, preserve provenance links. |
| Acceptance criteria | Judge can understand in 30 seconds; baseline highlighted; approved/rejected states visible; point details inspectable. |
| Failure cases | Flat table only, misleading axes, hidden baseline, visual contradicts summary. |
| Demo proof | Surface changes interpretation of baseline claim. |
| Judging value | Presentation, Originality. |

## F07 - Explanation Panel

| Field | Contract |
|---|---|
| Purpose | Summarize results without overclaiming. |
| Inputs | Computed result summary, sensitivity drivers, limitations, forbidden wording list. |
| Outputs | Plain-English conclusion with limitations. |
| User sees | Robust, fragile, mixed, or inconclusive under the tested specification space. |
| LLM responsibility | Produce cautious explanation from computed fields only. |
| Deterministic code responsibility | Provide result labels, counts, and guardrail flags. |
| Acceptance criteria | Does not say replication; does not prove truth/falsehood; states limits and main sensitivity driver. |
| Failure cases | Unsupported causal claim, certainty language, omitted limitation. |
| Demo proof | Final 10-second conclusion can be read aloud safely. |
| Judging value | Presentation, trust. |

## F08 - Exportable Robustness Report

| Field | Contract |
|---|---|
| Purpose | Turn the demo into a user-valued artifact. |
| Inputs | Metadata, baseline JSON, spec log, verifier log, results, benchmark log, conclusion. |
| Outputs | Markdown or JSON report for MVP; PDF optional later. |
| User sees | Downloadable or visible report with provenance and limitations. |
| LLM responsibility | Draft report prose from approved fields and cite limitations. |
| Deterministic code responsibility | Assemble report, include hashes/paths/timestamps, prevent missing sections. |
| Acceptance criteria | Includes claim, dataset, spec counts, rejected specs, benchmark method, result summary, limitations. |
| Failure cases | Report omits benchmark method, invents citations, lacks provenance, overclaims. |
| Demo proof | Show report preview or generated Markdown. |
| Judging value | Business Value, Presentation. |

## F09 - AMD Proof Panel

| Field | Contract |
|---|---|
| Purpose | Make MI300X visibly load-bearing. |
| Inputs | Hardware log, ROCm/PyTorch HIP status, CPU/GPU runtimes, warmup policy, speedup formula, tolerance result. |
| Outputs | UI panel plus benchmark artifact. |
| User sees | Device, ROCm/HIP, specs/resamples, CPU runtime, GPU runtime, speedup, log link. |
| LLM responsibility | Explain what the benchmark means only after logs exist. |
| Deterministic code responsibility | Capture hardware/runtime/tolerance data and block unsupported display states. |
| Acceptance criteria | Same workload on CPU/GPU; warmup policy stated; no hand-edited numbers; speedup computed from logged runtimes. |
| Failure cases | Decorative AMD logo, fake numbers, incomparable workloads, no tolerance check. |
| Demo proof | 30-second AMD moment in `11-demo-contract.md`. |
| Judging value | Application of Technology. |
