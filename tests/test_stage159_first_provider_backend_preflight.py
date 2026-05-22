from __future__ import annotations

import json

from qrope.stage159_first_provider_backend_preflight import (
    run_stage159_backend_preflight,
    write_stage159_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage158(tmp_path):
    path = tmp_path / "stage158.json"
    _write_json(
        path,
        {
            "decision": "FIRST_PROVIDER_PRE_EXECUTION_SANITY_READY_AWAITING_APPROVAL",
            "first_unlock_provider": "ibm_runtime",
            "approval_phrase_required": "APPROVE IBM RUNTIME STAGE133 LIVE RUN",
        },
    )
    return path


def _env() -> dict[str, str]:
    return {
        "IBM_QUANTUM_TOKEN": "token",
        "IBM_QUANTUM_INSTANCE_CRN": "crn:v1:secret",
        "QROPE_IBM_BACKEND": "ibm_brisbane",
    }


def test_stage159_ready_with_injected_backend_lookup_without_secret_values(tmp_path) -> None:
    stage158 = _stage158(tmp_path)

    result = run_stage159_backend_preflight(
        stage158_results_path=stage158,
        env=_env(),
        allow_backend_lookup=True,
        backend_lookup=lambda env: {
            "backend": "ibm_brisbane",
            "version": "2.0",
            "num_qubits": 127,
            "simulator": False,
            "operational": True,
            "pending_jobs": 4,
            "basis_gate_count": 8,
            "coupling_edge_count": 144,
        },
    )

    assert result["decision"] == "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL"
    assert result["backend_lookup_attempted"] is True
    assert result["backend_lookup_ready"] is True
    assert result["secret_values_recorded"] is False
    assert result["runnable_commands_recorded"] is False
    assert result["backend_metadata"]["backend"] == "ibm_brisbane"


def test_stage159_does_not_lookup_without_explicit_flag(tmp_path) -> None:
    stage158 = _stage158(tmp_path)

    result = run_stage159_backend_preflight(
        stage158_results_path=stage158,
        env=_env(),
        allow_backend_lookup=False,
        backend_lookup=lambda env: {"backend": "ibm_brisbane"},
    )

    assert result["decision"] == "FIRST_PROVIDER_BACKEND_PREFLIGHT_BLOCKED"
    assert result["backend_lookup_attempted"] is False
    assert "backend_lookup_not_requested" in result["blockers"]


def test_stage159_blocks_without_backend_env(tmp_path) -> None:
    stage158 = _stage158(tmp_path)
    env = _env()
    env.pop("QROPE_IBM_BACKEND")

    result = run_stage159_backend_preflight(stage158_results_path=stage158, env=env, allow_backend_lookup=True)

    assert result["decision"] == "FIRST_PROVIDER_BACKEND_PREFLIGHT_BLOCKED"
    assert "ibm_backend_env_missing" in result["blockers"]
    assert result["backend_lookup_attempted"] is False


def test_stage159_outputs_omit_crn_token_and_live_submit_commands(tmp_path) -> None:
    stage158 = _stage158(tmp_path)
    result = run_stage159_backend_preflight(
        stage158_results_path=stage158,
        env=_env(),
        allow_backend_lookup=True,
        backend_lookup=lambda env: {"backend": "ibm_brisbane", "num_qubits": 127},
    )

    paths = write_stage159_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "crn:v1" not in written
    assert '"token"' not in written
    assert "--allow-live-submit" not in written
    assert "crn:v1" not in summary
