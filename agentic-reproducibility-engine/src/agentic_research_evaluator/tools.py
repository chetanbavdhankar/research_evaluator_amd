from __future__ import annotations

import hashlib
import json
import os
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any

from .schemas import ToolCall


ARXIV_API = "http://export.arxiv.org/api/query"
CROSSREF_API = "https://api.crossref.org/works"
DOI_CSL_API = "https://doi.org"
GITHUB_API = "https://api.github.com"
HF_API = "https://huggingface.co/api"
HTTP_TIMEOUT_SECONDS = int(os.environ.get("RESEARCH_EVALUATOR_HTTP_TIMEOUT", "30"))
USER_AGENT = os.environ.get(
    "RESEARCH_EVALUATOR_USER_AGENT",
    "agentic-research-evaluator/0.1 (research audit resolver)",
)


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def parse_paper(run_id: str, paper_text: str) -> ToolCall:
    del run_id
    title = paper_text.strip().splitlines()[0].strip("# ").strip() or "Untitled paper"
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", paper_text) if part.strip()]
    claims = [
        {"claim_id": f"claim_{idx + 1}", "text": sentence[:280], "source_ref": f"paper:s{idx + 1}"}
        for idx, sentence in enumerate(sentences[:4])
    ]
    identifiers = extract_identifiers(paper_text, title)
    output = {
        "title": title,
        "document_hash": _short_hash(paper_text),
        "claims": claims,
        "sections_detected": _detect_sections(paper_text),
        "identifiers": identifiers,
        "raw_text": paper_text,
    }
    return ToolCall("parse_paper", "ok", f"Parsed {len(claims)} candidate claims.", output)


def resolve_arxiv(run_id: str, paper: dict[str, Any], *, allow_network: bool = True) -> ToolCall:
    if not allow_network:
        return _resolver_skipped("arxiv_resolver", "Network resolution disabled by run policy.")

    identifiers = paper.get("identifiers", {})
    arxiv_ids = identifiers.get("arxiv_ids", [])
    atom_error: BaseException | None = None
    try:
        if arxiv_ids:
            params = {"id_list": ",".join(arxiv_ids), "max_results": "5"}
        else:
            params = {
                "search_query": f'ti:"{paper["title"]}"',
                "max_results": "3",
                "sortBy": "relevance",
                "sortOrder": "descending",
            }
        url = f"{ARXIV_API}?{urllib.parse.urlencode(params)}"
        entries = _parse_arxiv_entries(_fetch_text(url, allow_insecure_tls=True))
    except (urllib.error.URLError, TimeoutError, ET.ParseError) as exc:
        atom_error = exc
        entries = []

    if not entries and arxiv_ids:
        fallback_errors = []
        for arxiv_id in arxiv_ids:
            try:
                html = _fetch_text(
                    f"https://arxiv.org/abs/{urllib.parse.quote(arxiv_id, safe='/')}",
                    allow_insecure_tls=True,
                )
                entries.append(_parse_arxiv_abs_page(arxiv_id, html))
            except (urllib.error.URLError, TimeoutError) as exc:
                fallback_errors.append(str(exc))
        if not entries and atom_error:
            return ToolCall(
                "arxiv_resolver",
                "failed",
                f"arxiv_resolver failed: {atom_error}",
                {"evidence": [], "errors": [str(atom_error), *fallback_errors]},
            )

    evidence = [
        {
            "evidence_id": f"{run_id}:arxiv:{idx + 1}",
            "claim_id": "paper",
            "source_type": "arxiv",
            "locator": entry["id"],
            "confidence": "verified" if arxiv_ids else "candidate",
            "title": entry["title"],
            "authors": entry["authors"],
            "published": entry.get("published"),
            "updated": entry.get("updated"),
            "doi": entry.get("doi"),
            "resolver_path": entry.get("resolver_path", "atom"),
            "links": entry.get("links", []),
        }
        for idx, entry in enumerate(entries)
    ]
    status = "ok" if evidence else "missing"
    summary = (
        f"Resolved {len(evidence)} arXiv record(s)."
        if evidence
        else "No arXiv record resolved from id or title search."
    )
    return ToolCall("arxiv_resolver", status, summary, {"evidence": evidence})


