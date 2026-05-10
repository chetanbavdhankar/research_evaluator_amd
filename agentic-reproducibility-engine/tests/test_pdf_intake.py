from fastapi.testclient import TestClient

from agentic_research_evaluator import api as api_module
from agentic_research_evaluator.pdf_intake import extract_pdf_paper
from agentic_research_evaluator.tools import parse_paper


PDF_LINES = [
    "Denoising Diffusion Probabilistic Models",
    "arXiv: 2006.11239",
    "DOI: 10.48550/arXiv.2006.11239",
    "Code: https://github.com/hojonathanho/diffusion",
    "Data: CIFAR-10, LSUN, CelebA-HQ",
    "The paper evaluates diffusion models on image generation benchmarks.",
]


def test_extract_pdf_paper_returns_resolver_targets():
    result = extract_pdf_paper(
        _pdf_bytes(PDF_LINES, title="Denoising Diffusion Probabilistic Models"),
        filename="paper.pdf",
        content_type="application/pdf",
    )

    assert result["title"] == "Denoising Diffusion Probabilistic Models"
    assert result["reference"] == "2006.11239"
    assert result["code_repositories"] == ["hojonathanho/diffusion"]
    assert result["datasets"] == ["CIFAR-10", "LSUN", "CelebA-HQ"]
    assert result["pages_read"] == 1

    identifiers = parse_paper("run_pdf", result["paper_text"]).output["identifiers"]
    assert identifiers["arxiv_ids"] == ["2006.11239"]
    assert identifiers["dois"] == ["10.48550/arxiv.2006.11239"]
    assert identifiers["github_repos"] == ["hojonathanho/diffusion"]
    assert identifiers["dataset_mentions"] == ["CIFAR-10", "LSUN", "CelebA-HQ"]


def test_extract_endpoint_accepts_pdf_upload():
    client = TestClient(api_module.app)

    response = client.post(
        "/papers/extract",
        files={
            "file": (
                "paper.pdf",
                _pdf_bytes(PDF_LINES, title="Denoising Diffusion Probabilistic Models"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reference"] == "2006.11239"
    assert payload["identifiers"]["github_repos"] == ["hojonathanho/diffusion"]


def test_extract_endpoint_rejects_non_pdf_upload():
    client = TestClient(api_module.app)

    response = client.post(
        "/papers/extract",
        files={"file": ("paper.txt", b"not a pdf", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Upload must be a PDF file."


def test_extract_endpoint_rejects_unreadable_pdf():
    client = TestClient(api_module.app)

    response = client.post(
        "/papers/extract",
        files={
            "file": (
                "paper.pdf",
                b"%PDF-1.4\nnot a complete document",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unreadable PDF upload."


def test_extract_endpoint_rejects_empty_extraction():
    client = TestClient(api_module.app)

    response = client.post(
        "/papers/extract",
        files={"file": ("paper.pdf", _pdf_bytes([]), "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "PDF contains no extractable text."


def test_extract_endpoint_rejects_oversized_pdf(monkeypatch):
    client = TestClient(api_module.app)
    monkeypatch.setattr(api_module, "PDF_MAX_BYTES", 12)

    response = client.post(
        "/papers/extract",
        files={"file": ("paper.pdf", b"%PDF-" + b"x" * 32, "application/pdf")},
    )

    assert response.status_code == 413


def _pdf_bytes(lines: list[str], *, title: str | None = None) -> bytes:
    content_lines = ["BT", "/F1 12 Tf", "72 720 Td"]
    for index, line in enumerate(lines):
        if index:
            content_lines.append("0 -16 Td")
        content_lines.append(f"({_pdf_escape(line)}) Tj")
    content_lines.append("ET")
    content = "\n".join(content_lines).encode("latin-1")
    stream = b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n"
    stream += content + b"\nendstream"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> /ProcSet [/PDF /Text] >> "
            b"/Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        stream,
    ]
    trailer_info = b""
    if title:
        objects.append(f"<< /Title ({_pdf_escape(title)}) >>".encode("latin-1"))
        trailer_info = b" /Info 6 0 R"
    return _pdf_document(objects, trailer_info=trailer_info)


def _pdf_document(objects: list[bytes], *, trailer_info: bytes = b"") -> bytes:
    chunks = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
    offsets = []
    for number, obj in enumerate(objects, start=1):
        offsets.append(sum(len(chunk) for chunk in chunks))
        chunks.append(f"{number} 0 obj\n".encode("ascii") + obj + b"\nendobj\n")
    xref_offset = sum(len(chunk) for chunk in chunks)
    xref = [
        f"xref\n0 {len(objects) + 1}\n".encode("ascii"),
        b"0000000000 65535 f \n",
    ]
    xref.extend(f"{offset:010d} 00000 n \n".encode("ascii") for offset in offsets)
    chunks.extend(
        [
            *xref,
            b"trailer\n<< /Size "
            + str(len(objects) + 1).encode("ascii")
            + b" /Root 1 0 R"
            + trailer_info
            + b" >>\n",
            f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii"),
        ]
    )
    return b"".join(chunks)


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
