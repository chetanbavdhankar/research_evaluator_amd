# Plain-Language Explainer

## One-Sentence Version

SpecCurve is an AMD-powered research stress-test tool that asks: "Does this published result still hold if we analyze the data in many reasonable ways?"

## Simple Team Explanation

Many research results depend on analysis choices.

For example:

- Which participants are excluded?
- Which covariates are included?
- Which model is used?
- Which transformation is applied?
- Which statistical threshold is reported?

Each individual choice may be defensible. But different defensible choices can produce different conclusions.

Today, checking this manually is slow. A researcher may need to write many scripts, rerun models, compare outputs, and explain which choices matter. SpecCurve turns that into an interactive workflow:

1. Choose one public dataset and one published claim.
2. Define a space of defensible analytic choices.
3. Ask agents to propose additional valid specifications.
4. Use a verifier agent to reject invalid or unfair specifications.
5. Run the valid specifications in parallel on AMD MI300X.
6. Show a robustness surface that reveals whether the claim is stable or fragile.

The output is not a single yes/no verdict. It is a map:

```text
Here are the analysis choices under which the effect appears.
Here are the choices under which it weakens or disappears.
Here are the choices the verifier rejected as invalid.
Here is the most honest summary of the claim's robustness.
```

## Judge-Friendly Explanation

SpecCurve uses agentic AI and AMD MI300X together.

The agents reason about the research workflow:

- A proposer agent suggests possible statistical specifications.
- A verifier agent rejects invalid or misleading specifications.
- An explainer agent turns the results into a clear research summary.

The MI300X does the heavy numerical work:

- Batched regressions.
- Permutation tests.
- Bootstrap resampling.
- Thousands of model variants and resamples.

The visual result is a robustness surface. Judges can immediately see whether a scientific claim is stable across many defensible choices or depends on a narrow path through the data.

## What Makes It More Than a Chatbot

The agents do not just write prose. They create and criticize structured analysis plans. The deterministic statistics engine executes those plans. The result is traceable and auditable.

Without the agents, the system is just a batch statistics runner.

Without the GPU, the system is too slow to make the robustness surface interactive.

Without the verifier, the system can generate misleading specifications.

All three pieces are load-bearing.

## The Core Demo Moment

The demo starts with one published claim:

```text
This study reports an effect in a public dataset.
```

Then SpecCurve runs:

```text
200 defensible analytic specifications
```

The screen fills with points on a robustness surface. Some points support the claim. Some weaken it. Some are rejected before execution because they violate the rules.

The punchline:

```text
Instead of asking whether one analysis is convincing, SpecCurve shows the whole decision landscape.
```

## What To Say If Asked "Is This Replication?"

No. Replication means collecting or using independent new data.

SpecCurve is a specification robustness test. It asks whether the original conclusion survives reasonable choices within the available data.

That distinction is important and should be stated clearly.

## What To Say If Asked "What Is Original?"

Specification curves already exist as a statistical idea. The originality here is the combination:

- Agent-generated specifications.
- Verifier agent for invalid analysis plans.
- GPU-scale batched execution.
- Interactive robustness surface.
- Reproducible provenance for every analytic choice.

The product is not claiming to invent specification curves. It makes them faster, more interactive, and easier to audit.

## Name And Tagline Options

Recommended name:

```text
SpecCurve
```

Recommended tagline:

```text
GPU-scale robustness checks for research claims.
```

Alternative taglines:

```text
Stress-test a published result in minutes.
```

```text
See whether a finding survives the analysis maze.
```

```text
From one p-value to a full robustness surface.
```

