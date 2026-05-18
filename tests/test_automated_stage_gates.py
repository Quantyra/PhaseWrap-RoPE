from __future__ import annotations

import json

from qrope.automated_stage_gates import (
    ENTANGLING_CX_CIRCUIT_FAMILY,
    HardwareAdapter,
    all_stage1_diagnostics_pass,
    build_hardware_config,
    evaluate_circuit_parity,
    evaluate_noisy_simulator,
    evaluate_stage1_packet,
    freeze_hardware_packet,
    generate_transformer_phase_wrap_attention_bundle,
    hardware_preflight,
    ideal_counts_for_hardware_row,
    quandela_sample_count_to_hardware_counts,
    parse_attention_row_text,
    run_hardware_packet,
)
from scripts.verify_stage4_hardware_packet import verify_packet_files


HARDWARE_ENV = {
    "QROPE_REAL_HARDWARE_PROVIDER": "ibm_runtime",
    "QROPE_HARDWARE_BACKEND": "fake_backend",
    "QROPE_HARDWARE_BUDGET_USD_CAP": "10",
    "QROPE_HARDWARE_ROW_LIMIT": "8",
    "QROPE_HARDWARE_SHOT_COUNT": "4096",
    "IBM_QUANTUM_TOKEN": "fake-token",
}


class ReadyOnlyHardwareAdapter(HardwareAdapter):
    def preflight(self, packet: dict) -> dict:
        return {
            "status": "READY",
            "blockers": [],
            "provider": packet["provider"],
            "backend": packet["backend"],
            "budget_cap_usd": packet["config"]["budget_cap_usd"],
            "estimated_packet_cost_usd": packet["config"]["estimated_packet_cost_usd"],
            "note": "READY is not PASS",
        }

    def run_packet(self, packet: dict) -> dict:
        return {"status": "NOT_RUN", "error": "ready-only adapter did not submit jobs"}


class IdealHardwareAdapter(ReadyOnlyHardwareAdapter):
    def run_packet(self, packet: dict) -> dict:
        return {
            "status": "COMPLETED",
            "jobs": [
                {
                    "job_id": "ideal-job-1",
                    "provider": packet["provider"],
                    "backend": packet["backend"],
                    "shot_count": packet["shot_count"],
                    "raw_counts_by_row": [
                        {
                            "row_id": row["row_id"],
                            "counts": ideal_counts_for_hardware_row(row, packet["shot_count"]),
                        }
                        for row in packet["rows"]
                    ],
                }
            ],
            "backend_metadata": {"provider": packet["provider"], "backend": packet["backend"]},
            "calibration_metadata": {"captured_at_utc": "2026-05-16T00:00:00Z"},
        }


class MissingMetadataHardwareAdapter(IdealHardwareAdapter):
    def run_packet(self, packet: dict) -> dict:
        execution = super().run_packet(packet)
        execution.pop("calibration_metadata")
        return execution


class NegativeHardwareAdapter(IdealHardwareAdapter):
    def run_packet(self, packet: dict) -> dict:
        execution = super().run_packet(packet)
        for item in execution["jobs"][0]["raw_counts_by_row"]:
            item["counts"] = {"00": packet["shot_count"]}
        return execution


def test_transformer_phase_wrap_attention_bundle_passes_diagnostics() -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    assert bundle.diagnostics["dataset"] == "synthetic_transformer_phase_wrap_attention_selection"
    assert all_stage1_diagnostics_pass(bundle.diagnostics)
    parsed = parse_attention_row_text(bundle.train[0].text)
    assert parsed["candidate_delta"] == bundle.train[0].candidate_delta
    assert parsed["reference_delta"] == bundle.train[0].reference_delta


def test_stage1_witness_beats_symbolic_control() -> None:
    result = evaluate_stage1_packet(42)
    assert result["gate_pass"] is True
    assert result["witness"]["mae"] < result["control"]["mae"]
    assert result["witness"]["rank_correlation"] > result["control"]["rank_correlation"]


