from __future__ import annotations

import csv
import hashlib
import random
import urllib.request
from pathlib import Path
from typing import Any

from .artifacts import file_hash, write_csv

RAW_LALONDE_COLUMNS = [
    "treat",
    "age",
    "educ",
    "black",
    "hispan",
    "married",
    "nodegree",
    "re74",
    "re75",
    "re78",
]
DERIVED_LALONDE_COLUMNS = ["u74", "u75"]
LALONDE_COLUMNS = RAW_LALONDE_COLUMNS + DERIVED_LALONDE_COLUMNS

RDATSETS_LALONDE_URL = "https://vincentarelbundock.github.io/Rdatasets/csv/MatchIt/lalonde.csv"
NBER_DATA_PAGE = "https://users.nber.org/~rdehejia/nswdata2.html"
NBER_DW_TREATED_URL = "https://www.nber.org/~rdehejia/data/nswre74_treated.txt"
NBER_DW_CONTROL_URL = "https://www.nber.org/~rdehejia/data/nswre74_control.txt"
NBER_PSID_CONTROLS_URL = "https://www.nber.org/~rdehejia/data/psid_controls.txt"


def generate_demo_lalonde_fixture(row_count: int = 420, seed: int = 20260507) -> list[dict[str, float]]:
    """Generate a deterministic LaLonde-shaped fixture for UI and contract testing.

    This fixture is intentionally not evidence for the final claim. It exists so the app,
    verifier, report renderer, and benchmark plumbing can be exercised before the final
    dataset gate is closed.
    """

    rng = random.Random(seed)
    rows: list[dict[str, float]] = []
    treated_count = int(row_count * 0.34)

    for index in range(row_count):
        treat = 1.0 if index < treated_count else 0.0
        age = rng.randint(18, 52)
        educ = max(4, min(18, int(rng.gauss(10.6 + 0.4 * treat, 2.0))))
        black = 1.0 if rng.random() < (0.72 if treat else 0.55) else 0.0
        hispan = 1.0 if black == 0.0 and rng.random() < (0.11 if treat else 0.16) else 0.0
        married = 1.0 if rng.random() < (0.22 if treat else 0.58) else 0.0
        nodegree = 1.0 if educ < 12 else 0.0
        latent = 5500 + 190 * educ + 55 * age + 700 * married - 850 * nodegree
        group_penalty = -900 * black - 350 * hispan
        re74 = max(0.0, rng.gauss(latent + group_penalty, 3600))
        re75 = max(0.0, rng.gauss(0.72 * re74 + 1100 * married, 2800))
        training_effect = 880 + 70 * max(0, 12 - educ)
        shock = rng.gauss(0, 4300)
        re78 = max(0.0, 0.45 * re74 + 0.38 * re75 + 260 * educ + training_effect * treat + shock)
        rows.append(
            {
                "treat": treat,
                "age": float(age),
                "educ": float(educ),
                "black": black,
                "hispan": hispan,
                "married": married,
                "nodegree": nodegree,
                "re74": round(re74, 2),
                "re75": round(re75, 2),
                "re78": round(re78, 2),
            }
        )
    return augment_lalonde_rows(rows)


def fetch_rdatasets_lalonde(destination: Path) -> list[dict[str, float]]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(RDATSETS_LALONDE_URL, timeout=30) as response:
        destination.write_bytes(response.read())
    return load_rdatasets_lalonde(destination)


def fetch_nber_lalonde(
    data_dir: Path,
    design: str,
) -> tuple[list[dict[str, float]], list[dict[str, str]]]:
    data_dir.mkdir(parents=True, exist_ok=True)
    if design == "dw-experimental":
        files = [
            ("nswre74_treated.txt", NBER_DW_TREATED_URL),
            ("nswre74_control.txt", NBER_DW_CONTROL_URL),
        ]
    elif design == "dw-psid1":
        files = [
            ("nswre74_treated.txt", NBER_DW_TREATED_URL),
            ("psid_controls.txt", NBER_PSID_CONTROLS_URL),
        ]
    else:
        raise ValueError(f"unknown NBER design: {design}")

    rows: list[dict[str, float]] = []
    raw_files: list[dict[str, str]] = []
    for filename, url in files:
        path = data_dir / filename
        if path.exists():
            content = path.read_bytes()
        else:
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read()
            path.write_bytes(content)
        raw_files.append(
            {
                "filename": filename,
                "url": url,
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
        rows.extend(load_nber_text(path))
    return rows, raw_files


def load_nber_text(path: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        values = line.strip().split()
        if not values:
            continue
        if len(values) != len(RAW_LALONDE_COLUMNS):
            raise ValueError(f"{path} has {len(values)} columns; expected {len(RAW_LALONDE_COLUMNS)}")
        rows.append({column: float(value) for column, value in zip(RAW_LALONDE_COLUMNS, values)})
    return augment_lalonde_rows(rows)


def load_rdatasets_lalonde(path: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            race = raw.get("race", "").strip().lower()
            rows.append(
                {
                    "treat": float(raw["treat"]),
                    "age": float(raw["age"]),
                    "educ": float(raw["educ"]),
                    "black": 1.0 if race == "black" else 0.0,
                    "hispan": 1.0 if race == "hispan" else 0.0,
                    "married": float(raw["married"]),
                    "nodegree": float(raw["nodegree"]),
                    "re74": float(raw["re74"]),
                    "re75": float(raw["re75"]),
                    "re78": float(raw["re78"]),
                }
            )
    return augment_lalonde_rows(rows)


def load_lalonde_csv(path: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [column for column in RAW_LALONDE_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")
        for raw in reader:
            rows.append({column: float(raw[column]) for column in RAW_LALONDE_COLUMNS})
    return augment_lalonde_rows(rows)


def augment_lalonde_rows(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    augmented: list[dict[str, float]] = []
    for row in rows:
        next_row = row.copy()
        next_row["u74"] = 1.0 if next_row["re74"] <= 0 else 0.0
        next_row["u75"] = 1.0 if next_row["re75"] <= 0 else 0.0
        augmented.append(next_row)
    return augmented


def persist_dataset(path: Path, rows: list[dict[str, float]]) -> dict[str, Any]:
    write_csv(path, rows, LALONDE_COLUMNS)
    return {
        "path": str(path),
        "row_count": len(rows),
        "columns": LALONDE_COLUMNS,
        "dataset_hash": file_hash(path),
    }
