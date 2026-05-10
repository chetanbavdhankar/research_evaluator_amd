from __future__ import annotations

import io
import os
import re
from typing import Any

from .tools import extract_identifiers


PDF_MAX_BYTES = int(
    os.environ.get("RESEARCH_EVALUATOR_PDF_MAX_BYTES", str(20 * 1024 * 1024))
)
PDF_CONTENT_TYPES = {"application/pdf", "application/x-pdf"}


class PdfIntakeError(ValueError):
    """Raised when an uploaded PDF cannot be converted into paper intake text."""


def extract_pdf_paper(
    data: bytes,
    *,
    filename: str | None = None,
    content_type: str | None = None,
    max_bytes: int = PDF_MAX_BYTES,
) -> dict[str, Any]:
    _validate_pdf_upload(data, filename=filename, content_type=content_type, max_bytes=max_bytes)

    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - dependency contract failure
        raise RuntimeError(
            "Install PDF intake dependencies with `pip install -e .[api]`."
        ) from exc

    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception as exc:
        raise PdfIntakeError("Unreadable PDF upload.") from exc

    if reader.is_encrypted:
        raise PdfIntakeError("Encrypted PDFs are not supported.")

    warnings: list[str] = []
    page_text: list[str] = []
    blank_pages = 0

    try:
        pages = list(reader.pages)
    except Exception as exc:
        raise PdfIntakeError("Unreadable PDF page tree.") from exc

    for page in pages:
        try:
            extracted = page.extract_text() or ""
        except Exception:
            extracted = ""
        if extracted.strip():
            page_text.append(extracted)
        else:
            blank_pages += 1

    raw_text = "\n\n".join(page_text)
    normalized_text = _normalize_pdf_text(raw_text)
    if not normalized_text:
        raise PdfIntakeError("PDF contains no extractable text.")

    if blank_pages:
        warnings.append(f"{blank_pages} page(s) had no extractable text.")

    title = _metadata_title(reader.metadata) or _title_from_text(normalized_text)
    identifiers = extract_identifiers(normalized_text, title)
    reference = _preferred_reference(normalized_text, identifiers, title)
    datasets = _dedupe([*identifiers["hf_datasets"], *identifiers["dataset_mentions"]])
    paper_text = _build_paper_text(
        title=title,
        reference=reference,
        identifiers=identifiers,
        datasets=datasets,
        extracted_text=normalized_text,
    )

    return {
        "paper_text": paper_text,
        "title": title,
        "reference": reference,
        "identifiers": identifiers,
        "code_repositories": identifiers["github_repos"],
        "datasets": datasets,
        "pages_read": len(pages),
        "warnings": warnings,
    }


def _validate_pdf_upload(
    data: bytes,
    *,
    filename: str | None,
    content_type: str | None,
    max_bytes: int,
) -> None:
    if not data:
        raise PdfIntakeError("Uploaded PDF is empty.")
    if len(data) > max_bytes:
        raise PdfIntakeError(
            f"Uploaded PDF exceeds the {max_bytes // (1024 * 1024)} MB limit."
        )

    suffix_ok = bool(filename and filename.lower().endswith(".pdf"))
    type_ok = bool(content_type and content_type.lower() in PDF_CONTENT_TYPES)
    if not suffix_ok and not type_ok:
        raise PdfIntakeError("Upload must be a PDF file.")
    if not data.lstrip().startswith(b"%PDF-"):
        raise PdfIntakeError("Upload must be a valid PDF file.")


def _normalize_pdf_text(text: str) -> str:
    text = text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    compact: list[str] = []
    last_blank = False
    for line in lines:
        if line:
            compact.append(line)
            last_blank = False
        elif not last_blank:
            compact.append("")
            last_blank = True
    return "\n".join(compact).strip()


def _metadata_title(metadata: Any) -> str:
    title = str(getattr(metadata, "title", "") or "").strip()
    if not title or title.lower() in {"untitled", "none"}:
        return ""
    return _clean_title(title)


def _title_from_text(text: str) -> str:
    for line in text.splitlines():
        candidate = _clean_title(line)
        if not candidate:
            continue
        if re.match(r"(?i)^(arxiv|doi|code|data|dataset|reference)\s*:", candidate):
            continue
        if len(candidate) <= 180:
            return candidate
    return "Untitled paper"


def _clean_title(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" #\t")


def _preferred_reference(text: str, identifiers: dict[str, list[str]], title: str) -> str:
    if identifiers["arxiv_ids"]:
        return identifiers["arxiv_ids"][0]
    if identifiers["dois"]:
        return identifiers["dois"][0]
    urls = re.findall(r"https?://[^\s<>'\"]+", text)
    if urls:
        return urls[0].rstrip(".,;:)]}")
    return title


def _build_paper_text(
    *,
    title: str,
    reference: str,
    identifiers: dict[str, list[str]],
    datasets: list[str],
    extracted_text: str,
) -> str:
    header = [f"# {title}", f"Reference: {reference}"]
    if identifiers["arxiv_ids"]:
        header.append(f"arXiv: {identifiers['arxiv_ids'][0]}")
    if identifiers["dois"]:
        header.append(f"DOI: {identifiers['dois'][0]}")
    if identifiers["github_repos"]:
        header.append(
            "Code: "
            + ", ".join(f"https://github.com/{repo}" for repo in identifiers["github_repos"])
        )
    if datasets:
        header.append("Data: " + ", ".join(datasets))
    return "\n".join(header) + "\n\n--- Extracted PDF Text ---\n" + extracted_text


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        normalized = value.strip()
        key = normalized.lower()
        if normalized and key not in seen:
            seen.add(key)
            result.append(normalized)
    return result
