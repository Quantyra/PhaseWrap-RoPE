# PhaseWrap-RoPE

[![CI](https://github.com/Quantyra/PhaseWrap-RoPE/actions/workflows/ci.yml/badge.svg)](https://github.com/Quantyra/PhaseWrap-RoPE/actions/workflows/ci.yml)

PhaseWrap-RoPE is Quantyra's public research repository for phase-wrapped positional scoring and small-circuit hardware validation.

This repository is intended for open scientific review of the PhaseWrap-RoPE method, validation scripts, evidence packets, and publication materials. It is not a claim of general quantum advantage, full transformer-scale superiority, entanglement-based advantage, or cross-backend hardware robustness.

## Status

- `Patent/IP posture`: USPTO provisional submission received `2026-05-18`; the Electronic Acknowledgement Receipt lists application `64/068,121` and Patent Center `76347440`; final Filing Receipt pending. See [Patent status note](docs/publication/patent-status-note-v1.md).
- `License`: GNU Affero General Public License v3.0 only (`AGPL-3.0-only`).
- `Publication posture`: bounded, reproducible, evidence-disciplined.
- `Current evidence posture`: Stage 4 real-noisy-hardware results for bounded frozen packet/backend/date/calibration contexts, including IBM Fez positives, Amazon Braket/Rigetti product-state positive evidence, and provider-aware Amazon Braket CX positive recomputations from committed raw counts.
- `Hardware posture`: IBM Fez product-state, IBM Fez CX, Amazon Braket/Rigetti product-state, and Amazon Braket CX lanes have completed active Stage 4 hardware artifacts; additional IBM machines are deferred from the active sweep; Amazon Braket/IonQ was checked on 2026-05-19 and was not run because Forte devices were `OFFLINE` and Aria 1 was `RETIRED`; AQT IBEX Q1 is deferred due cost.

## Claim boundary

The public claim frame for this repository is:

- PhaseWrap-RoPE defines phase-wrap residual features using mod-8 and mod-12 structure.
- The SQR score uses the product of the mod-8 and mod-12 signed margins.
- The evidence lane includes deterministic frozen-packet validation, raw counts, backend metadata, and offline recomputation.
- The Stage 4 result is a bounded real-hardware validation for the frozen packet reported in this repository.
- The Amazon Braket/Rigetti replication artifact is an 8-row, 1000-shot-per-row product-state hardware-positive run with offline verifier pass.
- The current active hardware evidence includes two product-state angle-encoding/readout witness artifacts: IBM Fez and Amazon Braket/Rigetti.
- The entangling CX witness family is implemented as `two_qubit_cx_parity_phase_wrap_v2`; IBM Fez and Amazon Braket executions on Rigetti Cepheus, IQM Garnet, and IQM Emerald verify as hardware-positive when decoded with the manifest-declared provider bitstring order. This does not support a general cross-backend robustness claim.

The public claim frame excludes:

- broad quantum advantage;
- full transformer-scale validation;
- general cross-backend superiority;
- claims that PhaseWrap-RoPE improves production language-model quality;
- claims that one backend/date/calibration result generalizes without additional evidence.

## Key documents

- [Manuscript-to-provisional support audit](docs/publication/manuscript-to-provisional-support-audit-v1.md)
- [Repository paper v1](docs/publication/qrope-paper-v1.md)
- [Patent status note](docs/publication/patent-status-note-v1.md)
- [Quickstart and results summary](docs/publication/quickstart-results-summary-v1.md)
- [External review response](docs/publication/external-review-response-v1.md)
- [Replication plan](docs/publication/replication-plan-v1.md)
- [External release plan](docs/publication/external-release-plan-v1.md)
- [PhaseWrap-RoPE method schematic](docs/publication/figures/qrope-method-schematic-v1.svg)
- [Validation pipeline figure](docs/publication/figures/qrope-validation-pipeline-v1.svg)
- [Stage 4 comparison figure](docs/publication/figures/qrope-stage4-comparison-v1.svg)
- [Open-source release checklist](docs/publication/open-source-release-checklist-v1.md)
- [Patent notice](PATENTS.md)
- [Stage 4 real-hardware validation result](docs/research/q-rope-stage4-real-hardware-validation-result-v1.md)
- [Stage 4 CX portability diagnostic](docs/research/q-rope-stage4-cx-portability-diagnostic-v1.md)
- [Amazon Braket hardware runbook](docs/evidence/E002-braket-hardware-runbook.md)
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

IBM and Amazon Braket hardware reruns require separate cloud credentials and provider dependencies. The local method check and saved-packet verifier do not require hardware credentials.

Install IBM Runtime dependencies only when preparing a real hardware run:

```bash
python -m pip install -e ".[ibm]"
```

Install Amazon Braket dependencies only when preparing a Braket hardware run:

```bash
python -m pip install -e ".[braket]"
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

Verify the Stage 4 hardware sweep manifest:

```bash
python scripts/verify_stage4_hardware_sweep.py
```

This verifier recomputes metrics for the active sweep records whose packet/execution/evaluation artifacts are present. The current active sweep covers the committed IBM Fez product-state packet, IBM Fez CX packet, Amazon Braket/Rigetti product-state artifact, and Amazon Braket CX artifacts on Rigetti Cepheus, IQM Garnet, and IQM Emerald. The verifier is provider-aware: IBM records use `q1q0` bitstring decoding and Amazon Braket records use `q0q1` decoding as declared in the manifest. Additional IBM backends and Amazon Braket/IonQ are documented as deferred or excluded targets unless real raw-count artifacts are later added.

Audit the earlier Braket CX generic-decoder failure from saved raw counts:

```bash
python scripts/diagnose_stage4_cx_portability.py
```

The diagnostic documents why the earlier generic `q1q0` Braket CX classification was corrected in the provider-aware sweep verifier.

## Reviewer path in 10 minutes

- Read the claim boundary in this README.
- Open [Quickstart and results summary](docs/publication/quickstart-results-summary-v1.md).
- Open [Repository paper v1](docs/publication/qrope-paper-v1.md).
- Inspect [Patent status note](docs/publication/patent-status-note-v1.md).
- Inspect the Stage 4 packet files under `logs/automated_stage_gates/stage4_hardware_packet/`.
- Run `python scripts/verify_stage4_hardware_packet.py`.
- Inspect `logs/automated_stage_gates/stage4_hardware_sweep/manifest.json`.
- Run `python scripts/verify_stage4_hardware_sweep.py`.

## CI and test coverage

GitHub Actions runs the public-review Stage 4/verifier test subset on Python `3.11` and `3.12`:

```bash
pytest tests/test_automated_stage_gates.py -k "not quandela" --cov=qrope --cov-report=term-missing --cov-report=xml
```

Coverage XML is uploaded as a workflow artifact. The broader local test suite remains useful, but it includes optional provider-specific paths that should not be treated as the public-review badge gate until those optional dependencies are standardized.

## Publication use

If you cite or discuss this work, use the bounded posture:

> PhaseWrap-RoPE is a phase-wrap positional-encoding and validation method with repository-backed deterministic evidence packets, including a bounded Stage 4 real-hardware validation result.

Do not restate the result as a proof of broad quantum transformer superiority.

## Research Roadmap

The current release is ready for bounded repository/preprint publication. The next research work should be evidence-producing rather than claim-broadening:

| Priority | Work item | Purpose |
| --- | --- | --- |
| 1 | Toy transformer or attention-scoring benchmark against standard RoPE | Test downstream impact on a concrete metric such as length extrapolation or attention-score stability. |
| 2 | DOI/preprint release hygiene | Make the current evidence package citable before further experiments change the repository state. |
| 3 | Independent hardware replication | Add new packet/date/backend records, including IonQ or Quandela only when provider availability, credentials, and budget support real artifacts. |
| 4 | Larger or error-aware witnesses | Explore larger qubit witnesses or mitigation analysis after downstream and replication evidence justify the added complexity. |

The mod-8/mod-12 choice is a fixed first-release design: two wrapped residual bases with one-step thresholds at `pi/4` and `pi/6`, producing a cross-band product signal. Other period pairs are future ablation targets, not current evidence.

## Licensing and patent notice

Software in this repository is released under `AGPL-3.0-only`. Patent and IP-status boundaries are documented in [PATENTS.md](PATENTS.md) and [Patent status note](docs/publication/patent-status-note-v1.md).
