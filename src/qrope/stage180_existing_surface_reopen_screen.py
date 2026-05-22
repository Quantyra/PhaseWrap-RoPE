from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

from qrope.stage153_simulated_noise_rehearsal import DEFAULT_STAGE100_MANIFEST, DEFAULT_STAGE99_MANIFEST, _comparison_summary, _metric_records
from qrope.stage177_ibm_backend_informed_noise_probe import (
    DEFAULT_OUTPUT_DIR as STAGE177_OUTPUT_DIR,
    MIN_MARGIN_SHOT_QUANTA,
    PRIMARY_MODEL_IDS,
    _enrich_summary,
)
from qrope.stage179_current_ibm_hardware_path_disposition import DEFAULT_OUTPUT_DIR as STAGE179_OUTPUT_DIR


STAGE180_SCHEMA_VERSION = "qrope_stage180_existing_surface_reopen_screen_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE177_RESULTS = STAGE177_OUTPUT_DIR / "results.json"
DEFAULT_STAGE179_RESULTS = STAGE179_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage180_existing_surface_reopen_screen"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE179_ARCHIVE = "CURRENT_IBM_HARDWARE_PATH_ARCHIVE_RECOMMENDED"
SOURCE_LANE_RE = re.compile(r"^(?P<provider>.+?)_(?P<template>product|cx)_seed(?P<seed>\d+)_")


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _packet_paths(manifest_path: Path) -> list[Path]:
    manifest = _load_json(manifest_path)
    if not isinstance(manifest, dict):
        return []
    return [Path(str(path)) for path in manifest.get("packet_paths", [])]


