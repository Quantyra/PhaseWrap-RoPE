from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE168_SCHEMA_VERSION = "qrope_stage168_real_source_seed_expansion_plan_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE4_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage4_preregistered_replication_packets" / "manifest.json"
DEFAULT_STAGE167_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage167_expanded_simulated_seed_stress_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage168_real_source_seed_expansion_plan"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
IBM_PROVIDER = "ibm_runtime"
REQUIRED_FAMILIES = ("two_qubit_zz_expectation_phase_wrap_v1", "two_qubit_cx_parity_phase_wrap_v2")
REQUIRED_REAL_IBM_SEEDS_FOR_BROADENED_SCOPE = 2
RECOMMENDED_ADDITIONAL_IBM_SEEDS = (577, 1618, 2718)
IBM_ROWS = 16
IBM_SHOTS = 4096


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _current_provider_seed_records(stage4: dict[str, Any] | None, provider: str) -> list[dict[str, Any]]:
    if not isinstance(stage4, dict):
        return []
    by_seed: dict[int, dict[str, Any]] = {}
    for record in stage4.get("records", []):
        if not isinstance(record, dict) or record.get("provider") != provider:
            continue
        seed = int(record.get("seed"))
        seed_record = by_seed.setdefault(
            seed,
            {
                "provider": provider,
                "seed": seed,
                "families": [],
                "lane_ids": [],
                "row_counts": [],
                "shot_counts": [],
            },
        )
        seed_record["families"].append(record.get("family"))
        seed_record["lane_ids"].append(record.get("lane_id"))
        seed_record["row_counts"].append(record.get("rows"))
        seed_record["shot_counts"].append(record.get("shots"))
    records = []
    for seed_record in by_seed.values():
        families = sorted(set(str(item) for item in seed_record["families"]))
        records.append(
            {
                **seed_record,
                "families": families,
                "lane_ids": sorted(set(str(item) for item in seed_record["lane_ids"])),
                "row_counts": sorted(set(int(item) for item in seed_record["row_counts"] if item is not None)),
                "shot_counts": sorted(set(int(item) for item in seed_record["shot_counts"] if item is not None)),
                "complete_family_pair": all(family in families for family in REQUIRED_FAMILIES),
            }
        )
    return sorted(records, key=lambda record: record["seed"])


