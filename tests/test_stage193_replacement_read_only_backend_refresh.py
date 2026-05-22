from __future__ import annotations

import json

from qrope.stage193_replacement_read_only_backend_refresh import run_stage193_replacement_read_only_backend_refresh, write_stage193_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path, *, credit_verified: bool = False):
    stage191 = tmp_path / "stage191.json"
    stage192 = tmp_path / "stage192.json"
    _write_json(
        stage191,
        {
            "decision": "REPLACEMENT_APPROVAL_DOSSIER_READY_FOR_HUMAN_REVIEW_NOT_LIVE",
            "estimated_total_job_count": 324,
            "estimated_total_shots": 1314720,
        },
    )
    _write_json(stage192, {"credit_balance_verified": credit_verified})
    return stage191, stage192


def _env() -> dict[str, str]:
    return {
        "IBM_QUANTUM_TOKEN": "secret-token",
        "IBM_QUANTUM_INSTANCE_CRN": "secret-crn",
        "QROPE_IBM_BACKEND": "ibm_fez",
    }


def test_stage193_does_not_attempt_refresh_without_explicit_allow(tmp_path) -> None:
    stage191, stage192 = _sources(tmp_path)

    result = run_stage193_replacement_read_only_backend_refresh(
        stage191_results_path=stage191,
        stage192_results_path=stage192,
        env=_env(),
        allow_read_only_refresh=False,
        backend_lookup=lambda env: {"backend": "ibm_fez"},
    )

    assert result["decision"] == "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_BLOCKED"
    assert result["backend_lookup_attempted"] is False
    assert "read_only_backend_refresh_not_requested" in result["blockers"]
    assert result["no_hardware_submission"] is True


def test_stage193_blocks_when_current_ibm_configuration_missing(tmp_path) -> None:
    stage191, stage192 = _sources(tmp_path)

    result = run_stage193_replacement_read_only_backend_refresh(
        stage191_results_path=stage191,
        stage192_results_path=stage192,
        env={},
        allow_read_only_refresh=True,
        backend_lookup=lambda env: {"backend": "ibm_fez"},
    )

    assert result["decision"] == "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_BLOCKED"
    assert result["backend_lookup_attempted"] is False
    assert "current_ibm_configuration_missing_or_incomplete" in result["blockers"]


def test_stage193_records_successful_read_only_refresh_without_credit_claim(tmp_path) -> None:
    stage191, stage192 = _sources(tmp_path, credit_verified=False)

    result = run_stage193_replacement_read_only_backend_refresh(
        stage191_results_path=stage191,
        stage192_results_path=stage192,
        env=_env(),
        allow_read_only_refresh=True,
        backend_lookup=lambda env: {"backend": "ibm_fez", "operational": True, "pending_jobs": 2},
    )

    assert result["decision"] == "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_READY_CREDIT_AND_APPROVAL_STILL_REQUIRED"
    assert result["backend_lookup_attempted"] is True
    assert result["backend_lookup_ready"] is True
    assert result["credit_balance_verified"] is False
    assert result["secret_values_recorded"] is False


def test_stage193_outputs_do_not_record_secret_values_or_live_submit(tmp_path) -> None:
    stage191, stage192 = _sources(tmp_path)
    result = run_stage193_replacement_read_only_backend_refresh(
        stage191_results_path=stage191,
        stage192_results_path=stage192,
        env={
            "IBM_QUANTUM_TOKEN": "do-not-write-this-token",
            "IBM_QUANTUM_INSTANCE_CRN": "crn:v1:do-not-write-this-crn",
            "QROPE_IBM_BACKEND": "ibm_fez",
        },
        allow_read_only_refresh=True,
        backend_lookup=lambda env: {"backend": "ibm_fez", "operational": True, "pending_jobs": 2},
    )

    paths = write_stage193_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "do-not-write-this-token" not in written
    assert "crn:v1:do-not-write-this-crn" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
