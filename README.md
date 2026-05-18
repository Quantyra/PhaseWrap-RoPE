# QRoPE

QRoPE is Quantyra's patent-pending research repository for Quantum Rotary Positional Encoding: a bounded, reproducible evidence lane for phase-wrapped positional scoring and small-circuit hardware validation.

This repository is intended for open scientific review of the QRoPE method, validation scripts, evidence packets, and publication materials. It is not a claim of general quantum advantage, full transformer-scale superiority, or cross-backend hardware robustness.

## Status

- `Patent-pending`: U.S. provisional patent application `64/068,121`, filed `2026-05-18`.
- `License`: GNU Affero General Public License v3.0 only (`AGPL-3.0-only`).
- `Publication posture`: bounded, reproducible, evidence-disciplined.
- `Current evidence posture`: Stage 4 real-noisy-hardware positive result for one frozen packet/backend/date/calibration context.

## Claim boundary

The public claim frame for this repository is:

- QRoPE defines phase-wrap residual features using mod-8 and mod-12 structure.
- The SQR score uses the product of the mod-8 and mod-12 signed margins.
- The evidence lane includes deterministic frozen-packet validation, raw counts, backend metadata, and offline recomputation.
- The Stage 4 result is a bounded real-hardware validation for the frozen packet reported in this repository.

The public claim frame excludes:

- broad quantum advantage;
- full transformer-scale validation;
- general cross-backend superiority;
- claims that QRoPE improves production language-model quality;
- claims that one backend/date/calibration result generalizes without additional evidence.

## Key documents

- [Manuscript-to-provisional support audit](docs/publication/manuscript-to-provisional-support-audit-v1.md)
- [Open-source release checklist](docs/publication/open-source-release-checklist-v1.md)
- [Patent notice](PATENTS.md)
- [Stage 4 real-hardware validation result](docs/research/q-rope-stage4-real-hardware-validation-result-v1.md)
- [Automated terminal human-review packet](docs/evidence/review-packets/qrope-automated-terminal-v1/qrope-terminal-human-review-packet-v1.md)
- [Phase-wrap algorithm note](docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md)

## Install

```bash
python -m pip install -e .
```

## Publication use

If you cite or discuss this work, use the bounded posture:

> QRoPE is a patent-pending phase-wrap positional-encoding and validation method with repository-backed deterministic evidence packets, including a bounded Stage 4 real-hardware validation result.

Do not restate the result as a proof of broad quantum transformer superiority.

## Licensing and patent notice

Software in this repository is released under `AGPL-3.0-only`. Patent-pending status and patent-license boundaries are documented in [PATENTS.md](PATENTS.md).
