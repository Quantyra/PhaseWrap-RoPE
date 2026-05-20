# PhaseWrap-RoPE

[![CI](https://github.com/Quantyra/PhaseWrap-RoPE/actions/workflows/ci.yml/badge.svg)](https://github.com/Quantyra/PhaseWrap-RoPE/actions/workflows/ci.yml)

PhaseWrap-RoPE is Quantyra's public research repository for phase-wrap positional scoring and bounded hardware validation.

The primary artifact is the paper: [PhaseWrap-RoPE repository paper v1](docs/publication/qrope-paper-v1.md). The code, figures, and evidence packets support that paper.

## Paper

- [PhaseWrap-RoPE repository paper v1](docs/publication/qrope-paper-v1.md)

The paper is the intended review entry point. It defines the method, claim boundary, validation protocol, and hardware evidence record.

## Scope

PhaseWrap-RoPE presents:

- phase-wrap residual features using mod-8 and mod-12 structure;
- a cross-band score computed from the product of the mod-8 and mod-12 signed margins;
- deterministic validation packets with raw counts, backend metadata, and offline recomputation;
- a free local Stage 4 simulation sweep for product-state and entangling-CX witness mechanics;
- a deferred Stage 4 hardware lane that becomes first-class evidence only when backed by tracked raw-count records and offline verification.

The paper does not claim broad quantum advantage, full transformer-scale superiority, or general cross-backend robustness.

## Status

- `Evidence`: free local Stage 4 simulation sweep verified; hardware evidence is deferred until real raw-count artifacts are supplied and verified.
- `Hardware`: no hardware execution is approved at this time.
- `License`: GNU Affero General Public License v3.0 only (`AGPL-3.0-only`).
- `Patent/IP`: patent pending; USPTO provisional application `64/068,121`. Additional receipt identifiers are retained in internal IP records.

## Quickstart

Recommended local environment: Python `3.11+`.

```bash
python -m pip install -e ".[dev]"
```

Run a local method check with no provider credentials:

```bash
python - <<'PY'
from qrope.automated_stage_gates import phase_margins, normalized_phase_label

margins = phase_margins(delta_a=1, delta_b=4)
print(margins)
print("label", normalized_phase_label(margins["score"]))
PY
```

Verify the saved Stage 4 packet arithmetic from the published raw-count evidence:

```bash
python scripts/verify_stage4_hardware_packet.py
```

Verify the Stage 4 multi-platform sweep manifest:

```bash
python scripts/verify_stage4_hardware_sweep.py
```

The sweep verifier is strict: it passes only when real packet, execution/raw-count, evaluation, summary, and metadata artifacts are present for every manifest record. If artifacts are missing, it fails and lists the missing records.

Run and verify the free local Stage 4 simulation sweep:

```bash
python scripts/run_stage4_simulation_sweep.py
python scripts/verify_stage4_simulation_sweep.py
```

The simulation sweep uses no provider credentials and submits no hardware jobs. It validates the packet, circuit-family, raw-count, and verifier mechanics only; it is not hardware evidence.

Offline verification does not submit hardware jobs and has no provider cost. Any future hardware execution or rerun with estimated cost over `$100` requires explicit approval before submission.

Install provider dependencies only when preparing an approved hardware rerun:

```bash
python -m pip install -e ".[ibm]"
```

## Reviewer Path

- Read the paper.
- Inspect the Stage 4 packet files under `logs/automated_stage_gates/stage4_hardware_packet/`.
- Run `python scripts/verify_stage4_hardware_packet.py`.
- Inspect the simulation sweep manifest at `logs/automated_stage_gates/stage4_simulation_sweep/manifest.json`.
- Run `python scripts/verify_stage4_simulation_sweep.py`.
- Inspect the sweep manifest at `logs/automated_stage_gates/stage4_hardware_sweep/manifest.json`.
- Run `python scripts/verify_stage4_hardware_sweep.py`.
- Compare verifier outputs with the corresponding `offline_verification.json` files.

## Appendix: Figures

- [Method schematic](docs/publication/figures/qrope-method-schematic-v1.svg)
- [Validation pipeline](docs/publication/figures/qrope-validation-pipeline-v1.svg)
- [Stage 4 hardware comparison](docs/publication/figures/qrope-stage4-comparison-v1.svg)

## Appendix: Supporting Documents

- [Patent status note](docs/publication/patent-status-note-v1.md)
- [Manuscript-to-provisional support audit](docs/publication/manuscript-to-provisional-support-audit-v1.md)
- [External review response](docs/publication/external-review-response-v1.md)
- [Replication plan](docs/publication/replication-plan-v1.md)
- [External release plan](docs/publication/external-release-plan-v1.md)
- [Open-source release checklist](docs/publication/open-source-release-checklist-v1.md)
- [Stage 4 real-hardware validation result](docs/research/q-rope-stage4-real-hardware-validation-result-v1.md)
- [Stage 4 simulation sweep](docs/research/phasewrap-rope-stage4-simulation-sweep-v1.md)
- [Phase-wrap algorithm note](docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md)

## Appendix: Licensing and Patent Notice

Software in this repository is released under `AGPL-3.0-only`. Patent and IP boundaries are documented in [PATENTS.md](PATENTS.md).