def resolve_doi(run_id: str, paper: dict[str, Any], *, allow_network: bool = True) -> ToolCall:
    if not allow_network:
        return _resolver_skipped("doi_resolver", "Network resolution disabled by run policy.")

    identifiers = paper.get("identifiers", {})
    dois = identifiers.get("dois", [])
    evidence: list[dict[str, Any]] = []
    errors: list[str] = []

    if dois:
        for doi in dois:
            record, error = _resolve_doi_by_identifier(doi)
            if record:
                evidence.append(_doi_evidence(run_id, doi, record, "verified", len(evidence) + 1))
            elif error:
                errors.append(error)
    else:
        try:
            params = {"query.title": paper["title"], "rows": "1"}
            payload = _fetch_json(f"{CROSSREF_API}?{urllib.parse.urlencode(params)}")
            items = payload.get("message", {}).get("items", [])
            if items:
                doi = items[0].get("DOI", "")
                evidence.append(_doi_evidence(run_id, doi, items[0], "candidate", 1))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append(str(exc))

    status = "ok" if evidence else ("failed" if errors else "missing")
    summary = (
        f"Resolved {len(evidence)} DOI metadata record(s)."
        if evidence
        else "No DOI metadata record resolved."
    )
    return ToolCall("doi_resolver", status, summary, {"evidence": evidence, "errors": errors})


def resolve_github(run_id: str, paper: dict[str, Any], *, allow_network: bool = True) -> ToolCall:
    if not allow_network:
        return _resolver_skipped("github_resolver", "Network resolution disabled by run policy.")

    identifiers = paper.get("identifiers", {})
    repos = identifiers.get("github_repos", [])
    evidence: list[dict[str, Any]] = []
    errors: list[str] = []

    for repo in repos:
        try:
            payload = _fetch_json(f"{GITHUB_API}/repos/{repo}", headers=_github_headers())
            evidence.append(_github_evidence(run_id, payload, "verified", len(evidence) + 1))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append(f"{repo}: {exc}")

    if not evidence:
        query = _github_search_query(paper)
        try:
            payload = _fetch_json(
                f"{GITHUB_API}/search/repositories?{urllib.parse.urlencode(query)}",
                headers=_github_headers(),
            )
            for item in payload.get("items", [])[:3]:
                evidence.append(_github_evidence(run_id, item, "candidate", len(evidence) + 1))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append(str(exc))

    status = "ok" if evidence else ("failed" if errors else "missing")
    summary = (
        f"Resolved {len(evidence)} GitHub repository record(s)."
        if evidence
        else "No GitHub repository record resolved."
    )
    return ToolCall("github_resolver", status, summary, {"evidence": evidence, "errors": errors})


def resolve_datasets(run_id: str, paper: dict[str, Any], *, allow_network: bool = True) -> ToolCall:
    if not allow_network:
        return _resolver_skipped("dataset_resolver", "Network resolution disabled by run policy.")

    identifiers = paper.get("identifiers", {})
    dataset_ids = identifiers.get("hf_datasets", [])
    arxiv_ids = identifiers.get("arxiv_ids", [])
    mentions = identifiers.get("dataset_mentions", [])
    evidence: list[dict[str, Any]] = []
    errors: list[str] = []

    for dataset_id in dataset_ids:
        try:
            payload = _fetch_json(f"{HF_API}/datasets/{urllib.parse.quote(dataset_id, safe='/')}")
            evidence.append(_hf_dataset_evidence(run_id, payload, "verified", len(evidence) + 1))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append(f"{dataset_id}: {exc}")

    for arxiv_id in arxiv_ids[:1]:
        try:
            payload = _fetch_json(f"{HF_API}/arxiv/{urllib.parse.quote(arxiv_id, safe='')}/repos")
            for item in _hf_arxiv_dataset_items(payload):
                evidence.append(_hf_dataset_evidence(run_id, item, "paper-linked", len(evidence) + 1))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append(f"hf-paper-repos:{arxiv_id}: {exc}")

    seen = {item.get("dataset_id") or item.get("locator") for item in evidence}
    for mention in mentions[:4]:
        try:
            params = {"search": mention, "limit": "3", "full": "true"}
            payload = _fetch_json(f"{HF_API}/datasets?{urllib.parse.urlencode(params)}")
            for item in payload[:3] if isinstance(payload, list) else []:
                dataset_id = item.get("id")
                if dataset_id and dataset_id not in seen:
                    evidence.append(
                        _hf_dataset_evidence(run_id, item, "candidate", len(evidence) + 1)
                    )
                    seen.add(dataset_id)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append(f"hf-search:{mention}: {exc}")

    status = "ok" if evidence else ("failed" if errors else "missing")
    summary = (
        f"Resolved {len(evidence)} dataset record(s)."
        if evidence
        else "No public dataset record resolved."
    )
    return ToolCall("dataset_resolver", status, summary, {"evidence": evidence, "errors": errors})


