# PhaseWrap-RoPE

[![CI](https://github.com/Quantyra/PhaseWrap-RoPE/actions/workflows/ci.yml/badge.svg)](https://github.com/Quantyra/PhaseWrap-RoPE/actions/workflows/ci.yml)
[![Open verification in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Quantyra/PhaseWrap-RoPE/blob/main/docs/notebooks/phasewrap_rope_verify.ipynb)

PhaseWrap-RoPE is Quantyra's public research repository for a phase-wrap positional scoring rule with two-qubit hardware readout.

This repository is intended for open scientific review of the PhaseWrap-RoPE scoring rule, validation scripts, evidence packets, and publication materials. It is not a claim of general quantum advantage, full transformer-scale superiority, entanglement-based advantage, or cross-backend hardware robustness.

Repository naming note: public materials use `PhaseWrap-RoPE`; Python imports, script paths, packet IDs, and evidence IDs retain the existing `qrope` stem.

## Status

- `Patent/IP posture`: USPTO provisional submission received `2026-05-18`; the Electronic Acknowledgement Receipt lists application `64/068,121` and Patent Center `76347440`; final Filing Receipt pending. See [Patent status note](docs/publication/patent-status-note-v1.md).
- `License`: GNU Affero General Public License v3.0 only (`AGPL-3.0-only`).
- `Publication posture`: bounded, reproducible, evidence-disciplined.
- `Current evidence posture`: Stage 4 real-noisy-hardware results for bounded frozen packet/backend/date/calibration contexts, including IBM Fez positives, Amazon Braket/Rigetti product-state positive evidence, and provider-aware Amazon Braket CX positive recomputations from committed raw counts.
- `Hardware posture`: IBM Fez product-state, IBM Fez CX, Amazon Braket/Rigetti product-state, and Amazon Braket CX lanes have completed active Stage 4 hardware artifacts; additional IBM machines are deferred from the active sweep; Amazon Braket/IonQ was checked on 2026-05-19 and was not run because Forte devices were `OFFLINE` and Aria 1 was `RETIRED`; AQT IBEX Q1 is deferred due cost.
- `Evidence tree posture`: `logs/automated_stage_gates/stage4_hardware_packet/` remains the default single-packet verifier path. The same IBM Fez 2026-05-17 product-state pass is also preserved as an immutable named run under `logs/automated_stage_gates/stage4_hardware_packet_ibm_fez_20260517_pass/` for the sweep manifest.

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
- [Stage 5 attention baseline result](docs/research/q-rope-stage5-attention-baselines-v1.md)
- [Stage 6 downstream attention result](docs/research/q-rope-stage6-downstream-attention-v1.md)
- [Stage 7 toy transformer ablation](docs/research/q-rope-stage7-toy-transformer-ablation-v1.md)
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

The default single-packet verifier output is checked in CI against the README expected summary:

```bash
python scripts/check_readme_verifier_output.py
```

Audit the earlier Braket CX generic-decoder failure from saved raw counts:

```bash
python scripts/diagnose_stage4_cx_portability.py
```

The diagnostic documents why the earlier generic `q1q0` Braket CX classification was corrected in the provider-aware sweep verifier.

Run the deterministic Stage 5 attention-scoring baselines:

```bash
python scripts/run_stage5_attention_baselines.py
```

Stage 5 compares the phase-wrap scoring rule against mod-24 lookup, `m8`/`m12`/`m8*m12`, a shallow regression tree, RoPE-style, sinusoidal, and ALiBI-style attention-scoring baselines. The current synthetic label is exactly recoverable by mod-24 lookup and the direct `m8*m12` feature baseline, so this closes the requested baseline gap but does not support transformer-scale superiority.

Run the deterministic Stage 6 toy downstream attention benchmark:

```bash
python scripts/run_stage6_downstream_attention.py
```

Stage 6 mixes token/content compatibility with phase-wrap positional signal so mod-24 lookup and direct `m8/m12/m8*m12` baselines are no longer exact. On the fixed packet, `phasewrap_rope_attention` has the lowest MAE, while the claim remains limited to this toy downstream benchmark.

Run the deterministic Stage 7 four-layer toy transformer ablation:

```bash
python scripts/run_stage7_toy_transformer_ablation.py
```

Stage 7 swaps the PhaseWrap positional term into a four-layer attention-only toy transformer on a synthetic length-extrapolation retrieval task. On the fixed packet, `phasewrap_rope_4layer` has the best top-1 and MRR; this remains a small synthetic ablation, not production transformer evidence.

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

GitHub Actions runs the full unit suite on Python `3.11` and `3.12` without hardware-provider credentials:

```bash
pytest --cov=qrope --cov-report=term-missing --cov-report=xml
python scripts/check_readme_verifier_output.py
```

Coverage XML is uploaded as a workflow artifact. Optional provider SDK tests use mocks or skip paths when optional packages such as Perceval are not installed.

## Publication use

If you cite or discuss this work, use the bounded posture:

> PhaseWrap-RoPE is a phase-wrap positional scoring rule with two-qubit hardware readout and repository-backed deterministic evidence packets, including bounded Stage 4 real-hardware validation records.

Do not restate the result as a proof of broad quantum transformer superiority.

## Research Roadmap

The current release is ready for bounded repository/preprint publication. The next research work should be evidence-producing rather than claim-broadening:

| Priority | Work item | Purpose |
| --- | --- | --- |
| 1 | Attention-scoring benchmark against classical and positional baselines | Complete for the current synthetic task; simple exposed-feature baselines recover the label exactly. |
| 2 | DOI/preprint release hygiene | Make the current evidence package citable before further experiments change the repository state. |
| 3 | Toy downstream attention benchmark | Complete for a fixed synthetic packet; PhaseWrap-RoPE gives the best score calibration, but broader claims require harder tasks and more seeds. |
| 4 | Four-layer toy transformer ablation | Complete for a fixed synthetic length-extrapolation packet; PhaseWrap-RoPE improves target ranking, but broader claims require harder tasks and more seeds. |
| 5 | Independent hardware replication | Add new packet/date/backend records, confidence or bootstrap intervals for MAE/rank correlations, and IonQ or Quandela only when provider availability, credentials, and budget support real artifacts. |
| 6 | Larger or error-aware witnesses | Explore larger qubit witnesses or mitigation analysis after downstream and replication evidence justify the added complexity. |

The mod-8/mod-12 choice is a fixed first-release design: two wrapped residual bases with one-step thresholds at `pi/4` and `pi/6`, producing a cross-band product signal. Other period pairs are future ablation targets, not current evidence.

The CX variant was chosen as the smallest entangling extension of the product-state witness: it preserves the two `RY` margin encodings, adds one `CX(q0 -> q1)`, and reads a target-qubit parity/product signal without changing the packet discipline. The full Stage 4 packet generation pipeline is already present in `src/qrope/automated_stage_gates.py` and exposed through the Stage 4 runner/verifier scripts; future work is to separate that path into a cleaner researcher-facing API without changing the recorded packets.

## Licensing and patent notice

Software in this repository is released under `AGPL-3.0-only`. Patent and IP-status boundaries are documented in [PATENTS.md](PATENTS.md) and [Patent status note](docs/publication/patent-status-note-v1.md).
