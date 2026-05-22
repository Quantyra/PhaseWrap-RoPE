from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE107_SCHEMA_VERSION = "qrope_stage107_window_execution_orchestrator_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE102_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage102_calibration_execution_package" / "manifest.json"
DEFAULT_STAGE105_WINDOWS = DEFAULT_ARTIFACT_ROOT / "stage105_independent_rerun_protocol" / "rerun_windows.json"
DEFAULT_STAGE106_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage106_hardware_execution_preflight" / "manifest.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage107_window_execution_orchestrator"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _calibration_template_for_provider(stage102: dict[str, Any] | None, provider: str) -> str | None:
    if not stage102:
        return None
    for path in stage102.get("template_paths", []):
        if Path(str(path)).name == f"{provider}_known_state_execution.json":
            return str(path)
    return None


def _window_steps(window: dict[str, Any], calibration_template_path: str | None, stage106_ready: bool) -> list[dict[str, Any]]:
    window_dir = f"logs/automated_stage_gates/stage107_window_execution_orchestrator/windows/{window['window_id']}"
    packet_execution_dir = f"{window_dir}/packet_executions"
    calibration_dir = f"{window_dir}/calibration"
    return [
        {
            "step_id": "preflight",
            "status": "ready" if stage106_ready else "blocked",
            "command": "python scripts/run_stage106_hardware_execution_preflight.py --load-dotenv",
            "required_before_hardware_submission": True,
            "output_expectation": "Stage 106 decision must be HARDWARE_EXECUTION_PREFLIGHT_READY_NO_SUBMISSION.",
        },
        {
            "step_id": "known_state_calibration_execution",
            "status": "blocked_until_stage106_ready",
            "template_path": calibration_template_path,
            "output_path": f"{calibration_dir}/{window['provider']}_known_state_execution.json",
            "required_before_hardware_submission": True,
            "output_expectation": "Fill Stage 102 known-state execution template with real provider/backend/date counts and metadata.",
        },
        {
            "step_id": "known_state_calibration_verification",
            "status": "blocked_until_calibration_counts_present",
            "command": (
                "python scripts/run_stage101_known_state_calibration_gate.py "
                f"--execution-dir {calibration_dir} --output-dir {calibration_dir}/stage101"
            ),
            "required_before_matched_packet_interpretation": True,
            "output_expectation": "Stage 101 must pass for this provider/backend/date window.",
        },
        {
            "step_id": "matched_packet_execution",
            "status": "blocked_until_stage101_passes",
            "packet_template_count": window["packet_template_count"],
            "packet_templates": window["packet_templates"],
            "output_dir": packet_execution_dir,
            "output_expectation": "Fill every Stage 104 packet execution template for this provider window with canonical q0q1 row counts.",
        },
        {
            "step_id": "window_metric_recompute",
            "status": "blocked_until_all_packet_counts_present",
            "command": (
                "python scripts/run_stage103_robustness_metric_preregistration.py "
                f"--execution-dir {packet_execution_dir} --stage101-results {calibration_dir}/stage101/results.json "
                f"--output-dir {window_dir}/stage103"
            ),
            "required_before_claim": True,
            "output_expectation": "Compute Stage 103 metrics for this independent window only.",
        },
    ]


def run_stage107_orchestrator(
    *,
    stage102_manifest_path: Path = DEFAULT_STAGE102_MANIFEST,
    stage105_windows_path: Path = DEFAULT_STAGE105_WINDOWS,
    stage106_manifest_path: Path = DEFAULT_STAGE106_MANIFEST,
) -> dict[str, Any]:
    stage102 = _load_json(stage102_manifest_path)
    windows = _load_json(stage105_windows_path)
    stage106 = _load_json(stage106_manifest_path)
    sources = [
        (stage102_manifest_path, stage102),
        (stage105_windows_path, windows),
        (stage106_manifest_path, stage106),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    windows_list = windows if isinstance(windows, list) else []
    stage106_ready = bool(stage106 and stage106.get("ready_for_hardware_submission") is True)
    plans = []
    for window in windows_list:
        calibration_template = _calibration_template_for_provider(stage102, str(window["provider"]))
        plans.append(
            {
                "window_id": window["window_id"],
                "provider": window["provider"],
                "window_index": window["window_index"],
                "minimum_separation_from_previous_window_hours": window["minimum_separation_from_previous_window_hours"],
                "packet_template_count": window["packet_template_count"],
                "stage106_ready": stage106_ready,
                "calibration_template_path": calibration_template,
                "steps": _window_steps(window, calibration_template, stage106_ready),
            }
        )
    decision = (
        "WINDOW_EXECUTION_PLAN_READY_FOR_MANUAL_HARDWARE_RUN"
        if plans and stage106_ready and not missing_sources
        else "WINDOW_EXECUTION_PLAN_PREPARED_PREFLIGHT_BLOCKED"
    )
    return {
        "schema_version": STAGE107_SCHEMA_VERSION,
        "stage": "stage107_window_execution_orchestrator",
        "status": "completed" if plans and not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage106_ready_for_hardware_submission": stage106_ready,
        "window_count": len(plans),
        "provider_count": len({plan["provider"] for plan in plans}),
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "window_execution_plans": plans,
        "claim_boundary": {
            "supported": [
                "a dry-run orchestration plan for Stage 105 independent provider windows",
                "an ordered handoff from Stage 106 preflight to Stage 101 calibration, Stage 104 packet execution, and Stage 103 metric recomputation",
                "a no-submission artifact that keeps hardware execution blocked until preflight is ready",
            ],
            "excluded": [
                "real hardware submission",
                "completed calibration counts",
                "completed matched packet counts",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Clear Stage 106, then use the Stage 107 window execution plans to run calibration, matched packet execution, "
            "and metric recomputation for each Stage 105 independent window."
        ),
    }


def write_stage107_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage106_ready_for_hardware_submission": result["stage106_ready_for_hardware_submission"],
        "window_count": result["window_count"],
        "provider_count": result["provider_count"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "window_plan_path": str((output_dir / "window_execution_plans.json").as_posix()),
        "claim_boundary": result["claim_boundary"],
        "next_gate": result["next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "window_plans": str(output_dir / "window_execution_plans.json"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "window_execution_plans.json").write_text(
        json.dumps(result["window_execution_plans"], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "window_id",
                "provider",
                "window_index",
                "stage106_ready",
                "packet_template_count",
                "blocked_step_count",
            ),
        )
        writer.writeheader()
        for plan in result["window_execution_plans"]:
            writer.writerow(
                {
                    "window_id": plan["window_id"],
                    "provider": plan["provider"],
                    "window_index": plan["window_index"],
                    "stage106_ready": plan["stage106_ready"],
                    "packet_template_count": plan["packet_template_count"],
                    "blocked_step_count": sum(1 for step in plan["steps"] if str(step["status"]).startswith("blocked")),
                }
            )
    return paths


def print_stage107_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"stage106_ready_for_hardware_submission: {result['stage106_ready_for_hardware_submission']}")
    print(f"window_count: {result['window_count']}")
    print(f"next_gate: {result['next_gate']}")