def build_evidence_bundle(run_id: str, resolver_calls: list[ToolCall]) -> ToolCall:
    evidence: list[dict[str, Any]] = []
    missing: list[str] = []
    resolver_status: dict[str, str] = {}
    resolver_errors: dict[str, list[str]] = {}

    for call in resolver_calls:
        resolver_status[call.tool_id] = call.status
        evidence.extend(call.output.get("evidence", []))
        errors = call.output.get("errors", [])
        if errors:
            resolver_errors[call.tool_id] = errors
        if call.status in {"missing", "failed", "skipped"}:
            missing.append(_missing_reason(call))

    output = {
        "evidence": evidence,
        "missing": missing,
        "resolver_status": resolver_status,
        "resolver_errors": resolver_errors,
    }
    return ToolCall(
        "evidence_bundle",
        "ok" if evidence else "missing",
        f"Bundled {len(evidence)} live resolver evidence record(s).",
        output,
    )


def score_reproducibility(run_id: str, paper: dict[str, Any], evidence: dict[str, Any]) -> ToolCall:
    del run_id
    sections = set(paper.get("sections_detected", []))
    evidence_items = evidence.get("evidence", [])
    source_types = {item.get("source_type") for item in evidence_items}
    missing = list(evidence.get("missing", []))

    paper_identity_verified = bool({"arxiv", "doi"} & source_types)
    repository_verified = any(
        item.get("source_type") == "github" and item.get("confidence") == "verified"
        for item in evidence_items
    )
    repository_candidates = any(item.get("source_type") == "github" for item in evidence_items)
    dataset_records = [item for item in evidence_items if item.get("source_type") == "hf_dataset"]
    dataset_verified = bool(dataset_records)
    dataset_license_verified = any(item.get("license") not in {None, "", "unknown"} for item in dataset_records)

    if not paper_identity_verified:
        missing.append("paper identity not verified by arXiv or DOI")
    if "code" in sections and not repository_verified:
        missing.append(
            "official GitHub repository not identified"
            if repository_candidates
            else "GitHub repository not found"
        )
    if "data" in sections and not dataset_verified:
        missing.append("dataset resolver found no public dataset record")
    if "data" in sections and dataset_verified and not dataset_license_verified:
        missing.append("dataset license not resolved")

    missing = _dedupe(missing)

    score = 30
    if "methods" in sections:
        score += 15
    if len(paper.get("claims", [])) >= 3:
        score += 10
    if paper_identity_verified:
        score += 20
    if "code" not in sections or repository_verified:
        score += 10
    if "data" not in sections or dataset_verified:
        score += 10
    if "data" not in sections or dataset_license_verified:
        score += 5
    score -= min(30, max(0, len(missing) - 1) * 5)
    score = max(0, min(100, score))

    output = {
        "score": score,
        "decision": "degraded" if missing or score < 85 else "pass",
        "gaps": missing,
        "rubric": {
            "methods_specificity": "methods" in sections,
            "paper_identity_verified": paper_identity_verified,
            "repository_verified": repository_verified,
            "repository_candidates": repository_candidates,
            "dataset_verified": dataset_verified,
            "dataset_license_verified": dataset_license_verified,
            "external_evidence_records": len(evidence_items),
        },
    }
    return ToolCall("score_reproducibility", "ok", f"Score: {score}/100.", output)


def plan_experiment(run_id: str, audit: dict[str, Any]) -> ToolCall:
    del run_id
    output = {
        "replication_plan": [
            "Resolve primary paper identity through arXiv and DOI metadata.",
            "Bind each dataset mention to a public source or mark it unavailable.",
            "Verify whether a repository is official, candidate-only, or absent.",
            "Run deterministic extraction and reproducibility scorecard.",
            "Generate a minimal reproduction script for the central quantitative claim.",
            "Ask verifier to block unsupported final conclusions.",
        ],
        "blocked_items": audit.get("gaps", []),
    }
    return ToolCall("experiment_planner", "ok", "Built replication plan from audit gaps.", output)


