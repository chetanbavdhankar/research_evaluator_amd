# Build In Public And AMD Feedback

The AMD hackathon page includes an extra challenge for build-in-public work. It asks for at least two technical updates on social media, meaningful AMD/ROCm/cloud feedback, and an open-source project or technical walkthrough.

Use these as drafts. Replace bracketed placeholders before posting.

## Post 1 — Architecture Update

```text
Building for the AMD Developer Hackathon:

We pivoted from a static reproducibility demo to an actual agentic system:

Hugging Face Space UI
-> AMD Developer Cloud FastAPI backend
-> multi-agent audit runtime
-> vLLM serving Qwen/Qwen3.5-27B on ROCm
-> live arXiv/DOI/GitHub/dataset tools

The key UX choice: judges can see the agent trace, tool calls, verifier objections, and final report provenance.

@lablabai @AIatAMD
```

## Post 2 — Verification Update

```text
Second AMD hackathon build update:

The Agentic Reproducibility Engine now has an eval harness for the agents themselves.

It checks:
- separate agent prompts/context
- model artifacts
- tool request validation
- resolver coverage
- verifier objections
- fail-closed decisions when evidence is missing
- no placeholder evidence

This turns the demo into a testable agentic workflow, not just a nice UI.

@lablabai @AIatAMD
```

## AMD/ROCm Feedback Draft

```text
AMD Developer Cloud and ROCm made the target architecture practical because vLLM can expose Hugging Face models through an OpenAI-compatible endpoint while the app remains framework-agnostic.

The main developer friction is version matching: ROCm version, Python version, vLLM wheel/container, and model context length need a clear compatibility matrix. For agent builders, the ideal path would be a blessed MI300X image with vLLM, Hugging Face cache setup, and a health-check command already included.

What worked well:
- AMD GPU memory makes long-context research workflows realistic.
- The OpenAI-compatible vLLM endpoint keeps app code portable.
- Hugging Face Spaces pair naturally with an AMD-hosted backend.

What would improve the experience:
- one canonical ROCm/vLLM startup template for common open models
- first-party examples for Qwen tool calling on AMD
- an official readiness script for GPU, ROCm, vLLM, and model endpoint checks
```

## Technical Walkthrough Outline

Title:

```text
Building an AMD-hosted multi-agent reproducibility evaluator with Qwen, vLLM, and Hugging Face Spaces
```

Sections:

1. Why reproducibility auditing needs agents.
2. Why the frontend is static HTML and the backend runs on AMD.
3. How vLLM turns Qwen into an OpenAI-compatible endpoint.
4. How the agents coordinate.
5. How evidence resolvers fail closed.
6. How the eval harness grades agent behavior.
7. What changed after testing on AMD.