def test_circuit_parity_gate_passes() -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(314)
    result = evaluate_circuit_parity((bundle.train + bundle.validation + bundle.test)[:512])
    assert result["gate_pass"] is True
    assert result["sign_parity_pass"] is True
    assert result["rank_correlation"] >= 0.999
    assert result["mean_abs_normalized_score_error"] <= 1e-6


def test_noisy_simulator_gate_passes() -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    result = evaluate_noisy_simulator(bundle.test)
    assert result["gate_pass"] is True
    assert result["exact_witness"]["mae"] == 0.0
    assert result["exact_witness"]["rank_correlation"] == 1.0
    assert result["exact_to_noisy_mae_degradation"] <= result["degradation_tolerance"]
    assert result["witness"]["mae"] < result["control"]["mae"]
    assert result["witness"]["rank_correlation"] > result["control"]["rank_correlation"]


def test_hardware_preflight_blocks_without_configuration(monkeypatch) -> None:
    for name in (
        "QISKIT_IBM_TOKEN",
        "IBM_QUANTUM_TOKEN",
        "QUANDELA_TOKEN",
        "XANADU_CLOUD_KEY",
        "QROPE_REAL_HARDWARE_PROVIDER",
        "QROPE_HARDWARE_BACKEND",
        "QROPE_HARDWARE_BUDGET_USD_CAP",
    ):
        monkeypatch.delenv(name, raising=False)
    result = hardware_preflight(env={})
    assert result["status"] == "BLOCKED"
    assert result["blockers"]


def test_quandela_stage4_profile_uses_provider_specific_controls() -> None:
    env = {
        "QROPE_REAL_HARDWARE_PROVIDER": "quandela",
        "QROPE_HARDWARE_BACKEND": "ibm_fez",
        "QROPE_QUANDELA_BACKEND": "sim:slos",
        "QROPE_HARDWARE_BUDGET_USD_CAP": "25",
        "QROPE_QUANDELA_BUDGET_USD_CAP": "10",
        "QROPE_HARDWARE_ESTIMATED_COST_USD": "5",
        "QROPE_QUANDELA_ESTIMATED_COST_USD": "0",
        "QROPE_QUANDELA_QUEUE_DEPTH_CAP": "7",
        "QROPE_HARDWARE_ROW_LIMIT": "8",
        "QROPE_HARDWARE_SHOT_COUNT": "4096",
        "QUANDELA_CLOUD_TOKEN": "fake-token",
    }
    config = build_hardware_config(env)
    assert config["provider"] == "quandela"
    assert config["backend"] == "sim:slos"
    assert config["budget_cap_usd"] == 10.0
    assert config["estimated_packet_cost_usd"] == 0.0
    assert config["queue_depth_cap"] == 7
    assert config["row_limit"] == 8
    assert config["shot_count"] == 4096


def test_quandela_sample_count_converts_to_stage4_two_bit_counts() -> None:
    converted = quandela_sample_count_to_hardware_counts(
        {
            "|1,0,1,0>": 3,
            "|0,1,1,0>": 2,
            "|1,0,0,1>": 5,
            "|0,1,0,1>": 7,
            "|2,0,0,0>": 11,
        }
    )
    assert converted["counts"] == {"00": 3, "01": 2, "10": 5, "11": 7}
    assert converted["accepted_shots"] == 17
    assert converted["rejected_shots"] == 11
    assert converted["rejected_states"] == {"|2,0,0,0>": 11}


def test_quandela_stage4_preflight_ready_for_physical_platform(monkeypatch) -> None:
    import perceval.providers

    class FakeProcessor:
        name = "qpu:fake"
        type = "ProcessorType.PHYSICAL"
        status = "available"
        specs = {"available_commands": ["sample_count"], "constraints": {"max_photon_count": 4}}
        constraints = {"max_photon_count": 4}
        performance = {"source": "fake"}
        available_commands = ["sample_count"]

    class FakeSession:
        def __init__(self, platform_name: str, token: str, url: str | None = None) -> None:
            self.platform_name = platform_name
            self.token = token
            self.url = url

        def build_remote_processor(self) -> FakeProcessor:
            return FakeProcessor()

    monkeypatch.setattr(perceval.providers, "QuandelaSession", FakeSession)
    result = hardware_preflight(
        env={
            "QROPE_REAL_HARDWARE_PROVIDER": "quandela",
            "QROPE_QUANDELA_BACKEND": "qpu:fake",
            "QROPE_QUANDELA_BUDGET_USD_CAP": "10",
            "QROPE_QUANDELA_ESTIMATED_COST_USD": "1",
            "QROPE_HARDWARE_ROW_LIMIT": "2",
            "QROPE_HARDWARE_SHOT_COUNT": "16",
            "QUANDELA_CLOUD_TOKEN": "fake-token",
        }
    )
    assert result["status"] == "READY"
    assert result["blockers"] == []
    assert result["metadata_capture_available"] is True
    assert result["backend_metadata"]["processor_type"] == "ProcessorType.PHYSICAL"


