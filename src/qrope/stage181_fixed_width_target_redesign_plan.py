from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE181_SCHEMA_VERSION = "qrope_stage181_fixed_width_target_redesign_plan_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE177_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage177_ibm_backend_informed_noise_probe" / "results.json"
DEFAULT_STAGE179_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage179_current_ibm_hardware_path_disposition" / "results.json"
DEFAULT_STAGE180_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage180_existing_surface_reopen_screen" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage181_fixed_width_target_redesign_plan"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE179_ARCHIVE = "CURRENT_IBM_HARDWARE_PATH_ARCHIVE_RECOMMENDED"
STAGE180_NO_EXISTING_REOPEN = "EXISTING_SURFACE_HAS_NO_IBM_INFORMED_REOPEN_CANDIDATE"
MIN_MARGIN_SHOT_QUANTA = 2.0
MIN_STABLE_TEMPLATES = 2
MIN_INDEPENDENT_SEEDS = 2
MIN_PRIMARY_NOISE_MODELS = 2


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _decision(payload: Any) -> str | None:
    return str(payload.get("decision")) if isinstance(payload, dict) and payload.get("decision") else None


def _design_families() -> list[dict[str, Any]]:
    return [
        {
            "family_id": "pw_balanced_phase_window_v1",
            "hypothesis": "Reduce baseline score compression by centering PhaseWrap components in a balanced phase window before noisy readout.",
            "fixed_width_constraints": {
                "measured_qubits": 2,
                "active_qubits": 2,
                "templates_required": ["two_ry_product_state_z_readout_v1", "two_ry_cx_parity_z_readout_v1"],
            },
            "allowed_changes": [
                "source-row selection and normalization",
                "phase component scaling before RY preparation",
                "matched comparator packet regeneration with identical row/source surface",
            ],
            "disallowed_changes": [
                "increasing qubit count",
                "dropping matched RoPE-like, sinusoidal-like, ALIBI-like, or no-position controls",
                "using hardware results for model selection",
            ],
        },
        {
            "family_id": "pw_contrast_amplified_delta_v1",
            "hypothesis": "Increase observable separation between PhaseWrap and positional comparators while preserving fixed-width score semantics.",
            "fixed_width_constraints": {
                "measured_qubits": 2,
                "active_qubits": 2,
                "templates_required": ["two_ry_product_state_z_readout_v1", "two_ry_cx_parity_z_readout_v1"],
            },
            "allowed_changes": [
                "delta-pair sampling policy",
                "score contrast scaling bounded before count generation",
                "new frozen real-source seed pairs before any hardware run",
            ],
            "disallowed_changes": [
                "post-hoc comparator removal",
                "single-template promotion",
                "changing shot quantum thresholds after seeing results",
            ],
        },
        {
            "family_id": "pw_error_orthogonalized_components_v1",
            "hypothesis": "Choose component encodings whose PhaseWrap errors are less aligned with IBM readout and two-qubit stochastic shrinkage.",
            "fixed_width_constraints": {
                "measured_qubits": 2,
                "active_qubits": 2,
                "templates_required": ["two_ry_product_state_z_readout_v1", "two_ry_cx_parity_z_readout_v1"],
            },
            "allowed_changes": [
                "component-basis rotation in the classical packet freezer",
                "matched transformation applied to all encoding families",
                "IBM-informed simulated screening before packet lock",
            ],
            "disallowed_changes": [
                "using provider-specific live results to tune packets",
                "treating coherent-proxy-only wins as hardware-run approval",
                "relaxing the no-position control requirement",
            ],
        },
    ]


def _screening_sequence(primary_noise_model_ids: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "gate_id": "redesign_packet_freeze",
            "purpose": "Freeze redesigned fixed-width packet families before any provider action.",
            "pass_condition": "All candidate families produce product and CX packets with PhaseWrap, three positional comparators, and no-position control.",
        },
        {
            "gate_id": "ibm_informed_primary_screen",
            "purpose": "Reject candidates that only win under hand-built coherent offsets.",
            "pass_condition": (
                "PhaseWrap has stable strict wins on both templates under every primary IBM-informed model: "
                + ", ".join(primary_noise_model_ids)
            ),
        },
        {
            "gate_id": "seed_stability_screen",
            "purpose": "Avoid one-seed artifacts before reopening hardware.",
            "pass_condition": f"At least {MIN_INDEPENDENT_SEEDS} independent real-source seed pairs pass the primary screen.",
        },
        {
            "gate_id": "hardware_reopen_gate",
            "purpose": "Reopen hardware only after simulation evidence justifies spend.",
            "pass_condition": (
                f"Margins exceed {MIN_MARGIN_SHOT_QUANTA} shot quanta over both best positional comparator and no-position control "
                f"on at least {MIN_STABLE_TEMPLATES} templates and {MIN_PRIMARY_NOISE_MODELS} primary IBM-informed models."
            ),
        },
    ]


