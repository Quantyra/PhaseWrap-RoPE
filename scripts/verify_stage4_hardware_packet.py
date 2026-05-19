from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.automated_stage_gates import evaluate_hardware_execution


DEFAULT_STAGE4_DIR = REPO_ROOT / "logs" / "automated_stage_gates" / "stage4_hardware_packet"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _select_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": payload.get("status"),
        "outcome": payload.get("outcome"),
        "gate_pass": payload.get("gate_pass"),
        "witness": payload.get("witness"),
        "control": payload.get("control"),
        "hardware_direction_positive": payload.get("hardware_direction_positive"),
        "noisy_direction_positive": payload.get("noisy_direction_positive"),
        "direction_agreement": payload.get("direction_agreement"),
        "metadata_complete": payload.get("metadata_complete"),
        "missing_metadata": payload.get("missing_metadata"),
        "comparability_pass": payload.get("comparability_pass"),
        "fail_reasons": payload.get("fail_reasons"),
    }


def _execution_job_ids(execution: dict[str, Any]) -> list[str]:
    job_ids: list[str] = []
    for job in execution.get("jobs", []):
        for record in job.get("provider_job_records", []):
            job_id = str(record.get("job_id", "")).strip()
            if job_id:
                job_ids.append(job_id)
        if not job.get("provider_job_records"):
            job_ids.extend(item for item in str(job.get("job_id", "")).split(",") if item)
    return job_ids


def verify_packet_files(
    *,
    packet_path: Path,
    execution_path: Path,
    evaluation_path: Path | None = None,
    summary_path: Path | None = None,
    expected_provider: str | None = None,
    expected_backend: str | None = None,
    expected_job_id: str | None = None,
) -> dict[str, Any]:
    packet = _read_json(packet_path)
    execution = _read_json(execution_path)
    recomputed = evaluate_hardware_execution(packet, execution)
    checks: list[dict[str, Any]] = []

    def add_check(name: str, passed: bool, detail: Any = None) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    add_check("execution_completed", execution.get("status") == "COMPLETED", execution.get("status"))
    add_check("recomputed_gate_pass", recomputed.get("gate_pass") is True, recomputed.get("gate_pass"))
    add_check("recomputed_outcome_hardware_positive", recomputed.get("outcome") == "hardware-positive", recomputed.get("outcome"))
    add_check("metadata_complete", recomputed.get("metadata_complete") is True, recomputed.get("missing_metadata"))
    add_check("comparability_pass", recomputed.get("comparability_pass") is True, recomputed.get("comparability_pass"))

    if expected_provider:
        add_check("expected_provider", packet.get("provider") == expected_provider, packet.get("provider"))
    if expected_backend:
        add_check("expected_backend", packet.get("backend") == expected_backend, packet.get("backend"))

    job_ids = _execution_job_ids(execution)
    if expected_job_id:
        add_check("expected_job_id", expected_job_id in job_ids, job_ids)
    else:
        add_check("job_id_present", all(bool(job_id) for job_id in job_ids) and bool(job_ids), job_ids)

    recorded_evaluation = _read_json(evaluation_path) if evaluation_path and evaluation_path.exists() else None
    if recorded_evaluation is not None:
        recorded_metrics = _select_metrics(recorded_evaluation)
        recomputed_metrics = _select_metrics(recomputed)
        add_check(
            "recorded_evaluation_matches_recomputed",
            recorded_metrics == recomputed_metrics,
            {"recorded": recorded_metrics, "recomputed": recomputed_metrics},
        )

    recorded_summary = _read_json(summary_path) if summary_path and summary_path.exists() else None
    if recorded_summary is not None:
        summary_result = recorded_summary.get("result", recorded_summary)
        add_check("summary_status_matches_recomputed", summary_result.get("status") == recomputed.get("status"), summary_result.get("status"))
        add_check("summary_outcome_matches_recomputed", summary_result.get("outcome") == recomputed.get("outcome"), summary_result.get("outcome"))

    verification = {
        "verifier": "qrope_stage4_offline_verifier_v1",
        "no_hardware_submission": True,
        "packet_path": str(packet_path),
        "execution_path": str(execution_path),
        "evaluation_path": str(evaluation_path) if evaluation_path else None,
        "summary_path": str(summary_path) if summary_path else None,
        "packet_sha256": _json_hash(packet_path),
        "execution_sha256": _json_hash(execution_path),
        "provider": packet.get("provider"),
        "backend": packet.get("backend"),
        "packet_id": packet.get("packet_id"),
        "job_ids": job_ids,
        "recomputed_evaluation": recomputed,
        "checks": checks,
        "pass": all(item["pass"] for item in checks),
    }
    return verification


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline verifier for the Q-RoPE Stage 4 hardware packet.")
    parser.add_argument("--stage4-dir", type=Path, default=DEFAULT_STAGE4_DIR)
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--execution", type=Path)
    parser.add_argument("--evaluation", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expected-provider")
    parser.add_argument("--expected-backend")
    parser.add_argument("--expected-job-id")
    args = parser.parse_args(argv)

    stage4_dir = args.stage4_dir
    packet_path = args.packet or stage4_dir / "frozen_packet.json"
    execution_path = args.execution or stage4_dir / "execution.json"
    evaluation_path = args.evaluation or stage4_dir / "evaluation.json"
    summary_path = args.summary or stage4_dir / "summary.json"
    output_path = args.output or stage4_dir / "offline_verification.json"

    verification = verify_packet_files(
        packet_path=packet_path,
        execution_path=execution_path,
        evaluation_path=evaluation_path,
        summary_path=summary_path,
        expected_provider=args.expected_provider,
        expected_backend=args.expected_backend,
        expected_job_id=args.expected_job_id,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(verification, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({key: verification[key] for key in ("pass", "provider", "backend", "packet_id", "job_ids")}, indent=2))
    return 0 if verification["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