def test_quandela_stage4_preflight_blocks_simulator_by_default(monkeypatch) -> None:
    import perceval.providers

    class FakeProcessor:
        name = "sim:fake"
        type = "ProcessorType.SIMULATOR"
        status = "available"
        specs = {"available_commands": ["sample_count"], "constraints": {"max_photon_count": 4}}
        constraints = {"max_photon_count": 4}
        performance = {}
        available_commands = ["sample_count"]

    class FakeSession:
        def __init__(self, platform_name: str, token: str, url: str | None = None) -> None:
            self.platform_name = platform_name
            self.token = token
            self.url = url

        def build_remote_processor(self) -> FakeProcessor:
            return FakeProcessor()

    monkeypatch.setattr(perceval.providers, "QuandelaSession", FakeSession)
    result = hardware_preflight(
        env={
            "QROPE_REAL_HARDWARE_PROVIDER": "quandela",
            "QROPE_QUANDELA_BACKEND": "sim:fake",
            "QROPE_QUANDELA_BUDGET_USD_CAP": "10",
            "QROPE_QUANDELA_ESTIMATED_COST_USD": "0",
            "QROPE_HARDWARE_ROW_LIMIT": "2",
            "QROPE_HARDWARE_SHOT_COUNT": "16",
            "QUANDELA_CLOUD_TOKEN": "fake-token",
        }
    )
    assert result["status"] == "BLOCKED"
    assert any("requires a physical platform" in blocker for blocker in result["blockers"])


def test_quandela_stage4_preflight_blocks_unavailable_physical_platform(monkeypatch) -> None:
    import perceval.providers

    class FakeProcessor:
        name = "qpu:fake"
        type = "ProcessorType.PHYSICAL"
        status = "maintenance"
        specs = {"available_commands": ["sample_count"], "constraints": {"max_photon_count": 4}}
        constraints = {"max_photon_count": 4}
        performance = {}
        available_commands = ["sample_count"]

    class FakeSession:
        def __init__(self, platform_name: str, token: str, url: str | None = None) -> None:
            self.platform_name = platform_name
            self.token = token
            self.url = url

        def build_remote_processor(self) -> FakeProcessor:
            return FakeProcessor()

    monkeypatch.setattr(perceval.providers, "QuandelaSession", FakeSession)
    result = hardware_preflight(
        env={
            "QROPE_REAL_HARDWARE_PROVIDER": "quandela",
            "QROPE_QUANDELA_BACKEND": "qpu:fake",
            "QROPE_QUANDELA_BUDGET_USD_CAP": "10",
            "QROPE_QUANDELA_ESTIMATED_COST_USD": "1",
            "QROPE_HARDWARE_ROW_LIMIT": "2",
            "QROPE_HARDWARE_SHOT_COUNT": "16",
            "QUANDELA_CLOUD_TOKEN": "fake-token",
        }
    )
    assert result["status"] == "BLOCKED"
    assert any("not currently available" in blocker for blocker in result["blockers"])


def test_hardware_preflight_ready_is_not_pass() -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    packet = freeze_hardware_packet(bundle.test, HARDWARE_ENV)
    result = ReadyOnlyHardwareAdapter().preflight(packet)
    assert result["status"] == "READY"
    assert result["status"] != "PASS"


