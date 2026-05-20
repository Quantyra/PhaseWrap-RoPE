# Braket Hardware Runbook

This note records the Amazon Braket Stage 4 execution path, setup blockers, and completed hardware smoke observed on 2026-05-19.

## Prepared Target

- Provider: `amazon_braket`
- AWS account: `485386182336`
- AWS profile used: `cyint-ea-dev`
- Region: `us-west-1`
- Device ARN: `arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q`
- Device status observed by preflight: `ONLINE`
- S3 output bucket rejected during setup: `localdev-experiments`
- S3 output bucket used for completed task: `amazon-braket-us-west-1-485386182336`
- Live device cost observed by preflight: `0.000425` USD per shot
- Current S3 bucket region: `localdev-experiments` reports `LocationConstraint: null`, which is AWS `us-east-1`
- Braket-compatible S3 bucket region: `amazon-braket-us-west-1-485386182336` reports `LocationConstraint: us-west-1`
- Prior S3 bucket name status: rejected by `CreateQuantumTask` because it does not start with `amazon-braket-`
- Standard same-region bucket `amazon-braket-us-west-1-485386182336` now exists and was used for the completed task.
- Standard same-region bucket `amazon-braket-eu-north-1-485386182336` was checked earlier and not found.

## Resolved Setup Blockers

An earlier `CreateQuantumTask` attempt was denied before a task ARN was created:

```text
ValidationException: The bucket localdev-experiments does not start with 'amazon-braket-'.
```

The Braket-compatible bucket `amazon-braket-us-west-1-485386182336` was created in `us-west-1` and cleared this blocker.

Earlier in the same setup pass, the user-agreement blocker was reproduced against online QPUs in multiple regions:

- `us-west-1`: Rigetti `Cepheus-1-108Q`, `0.000425` USD per shot
- `eu-north-1`: IQM `Garnet`, `0.00145` USD per shot

Both attempts used AWS account `485386182336` and failed before creating a Braket task ARN.

The later completed task shows the account path can now create Braket hardware tasks.

## Final Hardware Gate

The eight-row, 1000-shot Rigetti hardware gate completed and passed on Amazon Braket. This is the preferred final hardware artifact because it has materially better shot statistics than the earlier 10-shot smoke:

- Artifact directory: `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z`
- Packet ID: `qrope-hardware-5244f90bce2f93b8`
- Task count: `8`
- Shots per task: `1000`
- Task status: all `COMPLETED`
- Result S3 URI count: `8`
- Hardware evaluation outcome: `hardware-positive`
- Gate pass: `true`
- Witness metrics: `mae=0.069901`, `rank_correlation=0.786644`
- Control metrics: `mae=0.149995`, `rank_correlation=0.121232`
- Offline verifier: `pass=true`

Task ARNs:

- `arn:aws:braket:us-west-1:485386182336:quantum-task/e35e3aa6-a1c4-4e82-91e6-0696fa305429`
- `arn:aws:braket:us-west-1:485386182336:quantum-task/f00f3214-d6ad-4b79-b8b1-32f957e27126`
- `arn:aws:braket:us-west-1:485386182336:quantum-task/c3487449-55b4-4c33-b1db-3aa05e3ae63c`
- `arn:aws:braket:us-west-1:485386182336:quantum-task/06acf815-ef22-43c2-80ea-54c75608a10e`
- `arn:aws:braket:us-west-1:485386182336:quantum-task/9c2467b7-9322-416c-9379-b044d0fbe05b`
- `arn:aws:braket:us-west-1:485386182336:quantum-task/9471b78d-2b23-40cf-af7f-4cb87a0d5d37`
- `arn:aws:braket:us-west-1:485386182336:quantum-task/a1b3207e-46bf-43a0-9736-4a3aa1e8cda2`
- `arn:aws:braket:us-west-1:485386182336:quantum-task/277ea374-46d3-47fe-9fb2-fb330ccf9498`

Prior lower-shot runs:

- One-row, 10-shot smoke completed with task ARN `arn:aws:braket:us-west-1:485386182336:quantum-task/cfd7f938-4a7f-4d44-abd5-ce30089834de`; it produced `hardware-negative`.
- Eight-row, 10-shot gate completed and passed at `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100218Z`, but the 1000-shot run above supersedes it for statistical stability.

## Hardware Gate Command

To rerun the smoke:

```powershell
$env:PYTHONPATH = "src"
python scripts\run_stage4_hardware_sweep.py `
  --providers amazon_braket `
  --braket-device-arn arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q `
  --braket-profile cyint-ea-dev `
  --braket-region us-west-1 `
  --braket-s3-bucket amazon-braket-us-west-1-485386182336 `
  --braket-timeout-sec 600 `
  --braket-poll-interval-sec 15 `
  --target-shots 10 `
  --row-limit 1 `
  --budget-usd-cap 1 `
  --require-pass
```

The command writes a Stage 4 sweep artifact directory containing:

- `frozen_packet.json`
- `preflight.json`
- `execution.json`
- `evaluation.json`
- `run_payload.json`
- `summary.json`

Completion requires a nonempty Braket task ARN, downloaded result S3 URI, completed execution metadata, and a passing Stage 4 hardware evaluation.
The adapter/execution path is complete once a task ARN, S3 result URI, completed execution metadata, and evaluation are present. A positive hardware claim still requires `gate_pass: true`.
