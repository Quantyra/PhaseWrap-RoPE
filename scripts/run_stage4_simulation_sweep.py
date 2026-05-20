from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from qrope.automated_stage_gates import (
    ENTANGLING_CX_CIRCUIT_FAMILY,
    PRODUCT_STATE_CIRCUIT_FAMILY,
    HARDWARE_PACKET_ROW_LIMIT,
    HardwareAdapter,
    generate_transformer_phase_wrap_attention_bundle,
    ideal_counts_for_hardware_row,
    run_hardware_packet,
)
from scripts.verify_stage4_simulation_sweep import DEFAULT_MANIFEST, DEFAULT_OUTPUT, normalize_simulation_verification
from scripts.verify_stage4_hardware_sweep import verify_sweep_manifest


REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_ROOT = REPO_ROOT / "logs" / "automated_stage_gates" / "stage4_simulation_sweep"
FAMILIES = [PRODUCT_STATE_CIRCUIT_FAMILY, ENTANGLING_CX_CIRCUIT_FAMILY]


class FreeSimulationAdapter(HardwareAdapter):
    def __init__(self, backend: str) -> None:
        self.backend = backend

    def preflight(self, packet: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "READY",
            "blockers": [],
            "provider": packet["provider"],
            "backend": packet["backend"],
            "budget_cap_usd": packet["config"]["budget_cap_usd"],
            "estimated_packet_cost_usd": 0.0,
            "note": "free local simulation; no hardware submission",
        }

    def run_packet(self, packet: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "COMPLETED",
            "jobs": [
                {
                    "job_id": f"{self.backend}-deterministic-local-sim",
                    "provider": packet["provider"],
                    "backend": packet["backend"],
                    "shot_count": packet["shot_count"],
                    "raw_counts_by_row": [
                        {"row_id": row["row_id"], "counts": self._counts(row, packet["shot_count"])}
                        for row in packet["rows"]
                    ],
                }
            ],
            "backend_metadata": {
                "provider": packet["provider"],
                "backend": packet["backend"],
                "simulator": True,
                "hardware": False,
                "cost_usd": 0.0,
            },
            "calibration_metadata": {
                "simulator": True,
                "hardware": False,
                "model": self.backend,
                "captured_at_utc": "2026-05-18T00:00:00Z",
            },
        }

    def _counts(self, row: dict[str, Any], shots: int) -> dict[str, int]:
        counts = ideal_counts_for_hardware_row(row, shots)
        if self.backend != "local_readout_bias_simulator":
            return counts
        biased = dict(counts)
        move = max(1, shots // 128)
        if biased.get("00", 0) >= move:
            biased["00"] -= move
            biased["01"] = biased.get("01", 0) + move
        if biased.get("11", 0) >= move:
            biased["11"] -= move
            biased["10"] = biased.get("10", 0) + move
        return biased


def _write_record(record_dir: Path, result: dict[str, Any]) -> dict[str, str]:
    record_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "packet_path": record_dir / "frozen_packet.json",
        "execution_path": record_dir / "execution.json",
        "evaluation_path": record_dir / "evaluation.json",
        "summary_path": record_dir / "summary.json",
    }
    paths["packet_path"].write_text(json.dumps(result["packet"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths["execution_path"].write_text(json.dumps(result["execution"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths["evaluation_path"].write_text(json.dumps(result["evaluation"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths["summary_path"].write_text(
        json.dumps({"result": {"status": result["status"], "outcome": result["outcome"]}}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {key: str(path.relative_to(REPO_ROOT)).replace("\\", "/") for key, path in paths.items()}


def run_simulation_sweep(row_limit: int, shots: int) -> dict[str, Any]:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    records: list[dict[str, Any]] = []
    backends = ["local_ideal_simulator", "local_readout_bias_simulator"]
    for backend in backends:
        for family in FAMILIES:
            env = {
                "QROPE_REAL_HARDWARE_PROVIDER": "local_simulator",
                "QROPE_HARDWARE_BACKEND": backend,
                "QROPE_HARDWARE_BUDGET_USD_CAP": "0",
                "QROPE_HARDWARE_ESTIMATED_COST_USD": "0",
                "QROPE_HARDWARE_ROW_LIMIT": str(row_limit),
                "QROPE_HARDWARE_SHOT_COUNT": str(shots),
                "QROPE_HARDWARE_CIRCUIT_FAMILY": family,
            }
            result = run_hardware_packet(bundle.test[:row_limit], adapter=FreeSimulationAdapter(backend), env=env)
            record_id = f"local_simulator__{backend}__{family}"
            paths = _write_record(LOG_ROOT / record_id, result)
            records.append(
                {
                    "record_id": record_id,
                    "provider": "local_simulator",
                    "backend": backend,
                    "family": family,
                    "status": "completed",
                    "shots": shots,
                    "rows": row_limit,
                    "job_ids": [job.get("job_id") for job in result["execution"].get("jobs", [])],
                    "submitted_at_utc": None,
                    "completed_at_utc": None,
                    "calibration_metadata_path": None,
                    **paths,
                    "verifier_output_path": str((LOG_ROOT / record_id / "offline_verification.json").relative_to(REPO_ROOT)).replace("\\", "/"),
                    "recorded_metrics": None,
                    "reported_metrics": {
                        "witness": result["evaluation"].get("witness"),
                        "control": result["evaluation"].get("control"),
                        "outcome": "simulation-positive"
                        if result["evaluation"].get("outcome") == "hardware-positive"
                        else "simulation-negative"
                        if result["evaluation"].get("outcome") == "hardware-negative"
                        else "simulation-inconclusive",
                    },
                    "simulation_only": True,
                }
            )
    manifest = {
        "manifest_version": "stage4_simulation_sweep_manifest_v1",
        "sweep_id": "stage4-free-simulation-sweep-2026-05",
        "evidence_status": "simulation_verified",
        "budget_policy": {
            "approval_required_above_usd": 100,
            "offline_verification_cost_usd": 0,
            "hardware_execution_approved": False,
            "policy": "No hardware execution is approved for this simulation-only plan.",
        },
        "claim_boundary": {
            "supported": "Free local simulation validates packet, circuit-family, raw-count, and verifier mechanics only.",
            "excluded": [
                "hardware validation",
                "broad quantum advantage",
                "production transformer superiority",
                "full transformer-scale validation",
                "general cross-backend robustness",
                "deployed-model performance improvement",
            ],
        },
        "expected_families": FAMILIES,
        "expected_backends": [
            {"provider": "local_simulator", "backend": backend, "expected_shots": shots}
            for backend in backends
        ],
        "records": records,
    }
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    DEFAULT_MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    verification = normalize_simulation_verification(verify_sweep_manifest(DEFAULT_MANIFEST))
    DEFAULT_OUTPUT.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return verification


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the free local Stage 4 simulation sweep.")
    parser.add_argument("--row-limit", type=int, default=HARDWARE_PACKET_ROW_LIMIT)
    parser.add_argument("--shots", type=int, default=4096)
    args = parser.parse_args()
    verification = run_simulation_sweep(row_limit=args.row_limit, shots=args.shots)
    print(json.dumps({"pass": verification["pass"], "records": len(verification["records"]), "output": str(DEFAULT_OUTPUT)}, indent=2))
    return 0 if verification["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
