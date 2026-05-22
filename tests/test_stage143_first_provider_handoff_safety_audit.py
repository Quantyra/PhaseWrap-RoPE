from __future__ import annotations

import json

from qrope.stage143_first_provider_handoff_safety_audit import run_stage143_audit, write_stage143_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage142(path, *, unsafe_template: bool = False, unsafe_command: bool = False) -> None:
    _write_json(
        path,
        {
            "decision": "FIRST_PROVIDER_UNLOCK_HANDOFF_READY_ENV_OR_SDK_REQUIRED",
            "first_unlock_provider": "ibm_runtime",
            "env_template": "IBM_QUANTUM_TOKEN=secret\nIBM_QUANTUM_INSTANCE_CRN=\n"
            if unsafe_template
            else "IBM_QUANTUM_TOKEN=\nIBM_QUANTUM_INSTANCE_CRN=\n",
            "rerun_commands": [
                "python scripts/run_stage140_local_provider_configuration_readiness.py --load-dotenv",
                "python scripts/provider_runners/run_ibm_runtime_stage112_jobs.py --allow-live-submit"
                if unsafe_command
                else "python scripts/run_stage106_hardware_execution_preflight.py --load-dotenv",
            ],
            "no_hardware_submission": True,
            "secret_values_recorded": False,
        },
    )


def test_stage143_verifies_placeholder_and_non_live_handoff(tmp_path) -> None:
    stage142 = tmp_path / "stage142.json"
    _stage142(stage142)

    result = run_stage143_audit(stage142_results_path=stage142)

    assert result["decision"] == "FIRST_PROVIDER_HANDOFF_SAFETY_VERIFIED_NO_SUBMISSION"
    assert result["nonempty_template_assignment_count"] == 0
    assert result["forbidden_command_count"] == 0
    assert result["secret_values_recorded"] is False


def test_stage143_blocks_nonempty_template_assignment(tmp_path) -> None:
    stage142 = tmp_path / "stage142.json"
    _stage142(stage142, unsafe_template=True)

    result = run_stage143_audit(stage142_results_path=stage142)

    assert result["decision"] == "FIRST_PROVIDER_HANDOFF_SAFETY_BLOCKED"
    assert result["nonempty_template_assignment_count"] == 1
    assert result["template_placeholders_only"] is False


def test_stage143_blocks_live_submit_command_fragment(tmp_path) -> None:
    stage142 = tmp_path / "stage142.json"
    _stage142(stage142, unsafe_command=True)

    result = run_stage143_audit(stage142_results_path=stage142)

    assert result["decision"] == "FIRST_PROVIDER_HANDOFF_SAFETY_BLOCKED"
    assert result["forbidden_command_count"] == 1
    assert result["rerun_commands_non_live"] is False


def test_stage143_outputs_are_written(tmp_path) -> None:
    stage142 = tmp_path / "stage142.json"
    _stage142(stage142)
    result = run_stage143_audit(stage142_results_path=stage142)

    paths = write_stage143_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["decision"] == "FIRST_PROVIDER_HANDOFF_SAFETY_VERIFIED_NO_SUBMISSION"
    assert "IBM_QUANTUM_TOKEN" in summary
