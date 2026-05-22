from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


STAGE166_SCHEMA_VERSION = "qrope_stage166_simulated_evidence_sufficiency_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE99_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage99_matched_fixed_width_encoding_packets" / "manifest.json"
DEFAULT_STAGE100_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage100_matched_cx_encoding_packets" / "manifest.json"
DEFAULT_STAGE153_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage153_simulated_noise_rehearsal" / "results.json"
DEFAULT_STAGE165_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage165_simulated_noise_margin_stability_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage166_simulated_evidence_sufficiency_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE165_STABLE_GO = "SIMULATED_NOISE_STABLE_TARGETED_HARDWARE_PROBE_RECOMMENDED"
MIN_STABLE_TEMPLATE_COUNT_FOR_TARGETED_PROBE = 2
MIN_STABLE_SEED_COUNT_FOR_BROAD_SIMULATED_CLAIM = 2
MIN_STABLE_NOISE_MODEL_COUNT_FOR_BROAD_SIMULATED_CLAIM = 2


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _seed_from_lane(source_lane_id: str) -> str:
    match = re.search(r"seed(\d+)", source_lane_id)
    return match.group(1) if match else ""


def _manifest_packet_lanes(manifest: dict[str, Any] | None) -> set[str]:
    if not isinstance(manifest, dict):
        return set()
    lanes = set()
    for path in manifest.get("packet_paths", []):
        name = Path(str(path)).stem
        lane, _, _family = name.partition("__")
        if lane:
            lanes.add(lane)
    return lanes


