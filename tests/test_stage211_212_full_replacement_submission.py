from __future__ import annotations

import json

from qrope.stage211_full_replacement_guarded_runner_readiness import run_stage211_full_replacement_guarded_runner_readiness, write_stage211_outputs
from qrope.stage212_full_replacement_hardware_submission import run_stage212_full_replacement_hardware_submission, write_stage212_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _template(index: int) -> dict:
    return {
        "template_type": "replacement_packet_execution_counts",
        "packet_id": f"packet-{index}",
        "source_lane_id": "lane",
        "encoding_family": "phasewrap",
        "circuit_template": "two_ry_product_state_z_readout_v1",
        "shot_count": 4096,
        "raw_counts_by_row": [
            {
                "row_id": "r0",
                "openqasm3": "OPENQASM 3.0;\nqubit[2] q;\nbit[2] c;\nc[0] = measure q[0];\nc[1] = measure q[1];\n",
            }
        ],
    }


def _sources(tmp_path):
    stage190 = tmp_path / "stage190.json"
    stage193 = tmp_path / "stage193.json"
    stage194 = tmp_path / "stage194.json"
    stage195 = tmp_path / "stage195.json"
    templates = [_template(index) for index in range(20)]
    calibration = {
        "template_type": "replacement_known_state_calibration_counts",
        "shots_per_state": 1000,
        "raw_counts_by_state": [
            {
                "state": state,
                "openqasm3": "OPENQASM 3.0;\nqubit[2] q;\nbit[2] c;\nc[0] = measure q[0];\nc[1] = measure q[1];\n",
            }
            for state in ("00", "01", "10", "11")
        ],
    }
    _write_json(
        stage190,
        {
            "decision": "REPLACEMENT_EXECUTION_PACKAGE_PREPARED_COUNTS_AND_CALIBRATION_REQUIRED",
            "packet_template_count": 20,
            "calibration_template_count": 1,
            "estimated_packet_row_job_count": 320,
            "estimated_calibration_job_count": 4,
            "estimated_total_job_count": 324,
            "estimated_total_shots": 1314720,
            "no_hardware_submission": True,
            "execution_templates": templates,
            "calibration_template": calibration,
        },
    )
    _write_json(
        stage193,
        {
            "decision": "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_READY_CREDIT_AND_APPROVAL_STILL_REQUIRED",
            "backend_lookup_ready": True,
            "backend_metadata": {"backend": "ibm_fez", "operational": True, "pending_jobs": 1},
        },
    )
    _write_json(
        stage194,
        {
            "decision": "REPLACEMENT_CREDIT_ALLOWANCE_VERIFIED_READY_FOR_EXACT_APPROVAL_REVIEW",
            "human_credit_allowance_verified": True,
            "budget_cap_usd": 250.0,
        },
    )
    _write_json(
        stage195,
        {
            "decision": "REPLACEMENT_EXACT_APPROVAL_ACCEPTED_READY_FOR_LIVE_RUNNER_PREPARATION_REVIEW",
            "approval_phrase_matches": True,
            "stage194_decision": "REPLACEMENT_CREDIT_ALLOWANCE_VERIFIED_READY_FOR_EXACT_APPROVAL_REVIEW",
        },
    )
    return stage190, stage193, stage194, stage195


def test_stage211_ready_after_full_package_credit_and_approval(tmp_path) -> None:
    stage190, stage193, stage194, stage195 = _sources(tmp_path)

    result = run_stage211_full_replacement_guarded_runner_readiness(
        stage190_results_path=stage190,
        stage193_results_path=stage193,
        stage194_results_path=stage194,
        stage195_results_path=stage195,
    )

    assert result["decision"] == "FULL_REPLACEMENT_GUARDED_RUNNER_READY_FOR_FINAL_EXECUTION_STEP_NOT_LIVE"
    assert result["backend"] == "ibm_fez"
    assert result["explicit_user_approval_recorded"] is True
    assert result["no_hardware_submission"] is True