def test_hardware_packet_does_not_pass_without_completed_jobs() -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    result = run_hardware_packet(bundle.test, adapter=ReadyOnlyHardwareAdapter(), env=HARDWARE_ENV)
    assert result["status"] == "FAIL_STOP"
    assert result["outcome"] == "hardware-inconclusive"
    assert result["gate_pass"] is False


def test_hardware_packet_pass_requires_counts_metadata_and_metrics() -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    result = run_hardware_packet(bundle.test, adapter=IdealHardwareAdapter(), env=HARDWARE_ENV)
    assert result["status"] == "PASS"
    assert result["outcome"] == "hardware-positive"
    assert result["execution"]["jobs"][0]["job_id"] == "ideal-job-1"
    assert result["evaluation"]["metadata_complete"] is True
    assert result["evaluation"]["witness"]["mae"] < result["evaluation"]["control"]["mae"]
    assert result["evaluation"]["witness"]["rank_correlation"] > result["evaluation"]["control"]["rank_correlation"]
    assert result["evaluation"]["direction_agreement"] is True


def test_entangling_cx_hardware_family_uses_entangling_measurement_policy() -> None:
    env = dict(HARDWARE_ENV)
    env["QROPE_HARDWARE_CIRCUIT_FAMILY"] = ENTANGLING_CX_CIRCUIT_FAMILY
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    result = run_hardware_packet(bundle.test, adapter=IdealHardwareAdapter(), env=env)

    assert result["packet"]["circuit_family"] == ENTANGLING_CX_CIRCUIT_FAMILY
    assert result["packet"]["measurement_policy"]["entangling_gate"] == "cx q0->q1"
    assert result["status"] == "PASS"
    assert result["outcome"] == "hardware-positive"
    assert result["evaluation"]["witness"]["mae"] < result["evaluation"]["control"]["mae"]
    assert result["evaluation"]["witness"]["rank_correlation"] > result["evaluation"]["control"]["rank_correlation"]


def test_offline_stage4_verifier_recomputes_recorded_metrics(tmp_path) -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    result = run_hardware_packet(bundle.test[:4], adapter=IdealHardwareAdapter(), env=HARDWARE_ENV)
    packet_path = tmp_path / "frozen_packet.json"
    execution_path = tmp_path / "execution.json"
    evaluation_path = tmp_path / "evaluation.json"
    summary_path = tmp_path / "summary.json"
    packet_path.write_text(json.dumps(result["packet"], indent=2), encoding="utf-8")
    execution_path.write_text(json.dumps(result["execution"], indent=2), encoding="utf-8")
    evaluation_path.write_text(json.dumps(result["evaluation"], indent=2), encoding="utf-8")
    summary_path.write_text(json.dumps({"result": {"status": result["status"], "outcome": result["outcome"]}}, indent=2), encoding="utf-8")

    verification = verify_packet_files(
        packet_path=packet_path,
        execution_path=execution_path,
        evaluation_path=evaluation_path,
        summary_path=summary_path,
        expected_provider="ibm_runtime",
        expected_backend="fake_backend",
        expected_job_id="ideal-job-1",
    )

    assert verification["pass"] is True
    assert verification["no_hardware_submission"] is True
    assert verification["recomputed_evaluation"]["outcome"] == "hardware-positive"


def test_hardware_packet_fails_when_metadata_is_missing() -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    result = run_hardware_packet(bundle.test, adapter=MissingMetadataHardwareAdapter(), env=HARDWARE_ENV)
    assert result["status"] == "FAIL_STOP"
    assert result["outcome"] == "hardware-inconclusive"
    assert result["gate_pass"] is False
    assert result["evaluation"]["metadata_complete"] is False
    assert "required hardware metadata is incomplete" in result["evaluation"]["fail_reasons"]


def test_hardware_packet_can_return_hardware_negative() -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    result = run_hardware_packet(bundle.test, adapter=NegativeHardwareAdapter(), env=HARDWARE_ENV)
    assert result["status"] == "FAIL_STOP"
    assert result["outcome"] == "hardware-negative"
    assert result["gate_pass"] is False
    assert result["evaluation"]["metadata_complete"] is True
    assert "hardware witness did not beat hardware control on both metrics" in result["evaluation"]["fail_reasons"]
