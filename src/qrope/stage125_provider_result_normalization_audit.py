from __future__ import annotations

import csv
import importlib
import json
from pathlib import Path
from typing import Any


STAGE125_SCHEMA_VERSION = "qrope_stage125_provider_result_normalization_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE124_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage124_adapter_readiness_alignment_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage125_provider_result_normalization_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
PROVIDER_MODULES = {
    "amazon_braket": "qrope.provider_adapters.amazon_braket",
    "ibm_runtime": "qrope.provider_adapters.ibm_runtime",
}
SAMPLES = {
    "amazon_braket": [
        {"measurementCounts": {"00": 7, "11": 3}},
        {"counts": {"0b01": 4, "10": 6}},
    ],
    "ibm_runtime": [
        {"counts": {"00": 8, "0b11": 2}},
        {"quasi_dists": [{"00": 0.25, "11": 0.75}], "shots": 1000},
    ],
}


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _counts_ready(counts: Any) -> bool:
    if not isinstance(counts, dict) or not counts:
        return False
    if any(not isinstance(key, str) or any(char not in "01" for char in key) for key in counts):
        return False
    try:
        return sum(int(value) for value in counts.values()) > 0
    except (TypeError, ValueError):
        return False


def _provider_record(provider: str) -> dict[str, Any]:
    module = importlib.import_module(PROVIDER_MODULES[provider])
    normalizer = getattr(module, "normalize_result_counts", None)
    missing = []
    sample_records = []
    if not callable(normalizer):
        missing.append("normalizer_not_callable")
    for index, sample in enumerate(SAMPLES[provider]):
        try:
            counts = normalizer(sample) if callable(normalizer) else {}
            ready = _counts_ready(counts)
            if not ready:
                missing.append(f"sample_{index}_counts_not_ready")
            sample_records.append({"sample_index": index, "counts": counts, "ready": ready, "missing_evidence": [] if ready else ["counts_not_ready"]})
        except Exception as exc:  # noqa: BLE001 - audit reports normalizer failures.
            missing.append(f"sample_{index}_normalization_failed")
            sample_records.append({"sample_index": index, "counts": {}, "ready": False, "missing_evidence": [str(exc)]})
    return {
        "provider": provider,
        "normalizer_callable": callable(normalizer),
        "sample_count": len(SAMPLES[provider]),
        "ready_sample_count": sum(1 for record in sample_records if record["ready"]),
        "sample_records": sample_records,
        "missing_evidence": sorted(set(missing)),
        "ready": not missing,
    }


def run_stage125_audit(*, stage124_results_path: Path = DEFAULT_STAGE124_RESULTS) -> dict[str, Any]:
    stage124 = _load_json(stage124_results_path)
    missing_sources = [] if isinstance(stage124, dict) else [str(stage124_results_path.as_posix())]
    records = [_provider_record(provider) for provider in sorted(PROVIDER_MODULES)]
    ready = all(record["ready"] for record in records) and not missing_sources
    return {
        "schema_version": STAGE125_SCHEMA_VERSION,
        "stage": "stage125_provider_result_normalization_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_RESULT_NORMALIZATION_READY_EXECUTION_BLOCKED"
            if ready
            else "PROVIDER_RESULT_NORMALIZATION_INCOMPLETE"
        ),
        "source_artifacts": [str(stage124_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage124_decision": stage124.get("decision") if isinstance(stage124, dict) else None,
        "provider_count": len(records),
        "ready_provider_count": sum(1 for record in records if record["ready"]),
        "provider_records": records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "provider adapters expose result-count normalizers",
                "sample IBM Runtime and Amazon Braket result shapes normalize to canonical bitstring count mappings",
                "normalized counts are Stage 114-compatible before live SDK submission is enabled",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "live provider SDK submission",
                "real provider result records",
                "Stage 113 evidence assembly",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Wire provider SDK submitters to these normalizers so real provider outputs are converted into Stage 114 "
            "count records after Stage 106/111 readiness clears."
        ),
    }


def write_stage125_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage124_decision": result["stage124_decision"],
        "provider_count": result["provider_count"],
        "ready_provider_count": result["ready_provider_count"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
        "next_gate": result["next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("provider", "normalizer_callable", "sample_count", "ready_sample_count", "ready", "missing_evidence"),
        )
        writer.writeheader()
        for record in result["provider_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "normalizer_callable": record["normalizer_callable"],
                    "sample_count": record["sample_count"],
                    "ready_sample_count": record["ready_sample_count"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage125_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_provider_count: {result['ready_provider_count']}/{result['provider_count']}")
    print(f"next_gate: {result['next_gate']}")
