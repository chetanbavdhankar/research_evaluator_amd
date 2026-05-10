# Video Presentation Script

Target length: 4 minutes 30 seconds. The lablab guidance says video presentations should be no more than 5 minutes.

## 0:00-0:20 — Introduction

Hi, I am presenting the Agentic Reproducibility Engine, built for the AMD Developer Hackathon Track 1: AI Agents and Agentic Workflows.

The problem is simple: research reproducibility audits are slow, manual, and often hide uncertainty. Critical evidence is scattered across papers, arXiv, DOI metadata, GitHub repositories, datasets, and implementation notes.

## 0:20-0:55 — Product Thesis

This product turns that process into a visible multi-agent workflow. A user submits a paper, chooses an autonomy level, and watches specialized agents plan the audit, read the paper, retrieve evidence, score reproducibility, plan experiments, generate code/data follow-up commands, critique unsupported assumptions, and produce a final report.

The important design choice is fail-closed verification: if evidence cannot be verified, the system records the gap and degrades the decision instead of inventing placeholder evidence.

## 0:55-1:30 — Architecture

The public frontend is a static Hugging Face Space. The backend runs on AMD Developer Cloud. The model target is `Qwen/Qwen3.5-27B` served through vLLM on ROCm, with the backend talking to it through an OpenAI-compatible endpoint.

The tools include paper parsing, arXiv resolution, DOI resolution, GitHub lookup, dataset resolution, reproducibility scoring, experiment planning, code/data planning, verification, and report generation.

## 1:30-3:15 — Live Demo

Here is the dashboard. The autonomy slider controls how much the system can do. At lower levels, it can analyze locally or avoid network/code planning. At higher levels, it can use live evidence tools and verifier repair.

I will start an audit on a research paper with known arXiv, DOI, GitHub, and dataset references.

As the run starts, the UI streams the trace. You can see planning, paper understanding, tool requests, resolver outcomes, scoring, code/data planning, and verifier critique. This is the difference between an agentic system and a final-answer chatbot: the work is inspectable.

Now the report is generated. It includes the score, decision, evidence records, unresolved gaps, replication plan, code/data follow-up, verifier decision, and trace summary.

## 3:15-3:55 — Evals And Trust

The repo includes an eval harness inspired by Software 3.0 principles: prompts, context, traces, tool requests, and reports are treated as versioned software artifacts.

The evals check whether each agent did its job and whether the overall audit decision is justified. They also explicitly ban placeholder evidence.

## 3:55-4:20 — Business Value

The target users are research labs, ML teams, funders, reviewers, benchmark maintainers, and enterprise AI teams who need to decide whether a paper is safe to adopt or worth replicating.

The product does not promise magic reproduction. It gives teams an audit-ready first pass with provenance, uncertainty, and concrete next steps.

## 4:20-4:30 — Close

The Agentic Reproducibility Engine is an AMD-hosted multi-agent evaluator powered by open Hugging Face models. It makes reproducibility audits visible, verifiable, and ready for follow-up.