def test_stage211_blocks_without_exact_approval(tmp_path) -> None:
    stage190, stage193, stage194, stage195 = _sources(tmp_path)
    payload = json.loads(stage195.read_text(encoding="utf-8"))
    payload["approval_phrase_matches"] = False
    _write_json(stage195, payload)

    result = run_stage211_full_replacement_guarded_runner_readiness(
        stage190_results_path=stage190,
        stage193_results_path=stage193,
        stage194_results_path=stage194,
        stage195_results_path=stage195,
    )

    assert result["decision"] == "FULL_REPLACEMENT_GUARDED_RUNNER_READINESS_BLOCKED"
    assert "stage195_exact_approval_not_ready" in result["blockers"]


def test_stage212_blocks_without_allow_live_submit(tmp_path) -> None:
    stage190, stage193, stage194, stage195 = _sources(tmp_path)
    stage211_payload = run_stage211_full_replacement_guarded_runner_readiness(
        stage190_results_path=stage190,
        stage193_results_path=stage193,
        stage194_results_path=stage194,
        stage195_results_path=stage195,
    )
    stage211 = tmp_path / "stage211.json"
    _write_json(stage211, stage211_payload)

    result = run_stage212_full_replacement_hardware_submission(stage211_results_path=stage211, stage190_results_path=stage190)

    assert result["decision"] == "FULL_REPLACEMENT_HARDWARE_SUBMISSION_BLOCKED_OR_PARTIAL"
    assert "allow_live_submit_flag_required" in result["blockers"]
    assert result["submission_attempted"] is False


def test_stage212_records_fake_async_submission_ids(tmp_path) -> None:
    stage190, stage193, stage194, stage195 = _sources(tmp_path)
    stage211_payload = run_stage211_full_replacement_guarded_runner_readiness(
        stage190_results_path=stage190,
        stage193_results_path=stage193,
        stage194_results_path=stage194,
        stage195_results_path=stage195,
    )
    stage211 = tmp_path / "stage211.json"
    _write_json(stage211, stage211_payload)

    def fake_submit(*, template, backend_name):
        return {
            "runtime_job_id": f"job-{template.get('packet_id', 'calibration') or 'calibration'}",
            "submitted_at_utc": "2026-05-22T00:00:00+00:00",
            "backend_metadata": {"backend": backend_name, "provider": "ibm_runtime"},
        }

    result = run_stage212_full_replacement_hardware_submission(
        stage211_results_path=stage211,
        stage190_results_path=stage190,
        allow_live_submit=True,
        submit_template=fake_submit,
    )

    assert result["decision"] == "FULL_REPLACEMENT_HARDWARE_SUBMITTED_AWAITING_RESULTS"
    assert result["submitted_runtime_job_count"] == 21
    assert result["hardware_submission_performed"] is True
    assert result["secret_values_recorded"] is False


def test_stage211_and_212_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage190, stage193, stage194, stage195 = _sources(tmp_path)
    stage211_result = run_stage211_full_replacement_guarded_runner_readiness(
        stage190_results_path=stage190,
        stage193_results_path=stage193,
        stage194_results_path=stage194,
        stage195_results_path=stage195,
    )
    stage211_paths = write_stage211_outputs(stage211_result, tmp_path / "out211")
    stage211 = tmp_path / "out211" / "results.json"
    stage212_result = run_stage212_full_replacement_hardware_submission(stage211_results_path=stage211, stage190_results_path=stage190)
    stage212_paths = write_stage212_outputs(stage212_result, tmp_path / "out212")

    written = "\n".join(
        [
            (tmp_path / "out211" / "results.json").read_text(encoding="utf-8"),
            (tmp_path / "out211" / "summary.csv").read_text(encoding="utf-8"),
            (tmp_path / "out212" / "results.json").read_text(encoding="utf-8"),
            (tmp_path / "out212" / "summary.csv").read_text(encoding="utf-8"),
        ]
    )

    assert set(stage211_paths) == {"manifest", "result", "summary_csv"}
    assert set(stage212_paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "QISKIT_IBM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
