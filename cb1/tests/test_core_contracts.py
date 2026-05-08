from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import scripts.check_submission as check_submission
from scripts.mi300x_preflight import evaluate_preflight
from speccurve_l0.artifacts import read_json, write_json
from speccurve_l0.benchmark_contract import (
    benchmark_sha256_path,
    hardware_log_path,
    validate_benchmark_contract,
    validate_hardware_log_contract,
    write_benchmark_sha256,
    write_hardware_log,
)
from speccurve_l0.pipeline import run_pipeline
from scripts.export_static_space import _claim_artifact
from speccurve_l0.specs import generate_spec_grid, invalid_spec_fixtures
from speccurve_l0.verifier import verify_specs


class CoreContractsTest(unittest.TestCase):
    def test_spec_grid_has_enough_approved_paths(self) -> None:
        specs = [spec.to_dict() for spec in generate_spec_grid()]
        self.assertGreaterEqual(len(specs), 200)
        estimators = {spec["estimator"] for spec in specs}
        self.assertTrue({"psm_1nn", "ipw_att", "mahalanobis_1nn", "cem_att"}.issubset(estimators))

    def test_invalid_fixtures_are_rejected(self) -> None:
        dataset_columns = {
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
            "u74",
            "u75",
        }
        result = verify_specs(invalid_spec_fixtures(), dataset_columns)
        self.assertEqual(len(result["approved"]), 0)
        self.assertEqual(len(result["rejected"]), len(invalid_spec_fixtures()))

    def test_demo_pipeline_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp) / "artifacts"
            result = run_pipeline(artifact_dir, source="demo", max_specs=96)
            self.assertGreaterEqual(len(result["approved_specs"]), 50)
            self.assertEqual(len(result["results"]), len(result["approved_specs"]))
            self.assertTrue((artifact_dir / "dataset-card.json").exists())
            self.assertTrue((artifact_dir / "baseline.json").exists())
            self.assertTrue((artifact_dir / "report.md").exists())
            card = read_json(artifact_dir / "dataset-card.json")
            self.assertEqual(card["evidence_status"], "demo_only_not_claim_evidence")
            report = (artifact_dir / "report.md").read_text(encoding="utf-8")
            self.assertIn("Demo fixture is synthetic", report)
            estimators = {row["estimator"] for row in result["results"]}
            self.assertIn("psm_1nn", estimators)
            self.assertIn("ipw_att", estimators)

    def test_readiness_overall_prioritizes_failures(self) -> None:
        checks = [{"status": "external_blocker"}, {"status": "fail"}]
        self.assertEqual(check_submission._overall_status(checks), "fail")

    def test_mi300x_preflight_requires_rocm_visible_to_pytorch(self) -> None:
        hardware = {
            "torch_available": True,
            "gpu": "AMD Instinct MI300X",
            "hip": "6.3",
            "is_mi300x": True,
        }
        self.assertEqual(evaluate_preflight(hardware, {"status": "pass"}), [])
        failures = evaluate_preflight({**hardware, "hip": None}, {"status": "pass"})
        self.assertTrue(any("HIP" in failure for failure in failures))
        failures = evaluate_preflight({**hardware, "gpu": "NVIDIA H100", "is_mi300x": False}, {"status": "pass"})
        self.assertTrue(any("MI300" in failure for failure in failures))

    def test_demo_pipeline_is_isolated_from_evidence_artifacts(self) -> None:
        result = check_submission._demo_isolation_check()
        self.assertEqual(result["status"], "pass")

    def test_static_space_source_has_no_server_execution_surface(self) -> None:
        readme = Path("space") / "README.md"
        index = Path("space") / "index.html"
        self.assertIn("sdk: static", readme.read_text(encoding="utf-8"))
        index_text = index.read_text(encoding="utf-8")
        self.assertNotIn("innerHTML", index_text)
        self.assertNotIn("eval(", index_text)
        self.assertNotIn("new Function", index_text)
        self.assertNotIn("fetch('http", index_text)
        self.assertNotIn('fetch("http', index_text)
        self.assertIn("crypto.subtle.digest", index_text)
        self.assertIn("benchmark.json.sha256", index_text)
        self.assertIn("methodology/hardware.log", index_text)

    def test_static_claim_artifact_avoids_banned_public_copy_terms(self) -> None:
        claim = _claim_artifact(
            {
                "dataset_id": "nber",
                "source": "source",
                "dataset_hash": "abc",
                "evidence_status": "frozen_nber_source_psid1_controls",
                "row_count": 2675,
            }
        )
        public_text = " ".join(str(value) for value in claim.values())
        lowered = public_text.lower()
        for banned in ["replicated", "replication crisis", "truth verdict", "fraud", "misconduct"]:
            self.assertNotIn(banned, lowered)

    def test_benchmark_contract_uses_wiki_c_tolerance_shape(self) -> None:
        benchmark = {
            "benchmark_id": "bench-1",
            "dataset_hash": "abc",
            "spec_batch_id": "batch-1",
            "approved_spec_count": 2,
            "resamples_per_spec": 3,
            "total_statistical_runs": 6,
            "cpu_runtime_seconds": 12.0,
            "gpu_runtime_seconds": 2.0,
            "speedup": 6.0,
            "throughput_cpu": 0.5,
            "throughput_gpu": 3.0,
            "tolerance_check": "pass",
            "warmup_policy": "reported separately",
            "hardware": {
                "cpu": "cpu",
                "gpu": "AMD Instinct MI300X",
                "rocm": "6.3",
                "torch": "2.4",
                "hip": "6.3",
            },
            "generated_at": "2026-05-08T00:00:00Z",
            "submission_ready": True,
        }
        self.assertEqual(validate_benchmark_contract(benchmark, dataset_hash="abc"), [])
        benchmark["tolerance_check"] = {"passed": True}
        failures = validate_benchmark_contract(benchmark, dataset_hash="abc")
        self.assertTrue(any("tolerance_check" in failure for failure in failures))

    def test_benchmark_sha_sidecar_is_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "benchmark.json"
            write_json(path, {"benchmark_id": "bench-1"})
            digest = write_benchmark_sha256(path)
            sidecar = benchmark_sha256_path(path)
            self.assertTrue(sidecar.exists())
            self.assertIn(digest, sidecar.read_text(encoding="utf-8"))

    def test_hardware_log_contract_requires_benchmark_evidence(self) -> None:
        benchmark = self._valid_benchmark()
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp)
            benchmark_path = artifact_dir / "benchmark.json"
            write_json(benchmark_path, benchmark)
            path = write_hardware_log(artifact_dir, benchmark, benchmark["hardware"], benchmark_path)
            self.assertEqual(path, hardware_log_path(artifact_dir))
            self.assertEqual(validate_hardware_log_contract(path, benchmark), [])
            failures = validate_hardware_log_contract(artifact_dir / "methodology" / "missing.log", benchmark)
            self.assertIn("methodology/hardware.log is missing", failures)

    def test_readiness_accepts_valid_benchmark_contract_and_sha(self) -> None:
        benchmark = self._valid_benchmark()
        with tempfile.TemporaryDirectory() as tmp:
            old_artifacts = check_submission.ARTIFACTS
            try:
                artifact_dir = Path(tmp)
                check_submission.ARTIFACTS = artifact_dir
                write_json(artifact_dir / "benchmark.json", benchmark)
                write_benchmark_sha256(artifact_dir / "benchmark.json")
                write_hardware_log(
                    artifact_dir,
                    benchmark,
                    benchmark["hardware"],
                    artifact_dir / "benchmark.json",
                )
                result = check_submission._benchmark_contract_check({"dataset_hash": "abc"})
                self.assertEqual(result["status"], "pass")
                self.assertEqual(result["failures"], [])
            finally:
                check_submission.ARTIFACTS = old_artifacts

    def test_readiness_rejects_valid_benchmark_without_hardware_log(self) -> None:
        benchmark = self._valid_benchmark()
        with tempfile.TemporaryDirectory() as tmp:
            old_artifacts = check_submission.ARTIFACTS
            try:
                artifact_dir = Path(tmp)
                check_submission.ARTIFACTS = artifact_dir
                write_json(artifact_dir / "benchmark.json", benchmark)
                write_benchmark_sha256(artifact_dir / "benchmark.json")
                result = check_submission._benchmark_contract_check({"dataset_hash": "abc"})
                self.assertEqual(result["status"], "fail")
                self.assertTrue(any("hardware.log" in failure for failure in result["failures"]))
            finally:
                check_submission.ARTIFACTS = old_artifacts

    @staticmethod
    def _valid_benchmark() -> dict:
        return {
            "benchmark_id": "bench-1",
            "dataset_hash": "abc",
            "spec_batch_id": "batch-1",
            "approved_spec_count": 2,
            "resamples_per_spec": 3,
            "total_statistical_runs": 6,
            "cpu_runtime_seconds": 12.0,
            "gpu_runtime_seconds": 2.0,
            "speedup": 6.0,
            "throughput_cpu": 0.5,
            "throughput_gpu": 3.0,
            "tolerance_check": "pass",
            "warmup_policy": "reported separately",
            "hardware": {
                "cpu": "cpu",
                "gpu": "AMD Instinct MI300X",
                "rocm": "6.3",
                "torch": "2.4",
                "hip": "6.3",
            },
            "generated_at": "2026-05-08T00:00:00Z",
            "submission_ready": True,
        }


if __name__ == "__main__":
    unittest.main()
