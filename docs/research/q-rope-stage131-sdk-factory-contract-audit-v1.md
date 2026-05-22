# QRoPE Stage 131 - SDK Factory Contract Audit

## Objective
Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, under fixed circuit width.

## Result
Stage 131 freezes provider-specific SDK live-client factory contracts for IBM Runtime and Amazon Braket while preserving the current no-submission boundary.

Current decision:

`SDK_FACTORY_CONTRACTS_READY_EXECUTION_BLOCKED`

## What this supports
- IBM Runtime and Amazon Braket adapters expose testable live-client factory contracts.
- Contracts include official documentation URLs, required imports, required environment references, activation gates, factory steps, and result-shape obligations.
- SDK wrapper activation now has a concrete contract to preserve after Stage 106, Stage 111, and Stage 129 readiness clear.

## What this does not support
- No hardware job submission occurred.
- No provider credentials or secret values were read or recorded.
- No live provider SDK client was created.
- No real provider result records were produced.
- No noisy-hardware robustness or PhaseWrap advantage claim is supported.

## Artifacts
- `logs/automated_stage_gates/stage131_sdk_factory_contract_audit/manifest.json`
- `logs/automated_stage_gates/stage131_sdk_factory_contract_audit/results.json`
- `logs/automated_stage_gates/stage131_sdk_factory_contract_audit/summary.csv`

## Next gate
Activate the guarded SDK client wrappers against these contracts only after Stage 106/111 readiness and Stage 129 cutover authorization clear for the target provider.