def _stable_target_records(stage165: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(stage165, dict):
        return []
    return [record for record in stage165.get("target_records", []) if isinstance(record, dict) and record.get("stable_target") is True]


def _provider_records(stage165: dict[str, Any] | None) -> list[dict[str, Any]]:
    stable_targets = _stable_target_records(stage165)
    providers = sorted({str(record.get("provider")) for record in stable_targets})
    records = []
    for provider in providers:
        provider_targets = [record for record in stable_targets if record.get("provider") == provider]
        stable_templates = sorted({str(record.get("circuit_template")) for record in provider_targets})
        stable_noise_models = sorted({str(record.get("noise_model_id")) for record in provider_targets})
        stable_lanes = sorted({str(record.get("source_lane_id")) for record in provider_targets})
        stable_seeds = sorted({seed for seed in (_seed_from_lane(lane) for lane in stable_lanes) if seed})
        targeted_probe_ready = len(stable_templates) >= MIN_STABLE_TEMPLATE_COUNT_FOR_TARGETED_PROBE
        broad_simulated_claim_ready = (
            targeted_probe_ready
            and len(stable_seeds) >= MIN_STABLE_SEED_COUNT_FOR_BROAD_SIMULATED_CLAIM
            and len(stable_noise_models) >= MIN_STABLE_NOISE_MODEL_COUNT_FOR_BROAD_SIMULATED_CLAIM
        )
        records.append(
            {
                "provider": provider,
                "stable_target_count": len(provider_targets),
                "stable_template_count": len(stable_templates),
                "stable_templates": stable_templates,
                "stable_noise_model_count": len(stable_noise_models),
                "stable_noise_models": stable_noise_models,
                "stable_seed_count": len(stable_seeds),
                "stable_seeds": stable_seeds,
                "stable_source_lanes": stable_lanes,
                "targeted_probe_ready": targeted_probe_ready,
                "broad_simulated_claim_ready": broad_simulated_claim_ready,
                "broad_claim_blockers": []
                if broad_simulated_claim_ready
                else [
                    item
                    for item, blocked in (
                        ("stable_template_count_below_targeted_probe_threshold", not targeted_probe_ready),
                        ("stable_seed_count_below_broad_claim_threshold", len(stable_seeds) < MIN_STABLE_SEED_COUNT_FOR_BROAD_SIMULATED_CLAIM),
                        (
                            "stable_noise_model_count_below_broad_claim_threshold",
                            len(stable_noise_models) < MIN_STABLE_NOISE_MODEL_COUNT_FOR_BROAD_SIMULATED_CLAIM,
                        ),
                    )
                    if blocked
                ],
            }
        )
    return records


def run_stage166_sufficiency_audit(
    *,
    stage99_manifest_path: Path = DEFAULT_STAGE99_MANIFEST,
    stage100_manifest_path: Path = DEFAULT_STAGE100_MANIFEST,
    stage153_results_path: Path = DEFAULT_STAGE153_RESULTS,
    stage165_results_path: Path = DEFAULT_STAGE165_RESULTS,
) -> dict[str, Any]:
    stage99 = _load_json(stage99_manifest_path)
    stage100 = _load_json(stage100_manifest_path)
    stage153 = _load_json(stage153_results_path)
    stage165 = _load_json(stage165_results_path)
    sources = [
        (stage99_manifest_path, stage99),
        (stage100_manifest_path, stage100),
        (stage153_results_path, stage153),
        (stage165_results_path, stage165),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    product_lanes = _manifest_packet_lanes(stage99)
    cx_lanes = _manifest_packet_lanes(stage100)
    provider_records = _provider_records(stage165)
    targeted_providers = [record["provider"] for record in provider_records if record["targeted_probe_ready"] is True]
    broad_claim_providers = [record["provider"] for record in provider_records if record["broad_simulated_claim_ready"] is True]
    blockers = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if isinstance(stage165, dict) and stage165.get("decision") != STAGE165_STABLE_GO:
        blockers.append("stage165_stable_targeted_go_missing")
    if not targeted_providers:
        blockers.append("no_provider_with_two_template_stable_signal")
    if broad_claim_providers:
        decision = "SIMULATED_EVIDENCE_BROAD_CLAIM_READY_PENDING_HARDWARE"
    elif targeted_providers and not blockers:
        decision = "SIMULATED_EVIDENCE_TARGETED_PROBE_READY_BROAD_CLAIM_INSUFFICIENT"
    elif missing_sources:
        decision = "SIMULATED_EVIDENCE_SUFFICIENCY_AUDIT_INCOMPLETE"
    else:
        decision = "SIMULATED_EVIDENCE_TARGETED_PROBE_NOT_SUPPORTED_YET"
    return {
        "schema_version": STAGE166_SCHEMA_VERSION,
        "stage": "stage166_simulated_evidence_sufficiency_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage153_decision": stage153.get("decision") if isinstance(stage153, dict) else None,
        "stage165_decision": stage165.get("decision") if isinstance(stage165, dict) else None,
        "product_lane_count": len(product_lanes),
        "cx_lane_count": len(cx_lanes),
        "product_lanes": sorted(product_lanes),
        "cx_lanes": sorted(cx_lanes),
        "stable_provider_records": provider_records,
        "targeted_probe_ready_providers": targeted_providers,
        "broad_simulated_claim_ready_providers": broad_claim_providers,
        "sufficiency_thresholds": {
            "min_stable_template_count_for_targeted_probe": MIN_STABLE_TEMPLATE_COUNT_FOR_TARGETED_PROBE,
            "min_stable_seed_count_for_broad_simulated_claim": MIN_STABLE_SEED_COUNT_FOR_BROAD_SIMULATED_CLAIM,
            "min_stable_noise_model_count_for_broad_simulated_claim": MIN_STABLE_NOISE_MODEL_COUNT_FOR_BROAD_SIMULATED_CLAIM,
        },
        "blockers": sorted(set(blockers)),
        "simulated_only": True,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "simulated-only sufficiency audit separating targeted hardware-probe readiness from broad simulated robustness",
                "provider-level count of stable templates, seeds, source lanes, and noise models from Stage165",
                "explicit evidence that the current IBM signal is a narrow targeted-probe signal, not a broad claim",
            ],
            "excluded": [
                "real noisy-hardware evidence",
                "provider credit or queue availability validation",
                "hardware job submission",
                "a publication-ready noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "For a targeted hardware probe, pause and resolve IBM credit/provider state together before live execution. "
            "For a broader simulated claim, add independent seeds/noise models before hardware spend."
        ),
    }


def write_stage166_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage153_decision": result["stage153_decision"],
        "stage165_decision": result["stage165_decision"],
        "product_lane_count": result["product_lane_count"],
        "cx_lane_count": result["cx_lane_count"],
        "targeted_probe_ready_providers": result["targeted_probe_ready_providers"],
        "broad_simulated_claim_ready_providers": result["broad_simulated_claim_ready_providers"],
        "sufficiency_thresholds": result["sufficiency_thresholds"],
        "blockers": result["blockers"],
        "simulated_only": result["simulated_only"],
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
            fieldnames=(
                "provider",
                "stable_target_count",
                "stable_template_count",
                "stable_seed_count",
                "stable_noise_model_count",
                "targeted_probe_ready",
                "broad_simulated_claim_ready",
                "broad_claim_blockers",
            ),
        )
        writer.writeheader()
        for record in result["stable_provider_records"]:
            writer.writerow(
                {
                    **{field: record.get(field) for field in writer.fieldnames if field != "broad_claim_blockers"},
                    "broad_claim_blockers": "; ".join(record.get("broad_claim_blockers", [])),
                }
            )
    return paths


def print_stage166_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"targeted_probe_ready_providers: {', '.join(result['targeted_probe_ready_providers'])}")
    print(f"broad_simulated_claim_ready_providers: {', '.join(result['broad_simulated_claim_ready_providers'])}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
