from __future__ import annotations

import json

from scripts.run_braket_hardware_smoke import _artifact_summary as _braket_artifact_summary
import scripts.run_stage4_hardware_sweep as hardware_sweep
from qrope.automated_stage_gates import (
    ENTANGLING_CX_CIRCUIT_FAMILY,
    EnvironmentHardwareAdapter,
    HardwareAdapter,
    all_stage1_diagnostics_pass,
    braket_openqasm_for_hardware_row,
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
from scripts.run_stage4_hardware_sweep import _artifact_summary, _split_env_list
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


class BraketAgreementBlockedAdapter(ReadyOnlyHardwareAdapter):
    def run_packet(self, packet: dict) -> dict:
        raise RuntimeError(
            "AWS CLI command failed (254): An error occurred (AccessDeniedException) "
            "when calling the CreateQuantumTask operation: User agreement has not been accepted for 485386182336."
        )


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


def test_braket_stage4_profile_uses_aws_specific_controls() -> None:
    env = {
        "QROPE_REAL_HARDWARE_PROVIDER": "braket",
        "QROPE_BRAKET_DEVICE_ARN": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
        "QROPE_BRAKET_AWS_PROFILE": "cyint-ea-dev",
        "QROPE_BRAKET_AWS_REGION": "us-west-1",
        "QROPE_BRAKET_OUTPUT_S3_BUCKET": "localdev-experiments",
        "QROPE_BRAKET_OUTPUT_S3_PREFIX": "phasewrap-rope/test",
        "QROPE_BRAKET_BUDGET_USD_CAP": "1",
        "QROPE_BRAKET_ESTIMATED_COST_USD": "0.01",
        "QROPE_HARDWARE_ROW_LIMIT": "1",
        "QROPE_HARDWARE_SHOT_COUNT": "10",
    }
    config = build_hardware_config(env)
    assert config["provider"] == "amazon_braket"
    assert config["backend"] == "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q"
    assert config["aws_profile"] == "cyint-ea-dev"
    assert config["aws_region"] == "us-west-1"
    assert config["output_s3_bucket"] == "localdev-experiments"
    assert config["output_s3_key_prefix"] == "phasewrap-rope/test"
    assert config["budget_cap_usd"] == 1.0
    assert config["estimated_packet_cost_usd"] == 0.01


def test_braket_hardware_packet_includes_openqasm_programs() -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    packet = freeze_hardware_packet(
        bundle.test,
        {
            "QROPE_REAL_HARDWARE_PROVIDER": "amazon_braket",
            "QROPE_BRAKET_DEVICE_ARN": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
            "QROPE_BRAKET_AWS_PROFILE": "cyint-ea-dev",
            "QROPE_BRAKET_OUTPUT_S3_BUCKET": "localdev-experiments",
            "QROPE_BRAKET_BUDGET_USD_CAP": "1",
            "QROPE_BRAKET_ESTIMATED_COST_USD": "0.01",
            "QROPE_HARDWARE_ROW_LIMIT": "1",
            "QROPE_HARDWARE_SHOT_COUNT": "10",
        },
    )
    provider_execution = packet["provider_execution"]
    assert provider_execution["action_type"] == "braket.ir.openqasm.program"
    assert provider_execution["device_arn"] == packet["backend"]
    assert provider_execution["output_s3_bucket"] == "localdev-experiments"
    assert len(provider_execution["row_programs"]) == 1
    source = provider_execution["row_programs"][0]["action"]["source"]
    assert source.startswith("OPENQASM 3.0;")
    assert "include" not in source
    assert "ry(" in source
    assert "measure q[0]" in source
    assert "measure q[1]" in source


def test_braket_openqasm_adds_cnot_for_entangling_family() -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    packet = freeze_hardware_packet(
        bundle.test,
        {
            "QROPE_REAL_HARDWARE_PROVIDER": "amazon_braket",
            "QROPE_BRAKET_DEVICE_ARN": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
            "QROPE_BRAKET_AWS_PROFILE": "cyint-ea-dev",
            "QROPE_BRAKET_OUTPUT_S3_BUCKET": "localdev-experiments",
            "QROPE_BRAKET_BUDGET_USD_CAP": "1",
            "QROPE_BRAKET_ESTIMATED_COST_USD": "0.01",
            "QROPE_HARDWARE_CIRCUIT_FAMILY": ENTANGLING_CX_CIRCUIT_FAMILY,
            "QROPE_HARDWARE_ROW_LIMIT": "1",
            "QROPE_HARDWARE_SHOT_COUNT": "10",
        },
    )
    source = braket_openqasm_for_hardware_row(packet["rows"][0], ENTANGLING_CX_CIRCUIT_FAMILY)
    assert "cnot q[0], q[1];" in source


def test_entangling_ideal_counts_follow_q1q0_cx_mapping() -> None:
    row = {
        "circuit_parameters": {
            "embedding": ENTANGLING_CX_CIRCUIT_FAMILY,
            "z0_target_from_m8": 0.0,
            "z1_target_from_m12": 0.0,
        }
    }
    counts = ideal_counts_for_hardware_row(row, 4)
    assert counts == {"00": 1, "01": 1, "10": 1, "11": 1}

    row["circuit_parameters"]["z0_target_from_m8"] = -1.0
    row["circuit_parameters"]["z1_target_from_m12"] = 1.0
    counts = ideal_counts_for_hardware_row(row, 4)
    assert counts == {"00": 0, "01": 0, "10": 0, "11": 4}


def test_braket_preflight_ready_for_online_device() -> None:
    class FakeBraketAdapter(EnvironmentHardwareAdapter):
        def _run_aws_json(self, cmd: list[str]) -> dict:
            if "get-caller-identity" in cmd:
                return {
                    "Account": "485386182336",
                    "Arn": "arn:aws:iam::485386182336:user/cyint-ea",
                    "UserId": "AIDATEST",
                }
            if "get-bucket-location" in cmd:
                return {"LocationConstraint": None}
            assert "get-device" in cmd
            return {
                "deviceArn": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
                "deviceName": "Cepheus-1-108Q",
                "deviceStatus": "ONLINE",
                "deviceType": "QPU",
                "providerName": "Rigetti",
                "deviceCapabilities": json.dumps(
                    {
                        "service": {"shotsRange": [10, 50000], "deviceCost": {"price": 0.0009, "unit": "shot"}},
                        "action": {
                            "braket.ir.openqasm.program": {
                                "supportedOperations": ["ry", "cnot"],
                            }
                        },
                    }
                ),
            }

    result = hardware_preflight(
        adapter=FakeBraketAdapter(
            {
                "QROPE_REAL_HARDWARE_PROVIDER": "amazon_braket",
                "QROPE_BRAKET_DEVICE_ARN": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
                "QROPE_BRAKET_AWS_PROFILE": "cyint-ea-dev",
                "QROPE_BRAKET_OUTPUT_S3_BUCKET": "amazon-braket-test-bucket",
                "QROPE_BRAKET_BUDGET_USD_CAP": "1",
                "QROPE_BRAKET_ESTIMATED_COST_USD": "0.01",
                "QROPE_HARDWARE_ROW_LIMIT": "1",
                "QROPE_HARDWARE_SHOT_COUNT": "10",
            }
        ),
        env={
            "QROPE_REAL_HARDWARE_PROVIDER": "amazon_braket",
            "QROPE_BRAKET_DEVICE_ARN": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
            "QROPE_BRAKET_AWS_PROFILE": "cyint-ea-dev",
            "QROPE_BRAKET_OUTPUT_S3_BUCKET": "amazon-braket-test-bucket",
            "QROPE_BRAKET_BUDGET_USD_CAP": "1",
            "QROPE_BRAKET_ESTIMATED_COST_USD": "0.01",
            "QROPE_HARDWARE_ROW_LIMIT": "1",
            "QROPE_HARDWARE_SHOT_COUNT": "10",
        },
    )
    assert result["status"] == "READY"
    assert result["metadata_capture_available"] is True
    assert result["backend_metadata"]["device_status"] == "ONLINE"
    assert result["backend_metadata"]["aws_account_id"] == "485386182336"
    assert result["backend_metadata"]["aws_caller_arn"] == "arn:aws:iam::485386182336:user/cyint-ea"
    assert result["backend_metadata"]["output_s3_bucket"] == "amazon-braket-test-bucket"
    assert result["backend_metadata"]["output_s3_bucket_location"] is None
    assert result["backend_metadata"]["output_s3_bucket_name_pass"] is True
    assert result["backend_metadata"]["required_operations"] == ["ry"]
    assert "ry" in result["backend_metadata"]["supported_operations"]
    assert result["backend_metadata"]["operation_compatibility_pass"] is True
    assert result["backend_metadata"]["shot_range_pass"] is True
    assert result["account_setup_check"]["checked"] is False
    assert "CreateQuantumTask" in result["account_setup_check"]["reason"]


def test_braket_preflight_blocks_invalid_output_bucket_name() -> None:
    class FakeBraketAdapter(EnvironmentHardwareAdapter):
        def _run_aws_json(self, cmd: list[str]) -> dict:
            if "get-caller-identity" in cmd:
                return {"Account": "485386182336", "Arn": "arn:aws:iam::485386182336:user/cyint-ea", "UserId": "AIDATEST"}
            if "get-bucket-location" in cmd:
                return {"LocationConstraint": None}
            assert "get-device" in cmd
            return {
                "deviceArn": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
                "deviceName": "Cepheus-1-108Q",
                "deviceStatus": "ONLINE",
                "deviceType": "QPU",
                "providerName": "Rigetti",
                "deviceCapabilities": json.dumps(
                    {
                        "service": {"shotsRange": [10, 50000], "deviceCost": {"price": 0.0009, "unit": "shot"}},
                        "action": {"braket.ir.openqasm.program": {"supportedOperations": ["ry"]}},
                    }
                ),
            }

    env = {
        "QROPE_REAL_HARDWARE_PROVIDER": "amazon_braket",
        "QROPE_BRAKET_DEVICE_ARN": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
        "QROPE_BRAKET_AWS_PROFILE": "cyint-ea-dev",
        "QROPE_BRAKET_OUTPUT_S3_BUCKET": "localdev-experiments",
        "QROPE_BRAKET_BUDGET_USD_CAP": "1",
        "QROPE_BRAKET_ESTIMATED_COST_USD": "0.01",
        "QROPE_HARDWARE_ROW_LIMIT": "1",
        "QROPE_HARDWARE_SHOT_COUNT": "10",
    }
    result = hardware_preflight(adapter=FakeBraketAdapter(env), env=env)

    assert result["status"] == "BLOCKED"
    assert result["backend_metadata"]["output_s3_bucket_name_pass"] is False
    assert any("bucket name must start with amazon-braket-" in blocker for blocker in result["blockers"])


def test_braket_preflight_blocks_missing_required_operation() -> None:
    class MissingOperationAdapter(EnvironmentHardwareAdapter):
        def _run_aws_json(self, cmd: list[str]) -> dict:
            if "get-caller-identity" in cmd:
                return {"Account": "485386182336", "Arn": "arn:aws:iam::485386182336:user/cyint-ea", "UserId": "AIDATEST"}
            if "get-bucket-location" in cmd:
                return {"LocationConstraint": None}
            assert "get-device" in cmd
            return {
                "deviceArn": "arn:aws:braket:us-west-1::device/qpu/example/MissingRy",
                "deviceName": "MissingRy",
                "deviceStatus": "ONLINE",
                "deviceType": "QPU",
                "providerName": "Example",
                "deviceCapabilities": json.dumps(
                    {
                        "service": {"shotsRange": [10, 100], "deviceCost": {"price": 0.001, "unit": "shot"}},
                        "action": {"braket.ir.openqasm.program": {"supportedOperations": ["x", "z"]}},
                    }
                ),
            }

    env = {
        "QROPE_REAL_HARDWARE_PROVIDER": "amazon_braket",
        "QROPE_BRAKET_DEVICE_ARN": "arn:aws:braket:us-west-1::device/qpu/example/MissingRy",
        "QROPE_BRAKET_AWS_PROFILE": "cyint-ea-dev",
        "QROPE_BRAKET_OUTPUT_S3_BUCKET": "amazon-braket-test-bucket",
        "QROPE_BRAKET_BUDGET_USD_CAP": "1",
        "QROPE_BRAKET_ESTIMATED_COST_USD": "0.01",
        "QROPE_HARDWARE_ROW_LIMIT": "1",
        "QROPE_HARDWARE_SHOT_COUNT": "10",
    }
    result = hardware_preflight(adapter=MissingOperationAdapter(env), env=env)

    assert result["status"] == "BLOCKED"
    assert result["backend_metadata"]["operation_compatibility_pass"] is False
    assert any("required OpenQASM operations" in blocker for blocker in result["blockers"])


def test_braket_preflight_blocks_shots_outside_device_range() -> None:
    class ShotRangeAdapter(EnvironmentHardwareAdapter):
        def _run_aws_json(self, cmd: list[str]) -> dict:
            if "get-caller-identity" in cmd:
                return {"Account": "485386182336", "Arn": "arn:aws:iam::485386182336:user/cyint-ea", "UserId": "AIDATEST"}
            if "get-bucket-location" in cmd:
                return {"LocationConstraint": None}
            assert "get-device" in cmd
            return {
                "deviceArn": "arn:aws:braket:us-west-1::device/qpu/example/ShotRange",
                "deviceName": "ShotRange",
                "deviceStatus": "ONLINE",
                "deviceType": "QPU",
                "providerName": "Example",
                "deviceCapabilities": json.dumps(
                    {
                        "service": {"shotsRange": [100, 1000], "deviceCost": {"price": 0.001, "unit": "shot"}},
                        "action": {"braket.ir.openqasm.program": {"supportedOperations": ["ry"]}},
                    }
                ),
            }

    env = {
        "QROPE_REAL_HARDWARE_PROVIDER": "amazon_braket",
        "QROPE_BRAKET_DEVICE_ARN": "arn:aws:braket:us-west-1::device/qpu/example/ShotRange",
        "QROPE_BRAKET_AWS_PROFILE": "cyint-ea-dev",
        "QROPE_BRAKET_OUTPUT_S3_BUCKET": "amazon-braket-test-bucket",
        "QROPE_BRAKET_BUDGET_USD_CAP": "1",
        "QROPE_BRAKET_ESTIMATED_COST_USD": "0.01",
        "QROPE_HARDWARE_ROW_LIMIT": "1",
        "QROPE_HARDWARE_SHOT_COUNT": "10",
    }
    result = hardware_preflight(adapter=ShotRangeAdapter(env), env=env)

    assert result["status"] == "BLOCKED"
    assert result["backend_metadata"]["shot_range_pass"] is False
    assert any("outside device shotsRange" in blocker for blocker in result["blockers"])


def test_braket_run_packet_submits_waits_and_fetches_result() -> None:
    class CompletedBraketAdapter(EnvironmentHardwareAdapter):
        def __init__(self, env: dict[str, str]) -> None:
            super().__init__(env)
            self.commands: list[list[str]] = []

        def _run_aws_json(self, cmd: list[str]) -> dict:
            self.commands.append(cmd)
            if "get-device" in cmd:
                return {
                    "deviceArn": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
                    "deviceName": "Cepheus-1-108Q",
                    "deviceStatus": "ONLINE",
                    "deviceType": "QPU",
                    "providerName": "Rigetti",
                    "deviceCapabilities": json.dumps(
                        {"service": {"shotsRange": [10, 50000], "deviceCost": {"price": 0.000425, "unit": "shot"}}}
                    ),
                }
            if "create-quantum-task" in cmd:
                assert "--action" in cmd
                assert "--output-s3-bucket" in cmd
                return {"quantumTaskArn": "arn:aws:braket:us-west-1:485386182336:quantum-task/task-1"}
            if "get-quantum-task" in cmd:
                return {
                    "quantumTaskArn": "arn:aws:braket:us-west-1:485386182336:quantum-task/task-1",
                    "status": "COMPLETED",
                    "outputS3Directory": "s3://localdev-experiments/results/task-1",
                }
            raise AssertionError(f"unexpected AWS JSON command: {cmd}")

        def _run_aws_text(self, cmd: list[str]) -> str:
            self.commands.append(cmd)
            assert cmd[:3] == ["aws", "s3", "cp"]
            assert cmd[-1] == "-"
            return json.dumps({"measurementCounts": {"00": 3, "01": 2, "10": 4, "11": 1}})

    env = {
        "QROPE_REAL_HARDWARE_PROVIDER": "amazon_braket",
        "QROPE_BRAKET_DEVICE_ARN": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
        "QROPE_BRAKET_AWS_PROFILE": "cyint-ea-dev",
        "QROPE_BRAKET_AWS_REGION": "us-west-1",
        "QROPE_BRAKET_OUTPUT_S3_BUCKET": "localdev-experiments",
        "QROPE_BRAKET_OUTPUT_S3_PREFIX": "phasewrap-rope/test",
        "QROPE_BRAKET_BUDGET_USD_CAP": "1",
        "QROPE_BRAKET_ESTIMATED_COST_USD": "0.01",
        "QROPE_HARDWARE_ROW_LIMIT": "1",
        "QROPE_HARDWARE_SHOT_COUNT": "10",
    }
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    packet = freeze_hardware_packet(bundle.test[:1], env)
    adapter = CompletedBraketAdapter(env)
    execution = adapter.run_packet(packet)

    assert execution["status"] == "COMPLETED"
    job = execution["jobs"][0]
    assert job["job_id"] == "arn:aws:braket:us-west-1:485386182336:quantum-task/task-1"
    assert job["raw_counts_by_row"][0]["counts"] == {"00": 3, "01": 2, "10": 4, "11": 1}
    assert job["raw_counts_by_row"][0]["result_s3_uri"] == "s3://localdev-experiments/results/task-1/results.json"
    assert execution["backend_metadata"]["device_status"] == "ONLINE"
    assert execution["calibration_metadata"]["source"] == "aws_braket_get_device"
    assert any("create-quantum-task" in command for command in adapter.commands)
    assert any(command[:3] == ["aws", "s3", "cp"] for command in adapter.commands)


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


def test_braket_agreement_error_is_classified_as_hardware_blocked() -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    env = {
        "QROPE_REAL_HARDWARE_PROVIDER": "amazon_braket",
        "QROPE_BRAKET_DEVICE_ARN": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
        "QROPE_BRAKET_AWS_PROFILE": "cyint-ea-dev",
        "QROPE_BRAKET_OUTPUT_S3_BUCKET": "localdev-experiments",
        "QROPE_BRAKET_BUDGET_USD_CAP": "1",
        "QROPE_BRAKET_ESTIMATED_COST_USD": "0.01",
        "QROPE_HARDWARE_ROW_LIMIT": "1",
        "QROPE_HARDWARE_SHOT_COUNT": "10",
    }
    result = run_hardware_packet(bundle.test, adapter=BraketAgreementBlockedAdapter(), env=env)
    assert result["status"] == "FAIL_STOP"
    assert result["outcome"] == "hardware-blocked"
    assert result["execution"]["status"] == "BLOCKED"
    assert result["execution"]["error_category"] == "aws_braket_user_agreement_not_accepted"
    assert result["gate_pass"] is False


def test_stage4_sweep_summary_preserves_braket_blocker_details(tmp_path) -> None:
    result = {
        "status": "FAIL_STOP",
        "outcome": "hardware-blocked",
        "gate_pass": False,
        "packet": {"packet_id": "qrope-hardware-test"},
        "preflight": {
            "status": "READY",
            "blockers": [],
            "account_setup_check": {"checked": False, "reason": "validated on CreateQuantumTask"},
        },
        "execution": {
            "status": "BLOCKED",
            "error_category": "aws_braket_user_agreement_not_accepted",
            "blockers": ["Amazon Braket user agreement has not been accepted for this AWS account"],
            "rows": [],
            "jobs": [],
            "error": "AccessDeniedException",
        },
    }
    backend = {
        "provider": "amazon_braket",
        "backend": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
    }
    summary = _artifact_summary(
        result,
        backend,
        shot_target=10,
        shot_count=10,
        row_limit=1,
        result_dir=tmp_path,
    )
    assert summary["outcome"] == "hardware-blocked"
    assert summary["execution_status"] == "BLOCKED"
    assert summary["error_category"] == "aws_braket_user_agreement_not_accepted"
    assert summary["blockers"] == ["Amazon Braket user agreement has not been accepted for this AWS account"]
    assert summary["task_arns"] == []
    assert summary["result_s3_uris"] == []


def test_braket_summaries_extract_completed_task_artifacts(tmp_path) -> None:
    execution = {
        "status": "COMPLETED",
        "jobs": [
            {
                "job_id": "arn:aws:braket:us-west-1:485386182336:quantum-task/task-1",
                "provider_job_records": [
                    {"job_id": "arn:aws:braket:us-west-1:485386182336:quantum-task/task-1"}
                ],
                "raw_counts_by_row": [
                    {
                        "row_id": "hwrow-000",
                        "counts": {"00": 5, "01": 5},
                        "result_s3_uri": "s3://localdev-experiments/path/task-1/results.json",
                    }
                ],
            }
        ],
    }
    result = {
        "status": "PASS",
        "outcome": "hardware-positive",
        "gate_pass": True,
        "packet": {"packet_id": "qrope-hardware-task-test"},
        "preflight": {"status": "READY", "blockers": []},
        "execution": execution,
        "evaluation": {},
    }
    backend = {
        "provider": "amazon_braket",
        "backend": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
    }

    smoke_summary = _braket_artifact_summary(result, tmp_path)
    sweep_summary = _artifact_summary(
        result,
        backend,
        shot_target=10,
        shot_count=10,
        row_limit=1,
        result_dir=tmp_path,
    )

    for summary in (smoke_summary, sweep_summary):
        assert summary["task_arns"] == ["arn:aws:braket:us-west-1:485386182336:quantum-task/task-1"]
        assert summary["result_s3_uris"] == ["s3://localdev-experiments/path/task-1/results.json"]


def test_stage4_sweep_split_env_list_accepts_commas_and_semicolons() -> None:
    assert _split_env_list("amazon_braket, ibm_runtime;quandela") == [
        "amazon_braket",
        "ibm_runtime",
        "quandela",
    ]


def test_stage4_sweep_uses_braket_live_cost_for_estimate(monkeypatch, tmp_path) -> None:
    captured_env = {}

    def fake_run_hardware_packet(rows: list, *, env: dict) -> dict:
        captured_env.update(env)
        return {
            "status": "FAIL_STOP",
            "outcome": "hardware-blocked",
            "gate_pass": False,
            "packet": {"packet_id": "qrope-hardware-cost-test"},
            "preflight": {"status": "READY", "blockers": []},
            "execution": {"status": "BLOCKED", "jobs": [], "rows": []},
            "evaluation": {},
        }

    monkeypatch.setattr(hardware_sweep, "LOG_ROOT", tmp_path)
    monkeypatch.setattr(hardware_sweep, "run_hardware_packet", fake_run_hardware_packet)
    backend = {
        "provider": "amazon_braket",
        "backend": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
        "aws_profile": "cyint-ea-dev",
        "aws_region": "us-west-1",
        "output_s3_bucket": "localdev-experiments",
        "max_shots": 50000,
        "cost_per_shot_usd": 0.000425,
    }

    result, result_dir = hardware_sweep.run_single_backend(
        base_env={},
        backend=backend,
        row_limit=1,
        family="two_qubit_zz_expectation_phase_wrap_v1",
        shot_target=10,
        budget_cap=1.0,
    )

    assert result["outcome"] == "hardware-blocked"
    assert captured_env["QROPE_BRAKET_ESTIMATED_COST_USD"] == "0.00425"
    assert captured_env["QROPE_BRAKET_COST_PER_SHOT_USD"] == "0.000425"
    summary = json.loads((result_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["cost_per_shot_usd"] == 0.000425


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
    assert result["evaluation"]["metadata_complete"] is True
    assert result["evaluation"]["comparability_pass"] is True
    assert result["evaluation"]["witness"]["mae"] >= 0.0
    assert result["evaluation"]["control"]["mae"] >= 0.0
    assert result["outcome"] in {"hardware-positive", "hardware-negative"}


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


def test_offline_stage4_verifier_accepts_flat_summary(tmp_path) -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    result = run_hardware_packet(bundle.test[:4], adapter=IdealHardwareAdapter(), env=HARDWARE_ENV)
    packet_path = tmp_path / "frozen_packet.json"
    execution_path = tmp_path / "execution.json"
    evaluation_path = tmp_path / "evaluation.json"
    summary_path = tmp_path / "summary.json"
    packet_path.write_text(json.dumps(result["packet"], indent=2), encoding="utf-8")
    execution_path.write_text(json.dumps(result["execution"], indent=2), encoding="utf-8")
    evaluation_path.write_text(json.dumps(result["evaluation"], indent=2), encoding="utf-8")
    summary_path.write_text(
        json.dumps({"status": result["status"], "outcome": result["outcome"]}, indent=2),
        encoding="utf-8",
    )

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
    assert any(check["name"] == "summary_status_matches_recomputed" and check["pass"] for check in verification["checks"])
    assert any(check["name"] == "summary_outcome_matches_recomputed" and check["pass"] for check in verification["checks"])


def test_offline_stage4_verifier_matches_individual_braket_task_id(tmp_path) -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    result = run_hardware_packet(bundle.test[:4], adapter=IdealHardwareAdapter(), env=HARDWARE_ENV)
    first_task = "arn:aws:braket:us-west-1:485386182336:quantum-task/task-1"
    second_task = "arn:aws:braket:us-west-1:485386182336:quantum-task/task-2"
    result["packet"]["provider"] = "amazon_braket"
    result["packet"]["backend"] = "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q"
    result["execution"]["jobs"][0]["provider"] = "amazon_braket"
    result["execution"]["jobs"][0]["backend"] = result["packet"]["backend"]
    result["execution"]["jobs"][0]["job_id"] = f"{first_task},{second_task}"
    result["execution"]["jobs"][0]["provider_job_records"] = [
        {"job_id": first_task},
        {"job_id": second_task},
    ]
    packet_path = tmp_path / "frozen_packet.json"
    execution_path = tmp_path / "execution.json"
    evaluation_path = tmp_path / "evaluation.json"
    summary_path = tmp_path / "summary.json"
    packet_path.write_text(json.dumps(result["packet"], indent=2), encoding="utf-8")
    execution_path.write_text(json.dumps(result["execution"], indent=2), encoding="utf-8")
    evaluation_path.write_text(json.dumps(result["evaluation"], indent=2), encoding="utf-8")
    summary_path.write_text(json.dumps({"status": result["status"], "outcome": result["outcome"]}, indent=2), encoding="utf-8")

    verification = verify_packet_files(
        packet_path=packet_path,
        execution_path=execution_path,
        evaluation_path=evaluation_path,
        summary_path=summary_path,
        expected_provider="amazon_braket",
        expected_backend="arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
        expected_job_id=second_task,
    )

    assert verification["pass"] is True
    assert verification["job_ids"] == [first_task, second_task]


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
