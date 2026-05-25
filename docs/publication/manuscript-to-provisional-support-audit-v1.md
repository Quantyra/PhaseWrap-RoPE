# PhaseWrap-RoPE manuscript-to-provisional support audit v1

Status: `PASS_WITH_BOUNDARIES`

Audit date: `2026-05-23`

USPTO provisional applications: `64/068,121` and `64/073,899`

Filing posture: patent pending; bounded publication permitted if the public paper and repository keep the claim frame below.

## Publication strategy

Publish PhaseWrap-RoPE as an open-source Quantyra research repository and bounded evidence paper. The correct posture is:

> patent pending, reproducible, evidence-disciplined, and limited to the submitted method plus repository-backed validation packets.

The incorrect posture is:

> PhaseWrap-RoPE proves broad quantum advantage or quantum transformer superiority.

## Support map

| Public statement | Provisional support | Repository support | Publication decision |
| --- | --- | --- | --- |
| PhaseWrap-RoPE uses phase-wrap positional residuals and mod-8/mod-12 signed margins. | Specification paragraphs `[0009]-[0015]`. | `docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md` | Allowed. |
| The cross-band score is the product of the mod-8 and mod-12 signed margins. | Specification paragraphs `[0010]-[0015]`. | `docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md` | Allowed. |
| A small circuit can encode or witness the PhaseWrap-RoPE score through a ZZ-style expectation statistic. | Specification paragraphs `[0021]-[0022]` and `[0079]-[0085]`. | Stage 4 hardware-validation materials and Stage216-218 full IBM Fez replacement artifacts. | Allowed when described as a bounded witness, not as a full transformer. |
| Validation should use frozen packets, fixed rows/shots, raw counts, backend metadata, and offline recomputation. | Specification paragraphs `[0023]-[0024]` and `[0093]-[0100]`. | Automated terminal packet, Stage 4 packet records, and Stage216-218 merged count/calibration/metric records. | Allowed and preferred. |
| The repo contains bounded real-noisy-hardware positive results, including the full IBM Fez replacement comparison. | Filed specification supports the validation method and result classes. | `docs/research/q-rope-stage4-real-hardware-validation-result-v1.md`; `logs/automated_stage_gates/stage216_full_replacement_merged_result_counts_250usd/`; `logs/automated_stage_gates/stage217_full_replacement_calibration_validation_250usd/`; `logs/automated_stage_gates/stage218_full_replacement_hardware_metric_interpreter_250usd/` | Allowed only as packet/backend/date/calibration-specific results. |
| The IBM backend name and job id are evidence metadata. | Filed specification supports backend metadata and raw-count records, but does not need a specific backend/job id as an invention claim. | Stage 4 result record. | Allowed in an evidence appendix if desired; not needed in abstract-level claims. |
| PhaseWrap-RoPE proves broad quantum advantage. | Not supported. | Not supported. | Prohibited. |
| PhaseWrap-RoPE has demonstrated transformer-scale superiority. | Not supported. | Not supported. | Prohibited. |
| PhaseWrap-RoPE has demonstrated general cross-backend robustness. | Not supported by bounded IBM Fez and selected Braket/Rigetti packet evidence alone. | Not supported. | Prohibited unless later replicated across broader backends and dates. |

## Manuscript claim frame

The manuscript may say:

- PhaseWrap-RoPE defines a phase-wrap positional scoring method.
- The method is patent pending under USPTO provisional applications `64/068,121` and `64/073,899`.
- The repo provides deterministic validation packets and offline recomputation artifacts.
- The Stage 4 and full IBM Fez replacement results are bounded real-hardware validations for the recorded packet/backend/date/calibration contexts.
- The evidence supports further research and replication.

The manuscript must not say:

- PhaseWrap-RoPE is a proven replacement for RoPE in production transformers.
- PhaseWrap-RoPE proves quantum advantage.
- PhaseWrap-RoPE establishes cross-backend hardware superiority.
- The Stage 4 packet generalizes beyond its frozen packet/backend/date/calibration context.

## Release verdict

The repository is suitable for public open-source release after these artifacts are present:

- `LICENSE` with `AGPL-3.0-only`;
- `PATENTS.md` with USPTO provisional applications `64/068,121` and `64/073,899`;
- public-facing `README.md` with the bounded claim frame;
- `CITATION.cff`;
- contributor, security, and conduct files;
- this support audit.

The publication should proceed as a bounded evidence release, not as an unrestricted superiority claim.