def _missing_seed_requests(current_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    complete_seed_count = sum(1 for record in current_records if record["complete_family_pair"] is True)
    missing_count = max(0, REQUIRED_REAL_IBM_SEEDS_FOR_BROADENED_SCOPE - complete_seed_count)
    current_seeds = {int(record["seed"]) for record in current_records}
    requests = []
    for seed in RECOMMENDED_ADDITIONAL_IBM_SEEDS:
        if len(requests) >= missing_count:
            break
        if seed in current_seeds:
            continue
        for family, lane_kind in (
            ("two_qubit_zz_expectation_phase_wrap_v1", "product"),
            ("two_qubit_cx_parity_phase_wrap_v2", "cx"),
        ):
            requests.append(
                {
                    "provider": IBM_PROVIDER,
                    "seed": seed,
                    "family": family,
                    "lane_id": f"ibm_{lane_kind}_seed{seed}_rows{IBM_ROWS}_shots{IBM_SHOTS}",
                    "row_count": IBM_ROWS,
                    "shot_count": IBM_SHOTS,
                    "execution_status": "not_submitted",
                }
            )
    return requests


def run_stage168_expansion_plan(
    *,
    stage4_manifest_path: Path = DEFAULT_STAGE4_MANIFEST,
    stage167_results_path: Path = DEFAULT_STAGE167_RESULTS,
) -> dict[str, Any]:
    stage4 = _load_json(stage4_manifest_path)
    stage167 = _load_json(stage167_results_path)
    sources = [(stage4_manifest_path, stage4), (stage167_results_path, stage167)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    current_records = _current_provider_seed_records(stage4, IBM_PROVIDER)
    complete_seed_count = sum(1 for record in current_records if record["complete_family_pair"] is True)
    missing_real_seed_count = max(0, REQUIRED_REAL_IBM_SEEDS_FOR_BROADENED_SCOPE - complete_seed_count)
    expansion_requests = _missing_seed_requests(current_records)
    synthetic_supported_broadening = (
        isinstance(stage167, dict)
        and stage167.get("decision") == "EXPANDED_SIMULATED_SEED_STRESS_SUPPORTS_BROADENED_HARDWARE_PROBE"
    )
    ready_for_broadened_scope = bool(not missing_sources and missing_real_seed_count == 0 and synthetic_supported_broadening)
    if missing_sources:
        decision = "REAL_SOURCE_SEED_EXPANSION_PLAN_INCOMPLETE"
    elif ready_for_broadened_scope:
        decision = "REAL_SOURCE_SEED_EXPANSION_NOT_REQUIRED_FOR_BROADENED_SCOPE"
    else:
        decision = "REAL_SOURCE_SEED_EXPANSION_REQUIRED_BEFORE_BROADENED_SCOPE"
    blockers = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if missing_real_seed_count:
        blockers.append("real_ibm_seed_pair_count_below_broadened_scope_threshold")
    if not synthetic_supported_broadening:
        blockers.append("stage167_synthetic_stress_did_not_support_broadened_scope")
    return {
        "schema_version": STAGE168_SCHEMA_VERSION,
        "stage": "stage168_real_source_seed_expansion_plan",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "provider": IBM_PROVIDER,
        "required_families": list(REQUIRED_FAMILIES),
        "required_real_ibm_seed_pair_count_for_broadened_scope": REQUIRED_REAL_IBM_SEEDS_FOR_BROADENED_SCOPE,
        "current_real_ibm_seed_pair_count": complete_seed_count,
        "missing_real_ibm_seed_pair_count": missing_real_seed_count,
        "current_real_ibm_seed_records": current_records,
        "recommended_expansion_requests": expansion_requests,
        "stage167_decision": stage167.get("decision") if isinstance(stage167, dict) else None,
        "stage167_stable_seed_count": stage167.get("stable_seed_count") if isinstance(stage167, dict) else None,
        "stage167_stable_noise_model_count": stage167.get("stable_noise_model_count") if isinstance(stage167, dict) else None,
        "blockers": sorted(set(blockers)),
        "simulated_only": True,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "no-submit plan for the real frozen IBM source seeds needed before broadened simulated or hardware scope",
                "count of current complete IBM product/CX seed pairs in Stage4 preregistered packets",
                "recommended additional IBM source lanes to freeze before broadening beyond the current targeted probe",
            ],
            "excluded": [
                "new source packet generation",
                "hardware job submission",
                "provider credentials or secret values",
                "real noisy-hardware evidence",
                "a broad robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Keep the live path scoped to the current targeted IBM probe unless additional real IBM product/CX seed pairs "
            "are frozen and rerun through Stage99/100/153/165/166/167."
        ),
    }


def write_stage168_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "provider": result["provider"],
        "required_real_ibm_seed_pair_count_for_broadened_scope": result[
            "required_real_ibm_seed_pair_count_for_broadened_scope"
        ],
        "current_real_ibm_seed_pair_count": result["current_real_ibm_seed_pair_count"],
        "missing_real_ibm_seed_pair_count": result["missing_real_ibm_seed_pair_count"],
        "stage167_decision": result["stage167_decision"],
        "blockers": result["blockers"],
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
            fieldnames=("provider", "seed", "family", "lane_id", "row_count", "shot_count", "execution_status"),
        )
        writer.writeheader()
        for record in result["recommended_expansion_requests"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage168_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"current_real_ibm_seed_pair_count: {result['current_real_ibm_seed_pair_count']}")
    print(f"missing_real_ibm_seed_pair_count: {result['missing_real_ibm_seed_pair_count']}")
    print(f"expansion_request_count: {len(result['recommended_expansion_requests'])}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