def run_stage181_fixed_width_target_redesign_plan(
    *,
    stage177_results_path: Path = DEFAULT_STAGE177_RESULTS,
    stage179_results_path: Path = DEFAULT_STAGE179_RESULTS,
    stage180_results_path: Path = DEFAULT_STAGE180_RESULTS,
) -> dict[str, Any]:
    stage177 = _load_json(stage177_results_path)
    stage179 = _load_json(stage179_results_path)
    stage180 = _load_json(stage180_results_path)
    sources = [
        (stage177_results_path, stage177),
        (stage179_results_path, stage179),
        (stage180_results_path, stage180),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage179, dict) and _decision(stage179) != STAGE179_ARCHIVE:
        blockers.append("stage179_current_ibm_path_not_archived")
    if isinstance(stage180, dict) and _decision(stage180) != STAGE180_NO_EXISTING_REOPEN:
        blockers.append("stage180_existing_surface_not_exhausted")
    primary_noise_model_ids = []
    if isinstance(stage177, dict):
        primary_noise_model_ids = [
            str(model.get("noise_model_id"))
            for model in stage177.get("noise_models", [])
            if isinstance(model, dict) and str(model.get("noise_model_id")) in {"ibm_backend_median_stochastic", "ibm_backend_p75_stochastic"}
        ]
    if not primary_noise_model_ids:
        blockers.append("stage177_primary_ibm_models_missing")

    design_families = _design_families()
    screening_sequence = _screening_sequence(primary_noise_model_ids)
    if blockers:
        decision = "FIXED_WIDTH_TARGET_REDESIGN_PLAN_INCOMPLETE"
    else:
        decision = "FIXED_WIDTH_TARGET_REDESIGN_PLAN_READY"
    return {
        "schema_version": STAGE181_SCHEMA_VERSION,
        "stage": "stage181_fixed_width_target_redesign_plan",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "primary_noise_model_ids": primary_noise_model_ids,
        "design_family_count": len(design_families),
        "design_families": design_families,
        "screening_sequence": screening_sequence,
        "hardware_reopen_thresholds": {
            "min_positional_margin_shot_quanta": MIN_MARGIN_SHOT_QUANTA,
            "min_control_margin_shot_quanta": MIN_MARGIN_SHOT_QUANTA,
            "min_stable_templates": MIN_STABLE_TEMPLATES,
            "min_independent_seed_pairs": MIN_INDEPENDENT_SEEDS,
            "min_primary_noise_models": MIN_PRIMARY_NOISE_MODELS,
        },
        "current_path_status": {
            "current_ibm_328_job_run_archived": _decision(stage179) == STAGE179_ARCHIVE,
            "existing_frozen_surface_exhausted": _decision(stage180) == STAGE180_NO_EXISTING_REOPEN,
        },
        "simulated_only": True,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "pre-registered redesign plan after archiving the current IBM run and exhausting existing frozen lanes",
                "fixed-width constraints and screening thresholds for future target/circuit redesign",
                "hardware reopen criteria tied to IBM-informed primary noise rather than hand-built coherent-only wins",
            ],
            "excluded": [
                "new packet generation",
                "hardware job submission",
                "a noisy-hardware robustness or auditability conclusion",
                "evidence that any redesign candidate has passed",
            ],
        },
        "next_gate": (
            "Implement the first redesigned packet family and screen it under the Stage177 IBM-informed primary noise models "
            "before considering any hardware reopen."
        ),
    }


def write_stage181_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
            "design_family_count",
            "hardware_reopen_thresholds",
            "current_path_status",
            "simulated_only",
            "no_hardware_submission",
            "provider_credentials_required",
            "secret_values_recorded",
            "runnable_commands_recorded",
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
        writer = csv.DictWriter(handle, fieldnames=("family_id", "hypothesis", "templates_required"))
        writer.writeheader()
        for family in result["design_families"]:
            writer.writerow(
                {
                    "family_id": family["family_id"],
                    "hypothesis": family["hypothesis"],
                    "templates_required": "; ".join(family["fixed_width_constraints"]["templates_required"]),
                }
            )
    return paths


def print_stage181_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"design_family_count: {result['design_family_count']}")
    print(f"next_gate: {result['next_gate']}")