def _primary_noise_models(stage177: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(
        model
        for model in stage177.get("noise_models", [])
        if isinstance(model, dict) and str(model.get("noise_model_id")) in PRIMARY_MODEL_IDS
    )


def _lane_parts(source_lane_id: str, provider: str) -> dict[str, str]:
    match = SOURCE_LANE_RE.match(source_lane_id)
    if not match:
        return {"provider_family": provider, "template_kind": "", "seed": ""}
    return {
        "provider_family": match.group("provider"),
        "template_kind": match.group("template"),
        "seed": match.group("seed"),
    }


def _candidate_records(comparison_summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for record in comparison_summary:
        lane = _lane_parts(str(record.get("source_lane_id")), str(record.get("provider")))
        key = (
            str(record.get("noise_model_id")),
            lane["provider_family"] or str(record.get("provider")),
            lane["seed"],
        )
        groups.setdefault(key, []).append({**record, **lane})

    records = []
    for (noise_model_id, provider_family, seed), group in sorted(groups.items()):
        stable = [record for record in group if record.get("stable_strict_target") is True]
        stable_templates = sorted({str(record.get("circuit_template")) for record in stable})
        stable_lanes = sorted({str(record.get("source_lane_id")) for record in stable})
        records.append(
            {
                "noise_model_id": noise_model_id,
                "provider_family": provider_family,
                "seed": seed,
                "comparison_group_count": len(group),
                "stable_target_count": len(stable),
                "stable_template_count": len(stable_templates),
                "stable_templates": stable_templates,
                "stable_lanes": stable_lanes,
                "min_positional_margin_shot_quanta": min(
                    (float(record.get("positional_margin_shot_quanta")) for record in group if record.get("positional_margin_shot_quanta") is not None),
                    default=None,
                ),
                "min_control_margin_shot_quanta": min(
                    (float(record.get("control_margin_shot_quanta")) for record in group if record.get("control_margin_shot_quanta") is not None),
                    default=None,
                ),
                "reopen_candidate": len(stable_templates) >= 2,
            }
        )
    return records


def run_stage180_existing_surface_reopen_screen(
    *,
    stage177_results_path: Path = DEFAULT_STAGE177_RESULTS,
    stage179_results_path: Path = DEFAULT_STAGE179_RESULTS,
    stage99_manifest_path: Path = DEFAULT_STAGE99_MANIFEST,
    stage100_manifest_path: Path = DEFAULT_STAGE100_MANIFEST,
) -> dict[str, Any]:
    stage177 = _load_json(stage177_results_path)
    stage179 = _load_json(stage179_results_path)
    sources = [
        (stage177_results_path, stage177),
        (stage179_results_path, stage179),
        (stage99_manifest_path, _load_json(stage99_manifest_path)),
        (stage100_manifest_path, _load_json(stage100_manifest_path)),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage179, dict) and stage179.get("decision") != STAGE179_ARCHIVE:
        blockers.append("stage179_current_ibm_path_not_archived")
    if not isinstance(stage177, dict) or not _primary_noise_models(stage177):
        blockers.append("stage177_primary_models_missing")

    packet_paths = _packet_paths(stage99_manifest_path) + _packet_paths(stage100_manifest_path)
    noise_models = _primary_noise_models(stage177) if isinstance(stage177, dict) and not blockers else ()
    metric_records, missing_packets = _metric_records(packet_paths, noise_models) if noise_models else ([], [])
    if missing_packets:
        blockers.append("missing_matched_packets")

    comparison_summary = _enrich_summary(_comparison_summary(metric_records), metric_records, set()) if metric_records else []
    candidate_records = _candidate_records(comparison_summary)
    reopen_candidates = [record for record in candidate_records if record.get("reopen_candidate") is True]
    if blockers:
        decision = "EXISTING_SURFACE_REOPEN_SCREEN_INCOMPLETE"
    elif reopen_candidates:
        decision = "EXISTING_SURFACE_REOPEN_CANDIDATES_FOUND"
    else:
        decision = "EXISTING_SURFACE_HAS_NO_IBM_INFORMED_REOPEN_CANDIDATE"

    return {
        "schema_version": STAGE180_SCHEMA_VERSION,
        "stage": "stage180_existing_surface_reopen_screen",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "primary_noise_model_ids": [model["noise_model_id"] for model in noise_models],
        "packet_count": len(packet_paths),
        "comparison_group_count": len(comparison_summary),
        "candidate_group_count": len(candidate_records),
        "reopen_candidate_count": len(reopen_candidates),
        "reopen_candidates": reopen_candidates,
        "candidate_records": candidate_records,
        "simulated_only": True,
        "ibm_backend_properties_informed": bool(noise_models),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "stability_thresholds": {
            "min_positional_margin_shot_quanta": MIN_MARGIN_SHOT_QUANTA,
            "min_control_margin_shot_quanta": MIN_MARGIN_SHOT_QUANTA,
            "min_stable_template_count_for_reopen": 2,
        },
        "claim_boundary": {
            "supported": [
                "no-submit screen of the existing frozen fixed-width packet surface after archiving the current IBM run",
                "evidence for whether any existing provider/seed pair can reopen the hardware path under IBM-informed primary noise",
                "decision support for moving from run selection to target/circuit redesign",
            ],
            "excluded": [
                "hardware job submission",
                "new packet or circuit-family generation",
                "a noisy-hardware robustness or auditability conclusion",
                "a claim that all possible redesigned targets have failed",
            ],
        },
        "next_gate": (
            "If no existing-surface reopen candidate is found, the next progress path is target/circuit redesign rather than "
            "selecting another already frozen lane."
        ),
    }


def write_stage180_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        key: result[key]
        for key in (
            "schema_version",
            "stage",
            "status",
            "objective",
            "decision",
            "source_artifacts",
            "missing_source_artifacts",
            "blockers",
            "primary_noise_model_ids",
            "packet_count",
            "comparison_group_count",
            "candidate_group_count",
            "reopen_candidate_count",
            "reopen_candidates",
            "simulated_only",
            "ibm_backend_properties_informed",
            "no_hardware_submission",
            "provider_credentials_required",
            "secret_values_recorded",
            "runnable_commands_recorded",
            "stability_thresholds",
            "claim_boundary",
            "next_gate",
        )
    }
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
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
            fieldnames=(
                "noise_model_id",
                "provider_family",
                "seed",
                "comparison_group_count",
                "stable_target_count",
                "stable_template_count",
                "min_positional_margin_shot_quanta",
                "min_control_margin_shot_quanta",
                "reopen_candidate",
            ),
        )
        writer.writeheader()
        for record in result["candidate_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage180_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"reopen_candidate_count: {result['reopen_candidate_count']}")
    print(f"next_gate: {result['next_gate']}")