def generate_code_data_plan(run_id: str, paper: dict[str, Any]) -> ToolCall:
    del run_id
    slug = re.sub(r"[^a-z0-9]+", "_", paper["title"].lower()).strip("_")[:48] or "paper"
    output = {
        "script_name": f"fetch_{slug}.py",
        "commands": [
            "python -m agentic_research_evaluator.tools.resolve_sources --input run_manifest.json",
            "python -m agentic_research_evaluator.tools.score_reproducibility --input evidence_bundle.json",
        ],
        "sandbox_required": True,
    }
    return ToolCall("code_data_planner", "ok", "Generated structured commands for sandboxed follow-up.", output)


def extract_identifiers(text: str, title: str) -> dict[str, list[str]]:
    combined = f"{title}\n{text}"
    return {
        "arxiv_ids": _dedupe(_extract_arxiv_ids(combined)),
        "dois": _dedupe(_extract_dois(combined)),
        "github_repos": _dedupe(_extract_github_repos(combined)),
        "hf_datasets": _dedupe(_extract_hf_datasets(combined)),
        "dataset_mentions": _dedupe(_extract_dataset_mentions(combined)),
    }


def _resolve_doi_by_identifier(doi: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return _fetch_json(f"{CROSSREF_API}/{urllib.parse.quote(doi, safe='')}"), None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as crossref_error:
        try:
            payload = _fetch_json(
                f"{DOI_CSL_API}/{urllib.parse.quote(doi, safe='/')}",
                headers={"Accept": "application/vnd.citationstyles.csl+json"},
            )
            return {"message": payload}, None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as doi_error:
            return None, f"{doi}: crossref={crossref_error}; doi.org={doi_error}"


def _doi_evidence(
    run_id: str,
    doi: str,
    record: dict[str, Any],
    confidence: str,
    index: int,
) -> dict[str, Any]:
    message = record.get("message", record)
    title = message.get("title", [])
    if isinstance(title, list):
        title = title[0] if title else ""
    return {
        "evidence_id": f"{run_id}:doi:{index}",
        "claim_id": "paper",
        "source_type": "doi",
        "locator": f"https://doi.org/{doi}" if doi else message.get("URL"),
        "confidence": confidence,
        "doi": doi or message.get("DOI"),
        "title": title,
        "publisher": message.get("publisher"),
        "issued": message.get("issued"),
        "license": _first_license(message),
    }


def _github_search_query(paper: dict[str, Any]) -> dict[str, str]:
    identifiers = paper.get("identifiers", {})
    terms = identifiers.get("arxiv_ids") or [paper["title"]]
    query = f'"{terms[0]}" in:name,description,readme'
    return {"q": query, "sort": "stars", "order": "desc", "per_page": "3"}


def _github_evidence(
    run_id: str,
    payload: dict[str, Any],
    confidence: str,
    index: int,
) -> dict[str, Any]:
    license_payload = payload.get("license") or {}
    return {
        "evidence_id": f"{run_id}:github:{index}",
        "claim_id": "paper",
        "source_type": "github",
        "locator": payload.get("html_url"),
        "confidence": confidence,
        "full_name": payload.get("full_name"),
        "description": payload.get("description"),
        "stars": payload.get("stargazers_count"),
        "forks": payload.get("forks_count"),
        "updated_at": payload.get("updated_at"),
        "license": license_payload.get("spdx_id") or license_payload.get("key") or "unknown",
    }


def _hf_dataset_evidence(
    run_id: str,
    payload: dict[str, Any],
    confidence: str,
    index: int,
) -> dict[str, Any]:
    dataset_id = payload.get("id") or payload.get("name") or payload.get("repoId")
    tags = payload.get("tags") or []
    return {
        "evidence_id": f"{run_id}:dataset:{index}",
        "claim_id": "paper",
        "source_type": "hf_dataset",
        "locator": f"https://huggingface.co/datasets/{dataset_id}" if dataset_id else payload.get("url"),
        "confidence": confidence,
        "dataset_id": dataset_id,
        "downloads": payload.get("downloads"),
        "likes": payload.get("likes"),
        "license": _license_from_tags(tags),
        "tags": tags,
    }


def _fetch_json(url: str, headers: dict[str, str] | None = None) -> Any:
    request = _request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def _fetch_text(
    url: str,
    headers: dict[str, str] | None = None,
    *,
    allow_insecure_tls: bool = False,
) -> str:
    request = _request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        if not allow_insecure_tls or "CERTIFICATE_VERIFY_FAILED" not in str(exc):
            raise
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
            context=context,
        ) as response:
            return response.read().decode("utf-8")


