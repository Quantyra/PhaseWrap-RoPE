from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE105_SCHEMA_VERSION = "qrope_stage105_independent_rerun_protocol_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE101_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage101_known_state_calibration_gate" / "results.json"
DEFAULT_STAGE103_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage103_robustness_metric_preregistration" / "manifest.json"
DEFAULT_STAGE104_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage104_matched_packet_execution_package" / "manifest.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage105_independent_rerun_protocol"
MIN_INDEPENDENT_WINDOWS_PER_PROVIDER = 2
MIN_HOURS_BETWEEN_WINDOWS = 24
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _template_records(stage104: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not stage104:
        return []
    paths = [Path(str(path)) for path in stage104.get("template_paths", [])]
    records = []
    for path in paths:
        payload = _load_json(path)
        if payload is None:
            records.append({"template_path": str(path.as_posix()), "missing": True})
            continue
        records.append(
            {
                "template_path": str(path.as_posix()),
                "packet_id": payload.get("packet_id"),
                "provider": payload.get("provider"),
                "source_lane_id": payload.get("source_lane_id"),
                "encoding_family": payload.get("encoding_family"),
                "circuit_template": payload.get("circuit_template"),
                "row_count": len(payload.get("raw_counts_by_row", [])),
                "shot_count": payload.get("shot_count"),
                "missing": False,
            }
        )
    return records


def _providers(records: list[dict[str, Any]]) -> list[str]:
    return sorted({str(record["provider"]) for record in records if not record.get("missing") and record.get("provider")})


def _window_id(provider: str, index: int) -> str:
    return f"{provider}__independent_window_{index:02d}"


def build_rerun_windows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    windows = []
    for provider in _providers(records):
        provider_templates = [record for record in records if record.get("provider") == provider and not record.get("missing")]
        for index in range(MIN_INDEPENDENT_WINDOWS_PER_PROVIDER):
            windows.append(
                {
                    "window_id": _window_id(provider, index),
                    "provider": provider,
                    "window_index": index,
                    "minimum_separation_from_previous_window_hours": 0 if index == 0 else MIN_HOURS_BETWEEN_WINDOWS,
                    "requires_fresh_stage101_calibration": True,
                    "requires_backend_metadata": True,
                    "requires_calibration_timestamp": True,
                    "requires_all_provider_packet_templates": True,
                    "packet_template_count": len(provider_templates),
                    "packet_templates": [
                        {
                            "packet_id": record["packet_id"],
                            "template_path": record["template_path"],
                            "source_lane_id": record["source_lane_id"],
                            "encoding_family": record["encoding_family"],
                            "circuit_template": record["circuit_template"],
                            "row_count": record["row_count"],
                            "shot_count": record["shot_count"],
                        }
                        for record in provider_templates
                    ],
                    "status": "execution_required",
                    "missing_evidence": [
                        "fresh Stage 101 calibration execution JSON for this provider/backend/date",
                        "filled Stage 104 packet execution templates for every packet in this provider window",
                        "backend metadata and calibration timestamp for this window",
                        "Stage 103 metrics recomputed for this window",
                    ],
                }
            )
    return windows


def run_stage105_protocol(
    *,
    stage101_results_path: Path = DEFAULT_STAGE101_RESULTS,
    stage103_manifest_path: Path = DEFAULT_STAGE103_MANIFEST,
    stage104_manifest_path: Path = DEFAULT_STAGE104_MANIFEST,
) -> dict[str, Any]:
    stage101 = _load_json(stage101_results_path)
    stage103 = _load_json(stage103_manifest_path)
    stage104 = _load_json(stage104_manifest_path)
    sources = [
        (stage101_results_path, stage101),
        (stage103_manifest_path, stage103),
        (stage104_manifest_path, stage104),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    records = _template_records(stage104)
    missing_templates = [record["template_path"] for record in records if record.get("missing")]
    windows = build_rerun_windows(records)
    providers = _providers(records)
    expected_window_count = len(providers) * MIN_INDEPENDENT_WINDOWS_PER_PROVIDER
    complete_protocol = (
        not missing_sources
        and not missing_templates
        and bool(providers)
        and len(windows) == expected_window_count
        and stage104 is not None
        and stage104.get("template_count") == 20
    )
    return {
        "schema_version": STAGE105_SCHEMA_VERSION,
        "stage": "stage105_independent_rerun_protocol",
        "status": "completed" if complete_protocol else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "INDEPENDENT_RERUN_PROTOCOL_PREREGISTERED_EXECUTION_REQUIRED"
            if complete_protocol
            else "INDEPENDENT_RERUN_PROTOCOL_INCOMPLETE"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "missing_template_artifacts": missing_templates,
        "stage101_known_state_calibration_pass": bool(stage101 and stage101.get("known_state_calibration_pass") is True),
        "stage103_decision": stage103.get("decision") if stage103 else None,
        "stage104_decision": stage104.get("decision") if stage104 else None,
        "providers": providers,
        "provider_count": len(providers),
        "packet_template_count": len([record for record in records if not record.get("missing")]),
        "min_independent_windows_per_provider": MIN_INDEPENDENT_WINDOWS_PER_PROVIDER,
        "min_hours_between_windows": MIN_HOURS_BETWEEN_WINDOWS,
        "expected_window_count": expected_window_count,
        "window_count": len(windows),
        "rerun_windows": windows,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "aggregation_rule": {
            "window_level": "Compute Stage 103 metrics independently inside each provider/backend/date calibration window.",
            "claim_level": (
                "A PhaseWrap robustness advantage may only be described as replicated if the Stage 103 advantage rule "
                "holds in every independent window for the same provider, source lane, and circuit template."
            ),
            "reporting": [
                "report per-window metric tables",
                "report across-window median and range for PhaseWrap and comparator errors",
                "report failures, missing packets, calibration failures, and queue/backend metadata without exclusion",
            ],
        },
        "claim_boundary": {
            "supported": [
                "a preregistered independent rerun protocol for the matched noisy-hardware comparison",
                "a minimum two-window provider/backend/date calibration requirement",
                "an aggregation rule preventing single-window noisy-hardware advantage claims",
            ],
            "excluded": [
                "completed independent reruns",
                "real hardware evidence",
                "a PhaseWrap robustness advantage claim",
                "provider-wide robustness beyond recorded windows",
            ],
        },
        "next_gate": (
            "Run Stage 101 calibration and all Stage 104 matched packet executions in each independent provider window, "
            "then recompute Stage 103 metrics per window and aggregate only under the Stage 105 rule."
        ),
    }


def write_stage105_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "missing_template_artifacts": result["missing_template_artifacts"],
        "providers": result["providers"],
        "packet_template_count": result["packet_template_count"],
        "min_independent_windows_per_provider": result["min_independent_windows_per_provider"],
        "min_hours_between_windows": result["min_hours_between_windows"],
        "expected_window_count": result["expected_window_count"],
        "window_count": result["window_count"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "aggregation_rule": result["aggregation_rule"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "rerun_windows_path": str((output_dir / "rerun_windows.json").as_posix()),
        "claim_boundary": result["claim_boundary"],
        "next_gate": result["next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "rerun_windows": str(output_dir / "rerun_windows.json"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "rerun_windows.json").write_text(json.dumps(result["rerun_windows"], indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "window_id",
                "provider",
                "window_index",
                "minimum_separation_from_previous_window_hours",
                "packet_template_count",
                "status",
                "missing_evidence",
            ),
        )
        writer.writeheader()
        for window in result["rerun_windows"]:
            writer.writerow(
                {
                    "window_id": window["window_id"],
                    "provider": window["provider"],
                    "window_index": window["window_index"],
                    "minimum_separation_from_previous_window_hours": window["minimum_separation_from_previous_window_hours"],
                    "packet_template_count": window["packet_template_count"],
                    "status": window["status"],
                    "missing_evidence": "; ".join(window["missing_evidence"]),
                }
            )
    return paths


def print_stage105_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"providers: {', '.join(result['providers'])}")
    print(f"window_count: {result['window_count']}")
    print(f"next_gate: {result['next_gate']}")
