from __future__ import annotations

from pathlib import Path
from typing import Any

from .analysis import estimate_specs
from .artifacts import stable_hash, utc_now, write_json, write_text
from .baseline import run_baseline
from .data import (
    LALONDE_COLUMNS,
    fetch_rdatasets_lalonde,
    fetch_nber_lalonde,
    generate_demo_lalonde_fixture,
    load_lalonde_csv,
    persist_dataset,
)
from .report import render_report
from .specs import generate_spec_grid, invalid_spec_fixtures
from .surface import render_surface_svg, summarize_surface
from .verifier import verify_specs


def run_pipeline(
    artifact_dir: Path,
    source: str = "demo",
    csv_path: Path | None = None,
    allow_network: bool = False,
    max_specs: int | None = 240,
) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    data_dir = artifact_dir / "data"

    rows, dataset_id, source_label, evidence_status, warnings, source_files = _load_rows(
        source=source,
        csv_path=csv_path,
        allow_network=allow_network,
        data_dir=data_dir,
    )
    dataset_path = data_dir / "dataset.csv"
    dataset_artifact = persist_dataset(dataset_path, rows)
    dataset_card = {
        "dataset_id": dataset_id,
        "source": source_label,
        "evidence_status": evidence_status,
        "row_count": dataset_artifact["row_count"],
        "columns": LALONDE_COLUMNS,
        "dataset_hash": dataset_artifact["dataset_hash"],
        "generated_at": utc_now(),
        "warnings": warnings,
        "source_files": source_files,
    }

    specs = [spec.to_dict() for spec in generate_spec_grid(max_specs=max_specs)]
    invalid_fixtures = invalid_spec_fixtures()
    verification = verify_specs(specs + invalid_fixtures, set(LALONDE_COLUMNS))
    approved_specs = verification["approved"]
    rejected_specs = verification["rejected"]
    spec_batch_id = stable_hash([spec["spec_id"] for spec in approved_specs])[:16]

    baseline = run_baseline(rows)
    results = estimate_specs(rows, approved_specs)
    surface_summary = summarize_surface(results)
    surface_svg = render_surface_svg(results)
    report = render_report(dataset_card, surface_summary, approved_specs, rejected_specs, baseline=baseline)

    write_json(artifact_dir / "dataset-card.json", dataset_card)
    write_json(artifact_dir / "baseline.json", baseline)
    write_json(artifact_dir / "specs-approved.json", approved_specs)
    write_json(artifact_dir / "specs-rejected.json", rejected_specs)
    write_json(artifact_dir / "result-table.json", results)
    write_json(artifact_dir / "robustness-surface.json", surface_summary)
    write_json(
        artifact_dir / "run-manifest.json",
        {
            "run_id": f"speccurve-l0-{utc_now()}",
            "dataset_hash": dataset_card["dataset_hash"],
            "spec_batch_id": spec_batch_id,
            "approved_spec_count": len(approved_specs),
            "rejected_spec_count": len(rejected_specs),
            "result_count": len(results),
            "generated_at": utc_now(),
            "artifacts": [
                "dataset-card.json",
                "baseline.json",
                "specs-approved.json",
                "specs-rejected.json",
                "result-table.json",
                "robustness-surface.json",
                "surface.svg",
                "report.md",
            ],
        },
    )
    write_text(artifact_dir / "surface.svg", surface_svg)
    write_text(artifact_dir / "report.md", report)

    return {
        "dataset_card": dataset_card,
        "baseline": baseline,
        "approved_specs": approved_specs,
        "rejected_specs": rejected_specs,
        "results": results,
        "surface_summary": surface_summary,
        "surface_svg": surface_svg,
        "report": report,
        "artifact_dir": str(artifact_dir),
        "spec_batch_id": spec_batch_id,
    }


def _load_rows(
    source: str,
    csv_path: Path | None,
    allow_network: bool,
    data_dir: Path,
) -> tuple[list[dict[str, float]], str, str, str, list[str], list[dict[str, str]]]:
    if source == "csv":
        if csv_path is None:
            raise ValueError("--csv-path is required when source=csv")
        return (
            load_lalonde_csv(csv_path),
            "user-provided-lalonde-csv",
            str(csv_path),
            "user_provided_unverified",
            [
                "User-provided CSV must be matched to a public license/citation before submission.",
                "This run does not by itself close the final dataset gate.",
            ],
            [],
        )

    if source == "rdatasets":
        if not allow_network:
            raise ValueError("source=rdatasets requires --allow-network")
        raw_path = data_dir / "rdatasets-lalonde.csv"
        return (
            fetch_rdatasets_lalonde(raw_path),
            "rdatasets-matchit-lalonde",
            "Rdatasets MatchIt lalonde mirror",
            "public_fallback_not_final_extended_psid",
            [
                "This is a public LaLonde package fallback, not the locked NSW extended PSID-1 dataset.",
                "Use it for pipeline validation only until the final dataset decision record is filled.",
            ],
            [],
        )

    if source == "nber-dw":
        if not allow_network:
            raise ValueError("source=nber-dw requires --allow-network")
        rows, raw_files = fetch_nber_lalonde(data_dir / "raw-nber-dw", "dw-experimental")
        return (
            rows,
            "nber-dehejia-wahba-nsw-dw-experimental",
            "NBER Dehejia-Wahba NSW treated plus NSW control text files",
            "frozen_nber_source_experimental_control",
            [
                "NBER states these data are distributed for attributable non-commercial use.",
                "Cite Dehejia and Wahba 1999, Dehejia and Wahba 2002, and LaLonde 1986.",
                "Raw source files frozen in artifacts/data/raw-nber-dw with SHA-256 hashes.",
            ],
            raw_files,
        )

    if source == "nber-psid":
        if not allow_network:
            raise ValueError("source=nber-psid requires --allow-network")
        rows, raw_files = fetch_nber_lalonde(data_dir / "raw-nber-psid", "dw-psid1")
        return (
            rows,
            "nber-dehejia-wahba-nsw-treated-psid1-controls",
            "NBER Dehejia-Wahba NSW treated sample plus PSID controls",
            "frozen_nber_source_psid1_controls",
            [
                "NBER states these data are distributed for attributable non-commercial use.",
                "Cite Dehejia and Wahba 1999, Dehejia and Wahba 2002, and LaLonde 1986.",
                "Raw source files frozen in artifacts/data/raw-nber-psid with SHA-256 hashes.",
            ],
            raw_files,
        )

    if source == "demo":
        return (
            generate_demo_lalonde_fixture(),
            "deterministic-lalonde-shaped-demo-fixture",
            "local deterministic fixture generated by speccurve_l0.data",
            "demo_only_not_claim_evidence",
            [
                "Demo fixture is synthetic and cannot support the final empirical claim.",
                "It exists to test the verifier, result table, report, app shell, and benchmark plumbing.",
            ],
            [],
        )

    raise ValueError(f"unknown source: {source}")