def _request(url: str, headers: dict[str, str] | None = None) -> urllib.request.Request:
    all_headers = {"User-Agent": USER_AGENT}
    all_headers.update(headers or {})
    return urllib.request.Request(url, headers=all_headers)


def _github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _parse_arxiv_entries(xml_text: str) -> list[dict[str, Any]]:
    root = ET.fromstring(xml_text)
    atom = "{http://www.w3.org/2005/Atom}"
    arxiv = "{http://arxiv.org/schemas/atom}"
    entries = []
    for entry in root.findall(f"{atom}entry"):
        authors = [
            _text(author, f"{atom}name")
            for author in entry.findall(f"{atom}author")
            if _text(author, f"{atom}name")
        ]
        links = [
            {
                "href": link.attrib.get("href"),
                "rel": link.attrib.get("rel"),
                "type": link.attrib.get("type"),
                "title": link.attrib.get("title"),
            }
            for link in entry.findall(f"{atom}link")
        ]
        entries.append(
            {
                "id": _text(entry, f"{atom}id"),
                "title": _normalize_space(_text(entry, f"{atom}title")),
                "summary": _normalize_space(_text(entry, f"{atom}summary")),
                "published": _text(entry, f"{atom}published"),
                "updated": _text(entry, f"{atom}updated"),
                "authors": authors,
                "doi": _text(entry, f"{arxiv}doi"),
                "links": links,
            }
        )
    return entries


def _parse_arxiv_abs_page(arxiv_id: str, html: str) -> dict[str, Any]:
    title = _html_meta(html, "citation_title") or _html_title(html)
    authors = re.findall(
        r'<meta\s+name=["\']citation_author["\']\s+content=["\']([^"\']+)["\']',
        html,
        flags=re.IGNORECASE,
    )
    doi = _html_meta(html, "citation_doi")
    published = _html_meta(html, "citation_date")
    pdf_url = _html_meta(html, "citation_pdf_url")
    return {
        "id": f"https://arxiv.org/abs/{arxiv_id}",
        "title": title,
        "summary": "",
        "published": published,
        "updated": "",
        "authors": authors,
        "doi": doi,
        "resolver_path": "arxiv_abs_page",
        "links": [{"href": pdf_url, "rel": "related", "type": "application/pdf", "title": "pdf"}]
        if pdf_url
        else [],
    }


def _hf_arxiv_dataset_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        candidates = payload.get("datasets") or payload.get("dataset") or []
        if isinstance(candidates, list):
            return [item for item in candidates if isinstance(item, dict)]
        if isinstance(candidates, dict):
            return [candidates]
        repos = payload.get("repos") or payload.get("siblings") or []
    elif isinstance(payload, list):
        repos = payload
    else:
        repos = []
    return [
        item
        for item in repos
        if isinstance(item, dict) and item.get("type", item.get("repoType")) == "dataset"
    ]


def _extract_arxiv_ids(text: str) -> list[str]:
    patterns = [
        r"(?i)\barxiv\s*:\s*([a-z\-]+/\d{7}|\d{4}\.\d{4,5})(?:v\d+)?",
        r"(?i)arxiv\.org/(?:abs|pdf)/([a-z\-]+/\d{7}|\d{4}\.\d{4,5})(?:v\d+)?",
        r"(?i)\bdoi\s*:\s*10\.48550/arxiv\.([a-z\-]+/\d{7}|\d{4}\.\d{4,5})(?:v\d+)?",
    ]
    ids: list[str] = []
    for pattern in patterns:
        ids.extend(match.group(1) for match in re.finditer(pattern, text))
    return ids


def _extract_dois(text: str) -> list[str]:
    dois = []
    for match in re.finditer(r"\b10\.\d{4,9}/[^\s<>'\"]+", text, flags=re.IGNORECASE):
        dois.append(match.group(0).rstrip(".,;:)]}").lower())
    return dois


