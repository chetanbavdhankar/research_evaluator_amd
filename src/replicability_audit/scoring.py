from typing import Dict, Any

def score_data_accessibility(audit: dict) -> int:
    data_inv = audit.get("data_inventory", [])
    if not data_inv: return 3
    statuses = [a.get("access", {}).get("kind") for a in data_inv]
    if "gated" in statuses: return 1
    if "public_registration" in statuses: return 2
    return 3

def score_data_identifiability(audit: dict) -> int:
    data_inv = audit.get("data_inventory", [])
    if not data_inv: return 3
    has_doi = all(a.get("identifiers", {}).get("doi") for a in data_inv)
    if has_doi: return 3
    has_any_id = all(len(a.get("identifiers", {})) > 0 for a in data_inv)
    if has_any_id: return 2
    return 1

def score_method_specification(audit: dict) -> int:
    methods = audit.get("method_pipeline", [])
    if not methods: return 0
    underspecified = sum(1 for m in methods for p in m.get("parameters", []) if p.get("underspecified"))
    if underspecified == 0: return 3
    if underspecified <= 2: return 2
    return 1

def score_software_stack(audit: dict) -> int:
    software = audit.get("software_inventory", [])
    if not software: return 0
    has_versions = all(s.get("version") for s in software)
    if has_versions: return 2 
    return 1

def score_code_availability(audit: dict) -> int:
    data_inv = audit.get("data_inventory", [])
    code_assets = [a for a in data_inv if a.get("kind") == "code"]
    if not code_assets: return 0
    if any(a.get("access", {}).get("kind") == "gated" for a in code_assets): return 1
    return 2 

def score_compute_footprint(audit: dict) -> int:
    compute = audit.get("compute_estimate", {})
    if not compute: return 0
    gpu = compute.get("gpu_hours") or 0
    cpu = compute.get("cpu_hours") or 0
    if gpu > 1000: return 0
    if gpu > 100: return 1
    if gpu > 0 or cpu > 100: return 2
    return 3

def score_dependency_closure(audit: dict) -> int:
    return 2  # Stub

def score_result_verifiability(audit: dict) -> int:
    return 2  # Stub

def generate_scorecard(audit: dict) -> dict:
    return {
        "data_accessibility": score_data_accessibility(audit),
        "data_identifiability": score_data_identifiability(audit),
        "method_specification": score_method_specification(audit),
        "software_stack": score_software_stack(audit),
        "code_availability": score_code_availability(audit),
        "compute_footprint": score_compute_footprint(audit),
        "dependency_closure": score_dependency_closure(audit),
        "result_verifiability": score_result_verifiability(audit)
    }

def derive_tier(scorecard: dict) -> int:
    vals = list(scorecard.values())
    if (all(v >= 2 for v in vals)
        and scorecard.get("data_accessibility", 0) == 3
        and scorecard.get("code_availability", 0) >= 2):
        return 1
    if all(v != 0 for v in vals) and sum(1 for v in vals if v == 1) <= 2:
        return 2
    return 3
