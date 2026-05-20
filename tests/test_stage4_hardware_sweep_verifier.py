from __future__ import annotations

import json
import uuid
from pathlib import Path

from qrope.automated_stage_gates import (
    ENTANGLING_CX_CIRCUIT_FAMILY,
    PRODUCT_STATE_CIRCUIT_FAMILY,
    HardwareAdapter,
    counts_to_expectations,
    generate_transformer_phase_wrap_attention_bundle,
    ideal_counts_for_hardware_row,
    run_hardware_packet,
)
from scripts.verify_stage4_hardware_sweep import validate_manifest, verify_sweep_manifest


class SyntheticIdealHardwareAdapter(HardwareAdapter):
    def preflight(self, packet: dict) -> dict:
        return {
            "status": "READY",
            "blockers": [],
            "provider": packet["provider"],
            "backend": packet["backend"],
            "budget_cap_usd": packet["config"]["budget_cap_usd"],
            "estimated_packet_cost_usd": packet["config"]["estimated_packet_cost_usd"],
            "note": "synthetic test fixture only",
        }

    def run_packet(self, packet: dict) -> dict:
        return {
            "status": "COMPLETED",
            "jobs": [
                {
                    "job_id": "synthetic-job-1",
                    "provider": packet["provider"],
                    "backend": packet["backend"],
                    "shot_count": packet["shot_count"],
                    "raw_counts_by_row": [
                        {"row_id": row["row_id"], "counts": ideal_counts_for_hardware_row(row, packet["shot_count"])}
                        for row in packet["rows"]
                    ],
                }
            ],
            "backend_metadata": {"provider": packet["provider"], "backend": packet["backend"], "synthetic": True},
            "calibration_metadata": {"captured_at_utc": "2026-05-18T00:00:00Z", "synthetic": True},
        }


def _tmp_root() -> Path:
    root = Path(".pytest_cache") / "stage4_hardware_sweep_tests" / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=True)
    return root


def _write_record(root: Path, family: str, *, mutate_evaluation: bool = False) -> dict:
    env = {
        "QROPE_REAL_HARDWARE_PROVIDER": "ibm_runtime",
        "QROPE_HARDWARE_BACKEND": "synthetic_backend",
        "QROPE_HARDWARE_BUDGET_USD_CAP": "10",
        "QROPE_HARDWARE_ROW_LIMIT": "8",
        "QROPE_HARDWARE_SHOT_COUNT": "256",
        "QROPE_HARDWARE_CIRCUIT_FAMILY": family,
        "IBM_QUANTUM_TOKEN": "synthetic-token",
    }
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    result = run_hardware_packet(bundle.test[:8], adapter=SyntheticIdealHardwareAdapter(), env=env)
    record_dir = root / family
    record_dir.mkdir(parents=True)
    evaluation = json.loads(json.dumps(result["evaluation"]))
    if mutate_evaluation:
        evaluation["witness"]["mae"] = round(evaluation["witness"]["mae"] + 0.25, 6)
    paths = {
        "packet_path": record_dir / "frozen_packet.json",
        "execution_path": record_dir / "execution.json",
        "evaluation_path": record_dir / "evaluation.json",
        "summary_path": record_dir / "summary.json",
    }
    paths["packet_path"].write_text(json.dumps(result["packet"], indent=2), encoding="utf-8")
    paths["execution_path"].write_text(json.dumps(result["execution"], indent=2), encoding="utf-8")
    paths["evaluation_path"].write_text(json.dumps(evaluation, indent=2), encoding="utf-8")
    paths["summary_path"].write_text(
        json.dumps({"result": {"status": result["status"], "outcome": result["outcome"]}}, indent=2),
        encoding="utf-8",
    )
    return {
        "record_id": f"synthetic__synthetic_backend__{family}",
        "provider": "ibm_runtime",
        "backend": "synthetic_backend",
        "family": family,
        "status": "completed",
        "shots": 256,
        "rows": 8,
        "job_ids": ["synthetic-job-1"],
        "submitted_at_utc": "2026-05-18T00:00:00Z",
        "completed_at_utc": "2026-05-18T00:00:01Z",
        "calibration_metadata_path": None,
        "packet_path": str(paths["packet_path"]),
        "execution_path": str(paths["execution_path"]),
        "evaluation_path": str(paths["evaluation_path"]),
        "summary_path": str(paths["summary_path"]),
        "verifier_output_path": str(record_dir / "offline_verification.json"),
        "recorded_metrics": {
            "witness": result["evaluation"]["witness"],
            "control": result["evaluation"]["control"],
            "outcome": result["evaluation"]["outcome"],
        },
        "synthetic_fixture": True,
    }