def _extract_github_repos(text: str) -> list[str]:
    repos = []
    for match in re.finditer(r"github\.com[:/]+([\w.-]+)/([\w.-]+)", text, flags=re.IGNORECASE):
        repo = match.group(2).removesuffix(".git").rstrip(".,;:)]}")
        repos.append(f"{match.group(1)}/{repo}")
    return repos


def _extract_hf_datasets(text: str) -> list[str]:
    datasets = []
    for match in re.finditer(
        r"huggingface\.co/datasets/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+|[A-Za-z0-9_.-]+)",
        text,
        flags=re.IGNORECASE,
    ):
        datasets.append(match.group(1).rstrip(".,;:)]}"))
    return datasets


def _extract_dataset_mentions(text: str) -> list[str]:
    mentions: list[str] = []
    for line in text.splitlines():
        if re.match(r"^\s*(data|datasets?|benchmarks?)\s*:", line, flags=re.IGNORECASE):
            content = line.split(":", 1)[1]
            mentions.extend(_split_mentions(content))
    if not mentions:
        for phrase in re.findall(
            r"\b([A-Z][A-Za-z0-9-]*(?:\s+\d{4})?(?:\s+[A-Z][A-Za-z0-9-]*){0,3}\s+(?:dataset|corpus|benchmark|translation task)s?)\b",
            text,
        ):
            mentions.append(phrase)
    return [mention for mention in mentions if len(mention) >= 3][:8]


def _split_mentions(content: str) -> list[str]:
    pieces = re.split(r",|;|\bplus\b|\band\b", content)
    cleaned = []
    for piece in pieces:
        value = re.sub(r"\s+", " ", piece).strip(" .")
        if value and not value.lower().startswith(("the ", "a ")):
            cleaned.append(value)
    return cleaned


def _detect_sections(text: str) -> list[str]:
    lower = text.lower()
    candidates = {
        "methods": ["method", "approach", "estimator", "protocol", "architecture"],
        "data": ["data", "dataset", "corpus", "sample", "benchmark", "wmt"],
        "code": ["github", "repository", "software", "source code", "code:"],
        "results": ["result", "finding", "benchmark", "score", "bleu"],
    }
    return [name for name, needles in candidates.items() if any(needle in lower for needle in needles)]


def _missing_reason(call: ToolCall) -> str:
    if call.tool_id == "arxiv_resolver":
        return "arXiv resolver returned no verified paper record"
    if call.tool_id == "doi_resolver":
        return "DOI resolver returned no metadata record"
    if call.tool_id == "github_resolver":
        return "GitHub resolver returned no repository record"
    if call.tool_id == "dataset_resolver":
        return "dataset resolver returned no public dataset record"
    return f"{call.tool_id} returned no evidence"


def _resolver_skipped(tool_id: str, summary: str) -> ToolCall:
    return ToolCall(tool_id, "skipped", summary, {"evidence": [], "errors": [summary]})


def _resolver_failed(tool_id: str, exc: BaseException) -> ToolCall:
    return ToolCall(tool_id, "failed", f"{tool_id} failed: {exc}", {"evidence": [], "errors": [str(exc)]})


def _first_license(message: dict[str, Any]) -> str:
    licenses = message.get("license") or []
    if licenses and isinstance(licenses, list):
        return licenses[0].get("URL") or licenses[0].get("content-version") or "unknown"
    return "unknown"


def _license_from_tags(tags: list[str]) -> str:
    for tag in tags:
        if isinstance(tag, str) and tag.startswith("license:"):
            return tag.split(":", 1)[1]
    return "unknown"


def _text(element: ET.Element, tag: str) -> str:
    child = element.find(tag)
    return child.text.strip() if child is not None and child.text else ""


def _normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _html_meta(html: str, name: str) -> str:
    match = re.search(
        rf'<meta\s+name=["\']{re.escape(name)}["\']\s+content=["\']([^"\']+)["\']',
        html,
        flags=re.IGNORECASE,
    )
    return _normalize_space(match.group(1)) if match else ""


def _html_title(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    title = re.sub(r"^\[[^\]]+\]\s*", "", match.group(1))
    return _normalize_space(title)


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    out = []
    for value in values:
        normalized = value.strip()
        key = normalized.lower()
        if normalized and key not in seen:
            out.append(normalized)
            seen.add(key)
    return out
