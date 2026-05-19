# QRoPE

[![CI](https://github.com/Quantyra/QRoPE/actions/workflows/ci.yml/badge.svg)](https://github.com/Quantyra/QRoPE/actions/workflows/ci.yml)

QRoPE is Quantyra's public research repository for Quantum Rotary Positional Encoding: a bounded evidence lane for phase-wrapped positional scoring and small-circuit hardware validation.

This repository is intended for open scientific review of the QRoPE method, validation scripts, evidence packets, and publication materials. It is not a claim of general quantum advantage, full transformer-scale superiority, entanglement-based advantage, or cross-backend hardware robustness.

## Status

- `Patent/IP posture`: USPTO provisional submission received `2026-05-18`; the Electronic Acknowledgement Receipt lists application `64/068,121` and Patent Center `76347440`; final Filing Receipt pending. See [Patent status note](docs/publication/patent-status-note-v1.md).
- `License`: GNU Affero General Public License v3.0 only (`AGPL-3.0-only`).
- `Publication posture`: bounded, reproducible, evidence-disciplined.
- `Current evidence posture`: Stage 4 real-noisy-hardware positive result for one frozen packet/backend/date/calibration context.
- `Hardware posture`: IBM Quantum is the only hardware lane currently available for QRoPE Stage 4; IonQ and Quandela remain simulator paths unless explicitly reconfigured.

## Claim boundary

The public claim frame for this repository is:

- QRoPE defines phase-wrap residual features using mod-8 and mod-12 structure.
- The SQR score uses the product of the mod-8 and mod-12 signed margins.
- The evidence lane includes deterministic frozen-packet validation, raw counts, backend metadata, and offline recomputation.
- The Stage 4 result is a bounded real-hardware validation for the frozen packet reported in this repository.
- The current hardware evidence includes a two-qubit product-state angle-encoding/readout witness and an executed entangling CX witness family; neither should be described as evidence of nonclassical advantage.
- The entangling CX witness family is implemented as `two_qubit_cx_parity_phase_wrap_v2` and is included in the completed hardware comparison report.

The public claim frame excludes:

- broad quantum advantage;
- full transformer-scale validation;
- general cross-backend superiority;
- claims that QRoPE improves production language-model quality;
- claims that one backend/date/calibration result generalizes without additional evidence.

## Key documents

- [Manuscript-to-provisional support audit](docs/publication/manuscript-to-provisional-support-audit-v1.md)
- [Repository paper v1](docs/publication/qrope-paper-v1.md)
- [Patent status note](docs/publication/patent-status-note-v1.md)
- [External review response](docs/publication/external-review-response-v1.md)
- [Replication plan](docs/publication/replication-plan-v1.md)
- [External release plan](docs/publication/external-release-plan-v1.md)
- [QRoPE method schematic](docs/publication/figures/qrope-method-schematic-v1.svg)
- [Validation pipeline figure](docs/publication/figures/qrope-validation-pipeline-v1.svg)
- [Stage 4 comparison figure](docs/publication/figures/qrope-stage4-comparison-v1.svg)
- [Open-source release checklist](docs/publication/open-source-release-checklist-v1.md)
- [Patent notice](PATENTS.md)
- [Stage 4 real-hardware validation result](docs/research/q-rope-stage4-real-hardware-validation-result-v1.md)
- [Automated terminal human-review packet](docs/evidence/review-packets/qrope-automated-terminal-v1/qrope-terminal-human-review-packet-v1.md)
- [Phase-wrap algorithm note](docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md)

## Quickstart

Recommended local environment: Python `3.11+`.

```bash
python -m pip install -e ".[dev]"
```

Run a simulator-free local method check with no IBM credentials:

```bash
python - <<'PY'
from qrope.automated_stage_gates import phase_margins, normalized_phase_label

margins = phase_margins(delta_a=1, delta_b=4)
print(margins)
print("label", normalized_phase_label(margins["score"]))
PY
```

IBM hardware reruns require separate IBM Quantum credentials and runtime dependencies. The local method check and saved-packet verifier do not require IBM credentials.

Install IBM Runtime dependencies only when preparing a real hardware run:

```bash
python -m pip install -e ".[ibm]"
```

Verify the saved Stage 4 packet arithmetic from the published raw-count evidence:

```bash
python scripts/verify_stage4_hardware_packet.py
```

Expected verifier summary:

```json
{
  "pass": true,
  "provider": "ibm_runtime",
  "backend": "ibm_fez",
  "packet_id": "qrope-hardware-73c61893576297ff",
  "job_ids": ["d84jbq00bvlc73d4krr0"]
}
```

## Reviewer path in 10 minutes

- Read the claim boundary in this README.
- Open [Repository paper v1](docs/publication/qrope-paper-v1.md).
- Inspect [Patent status note](docs/publication/patent-status-note-v1.md).
- Inspect the Stage 4 packet files under `logs/automated_stage_gates/stage4_hardware_packet/`.
- Run `python scripts/verify_stage4_hardware_packet.py`.

## CI and test coverage

GitHub Actions runs the public-review Stage 4/verifier test subset on Python `3.11` and `3.12`:

```bash
pytest tests/test_automated_stage_gates.py -k "not quandela" --cov=qrope --cov-report=term-missing --cov-report=xml
```

Coverage XML is uploaded as a workflow artifact. The broader local test suite remains useful, but it includes optional provider-specific paths that should not be treated as the public-review badge gate until those optional dependencies are standardized.

## Publication use

If you cite or discuss this work, use the bounded posture:

> QRoPE is a phase-wrap positional-encoding and validation method with repository-backed deterministic evidence packets, including a bounded Stage 4 real-hardware validation result.

Do not restate the result as a proof of broad quantum transformer superiority.

## Licensing and patent notice

Software in this repository is released under `AGPL-3.0-only`. Patent and IP-status boundaries are documented in [PATENTS.md](PATENTS.md) and [Patent status note](docs/publication/patent-status-note-v1.md).