def _manifest(records: list[dict]) -> dict:
    return {
        "manifest_version": "stage4_hardware_sweep_manifest_v1",
        "sweep_id": "synthetic-stage4-sweep-fixture",
        "claim_boundary": {"supported": "synthetic verifier mechanics only", "excluded": ["scientific evidence"]},
        "budget_policy": {"approval_required_above_usd": 100, "offline_verification_cost_usd": 0},
        "expected_families": [PRODUCT_STATE_CIRCUIT_FAMILY, ENTANGLING_CX_CIRCUIT_FAMILY],
        "expected_backends": [{"provider": "ibm_runtime", "backend": "synthetic_backend", "expected_shots": 256}],
        "records": records,
    }


def test_manifest_schema_validation_rejects_missing_required_fields() -> None:
    errors = validate_manifest({"manifest_version": "stage4_hardware_sweep_manifest_v1", "records": [{"record_id": "bad"}]})
    assert any("missing required fields" in error for error in errors)


def test_raw_count_to_expectation_conversion() -> None:
    expectations = counts_to_expectations({"00": 3, "01": 1, "10": 5, "11": 7})
    assert expectations["shots"] == 16
    assert expectations["z0"] == 0.0
    assert expectations["z1"] == -0.5
    assert expectations["zz"] == 0.25
    assert expectations["valid"] is True


def test_product_state_sweep_record_recomputes_metrics() -> None:
    tmp_path = _tmp_root()
    record = _write_record(tmp_path, PRODUCT_STATE_CIRCUIT_FAMILY)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(_manifest([record]), indent=2), encoding="utf-8")
    verification = verify_sweep_manifest(manifest_path)
    metrics = verification["records"][0]["recomputed_metrics"]
    assert verification["pass"] is True
    assert verification["table"][0]["family"] == PRODUCT_STATE_CIRCUIT_FAMILY
    assert metrics["witness"]["mae"] < metrics["control"]["mae"]


def test_cx_sweep_record_recomputes_metrics() -> None:
    tmp_path = _tmp_root()
    record = _write_record(tmp_path, ENTANGLING_CX_CIRCUIT_FAMILY)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(_manifest([record]), indent=2), encoding="utf-8")
    verification = verify_sweep_manifest(manifest_path)
    metrics = verification["records"][0]["recomputed_metrics"]
    assert verification["table"][0]["family"] == ENTANGLING_CX_CIRCUIT_FAMILY
    assert metrics["witness"]["mae"] >= 0.0
    assert metrics["control"]["mae"] >= 0.0
    assert verification["records"][0]["checks"]


def test_missing_evidence_files_fail_clearly() -> None:
    tmp_path = _tmp_root()
    record = {
        "record_id": "missing-record",
        "provider": "ionq",
        "backend": "ionq_qpu",
        "family": PRODUCT_STATE_CIRCUIT_FAMILY,
        "status": "missing",
        "shots": 1024,
        "rows": 16,
        "packet_path": "missing/frozen_packet.json",
        "execution_path": "missing/execution.json",
        "evaluation_path": "missing/evaluation.json",
        "summary_path": "missing/summary.json",
        "missing_required_artifacts": ["frozen_packet.json", "execution.json"],
        "todo": "Supply real run records.",
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(_manifest([record]), indent=2), encoding="utf-8")
    verification = verify_sweep_manifest(manifest_path)
    assert verification["pass"] is False
    assert verification["missing_records"] == ["missing-record"]


def test_metric_mismatch_fails() -> None:
    tmp_path = _tmp_root()
    record = _write_record(tmp_path, PRODUCT_STATE_CIRCUIT_FAMILY, mutate_evaluation=True)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(_manifest([record]), indent=2), encoding="utf-8")
    verification = verify_sweep_manifest(manifest_path)
    checks = verification["records"][0]["checks"]
    assert verification["pass"] is False
    assert any(check["name"] == "recorded_evaluation_matches_recomputed" and check["pass"] is False for check in checks)


def test_public_docs_do_not_present_forbidden_overclaims() -> None:
    forbidden = [
        "quantum advantage proven",
        "transformer superiority proven",
        "general cross-backend robustness established",
        "production LLM improvement",
    ]
    docs = [
        Path("README.md"),
        Path("docs/publication/qrope-paper-v1.md"),
        Path("docs/research/q-rope-stage4-hardware-comparison-v1.md"),
    ]
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in docs if path.exists())
    for phrase in forbidden:
        assert phrase.lower() not in combined
