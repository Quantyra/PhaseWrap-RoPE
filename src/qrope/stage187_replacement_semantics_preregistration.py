from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage186_target_control_semantics_audit import DEFAULT_OUTPUT_DIR as STAGE186_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE187_SCHEMA_VERSION = "qrope_stage187_replacement_semantics_preregistration_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE186_RESULTS = STAGE186_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage187_replacement_semantics_preregistration"
STAGE186_REVISION_REQUIRED = "TARGET_CONTROL_SEMANTICS_REVISION_REQUIRED_BEFORE_HARDWARE"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _replacement_semantics() -> dict[str, Any]:
    return {
        "semantics_id": "matched_nonzero_null_noise_sensitivity_v1",
        "purpose": (
            "replace the zero-component no-position raw-MAE hardware gate with a fixed-width control and metric surface "
            "that exposes every family, including the null, to nonzero IBM-style shrink/readout"
        ),
        "fixed_width_constraints": {
            "measured_qubits": 2,
            "active_qubits": 2,
            "required_templates": ["two_ry_product_state_z_readout_v1", "two_ry_cx_parity_z_readout_v1"],
            "qubit_count_may_change": False,
        },
        "family_requirements": [
            "phasewrap",
            "rope_like",
            "sinusoidal_like",
            "alibi_like",
            "matched_nonzero_null_control",
        ],
        "control_definition": {
            "control_family": "matched_nonzero_null_control",
            "component_policy": (
                "for each source row, assign deterministic nonzero components with the same absolute exposure envelope as the "
                "positional families but with row-wise signs or pairing independent of positional delta"
            ),
            "allowed_forms": [
                "paired_delta_null: components from a sign-balanced permutation of source deltas within the same lane",
                "matched_exposure_null: components with the same absolute component histogram as PhaseWrap but row-permuted by frozen hash",
            ],
            "disallowed_forms": [
                "zero-zero component control",
                "dropping the no-position/control comparator",
                "choosing control components after seeing simulated or hardware wins",
            ],
        },
        "primary_metric": {
            "metric_id": "normalized_noise_sensitivity_delta_v1",
            "definition": (
                "compare each family by the noise-induced change in score relative to its own ideal, normalized by that row's "
                "nonzero component exposure; aggregate as mean absolute normalized shrink error"
            ),
            "required_reported_metrics": [
                "mean_absolute_score_error",
                "normalized_noise_sensitivity_delta",
                "slope_retention",
                "rank_retention",
                "matched_null_control_margin",
            ],
            "reason": (
                "separates task score distortion from the trivial stability of a zero ideal score, so a control can only win by "
                "being robust under comparable nonzero exposure"
            ),
        },
        "hardware_reopen_thresholds": {
            "min_matched_null_margin_shot_quanta": 2.0,
            "min_best_positional_margin_shot_quanta": 2.0,
            "min_stable_templates": 2,
            "min_independent_seed_pairs": 2,
            "required_primary_noise_models": ["ibm_backend_median_stochastic", "ibm_backend_p75_stochastic"],
            "coherent_proxy_only_may_reopen_hardware": False,
        },
        "selection_firewalls": [
            "replacement semantics must be frozen before Stage188 packet generation",
            "source row sets must be identical across all families within each lane",
            "live hardware results may not be used to tune controls, thresholds, source rows, or metrics",
            "any IBM hardware run remains disallowed until a later simulated gate passes all reopen thresholds",
        ],
    }


def run_stage187_replacement_semantics_preregistration(
    *,
    stage186_results_path: Path = DEFAULT_STAGE186_RESULTS,
) -> dict[str, Any]:
    stage186 = _load_json(stage186_results_path)
    missing_sources = [str(stage186_results_path.as_posix())] if not isinstance(stage186, dict) else []
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage186, dict) and stage186.get("decision") != STAGE186_REVISION_REQUIRED:
        blockers.append("stage186_revision_not_required")

    semantics = _replacement_semantics()
    if blockers:
        decision = "REPLACEMENT_SEMANTICS_PREREGISTRATION_INCOMPLETE"
    else:
        decision = "REPLACEMENT_SEMANTICS_PREREGISTERED_READY_FOR_PACKET_SCREEN"

    return {
        "schema_version": STAGE187_SCHEMA_VERSION,
        "stage": "stage187_replacement_semantics_preregistration",
        "status": "completed" if not blockers else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage186_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "semantics": semantics,
        "simulated_only": True,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "hardware_path_status": "current_ibm_328_job_run_remains_archived",
        "claim_boundary": {
            "supported": [
                "replacement target/control and metric semantics are preregistered after the Stage186 audit",
                "the next packet screen must use matched nonzero null/control exposure rather than zero-component control",
                "hardware remains disallowed until a later IBM-informed simulation gate passes the preregistered thresholds",
            ],
            "excluded": [
                "new packet generation",
                "simulated robustness result under the replacement semantics",
                "hardware job submission",
                "a final noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Generate fixed-width replacement-semantics packets and run an IBM-informed simulated screen against the "
            "preregistered normalized noise-sensitivity and matched-null margins."
        ),
    }


def write_stage187_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_keys = (
        "schema_version",
        "stage",
        "status",
        "objective",
        "decision",
        "source_artifacts",
        "missing_source_artifacts",
        "blockers",
        "semantics",
        "simulated_only",
        "no_hardware_submission",
        "provider_credentials_required",
        "secret_values_recorded",
        "runnable_commands_recorded",
        "hardware_path_status",
        "claim_boundary",
        "next_gate",
    )
    manifest = {key: result[key] for key in manifest_keys}
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
            fieldnames=("semantics_id", "control_family", "primary_metric_id", "min_independent_seed_pairs", "no_hardware_submission"),
        )
        writer.writeheader()
        writer.writerow(
            {
                "semantics_id": result["semantics"]["semantics_id"],
                "control_family": result["semantics"]["control_definition"]["control_family"],
                "primary_metric_id": result["semantics"]["primary_metric"]["metric_id"],
                "min_independent_seed_pairs": result["semantics"]["hardware_reopen_thresholds"]["min_independent_seed_pairs"],
                "no_hardware_submission": result["no_hardware_submission"],
            }
        )
    return paths


def print_stage187_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"semantics_id: {result['semantics']['semantics_id']}")
    print(f"control_family: {result['semantics']['control_definition']['control_family']}")
    print(f"primary_metric_id: {result['semantics']['primary_metric']['metric_id']}")
    print(f"next_gate: {result['next_gate']}")
