# QRoPE manuscript-to-provisional support audit v1

Status: `PASS_WITH_BOUNDARIES`

Audit date: `2026-05-18`

Provisional application: `64/068,121`

Filing posture: patent-pending; bounded publication permitted if the public paper and repository keep the claim frame below.

## Publication strategy

Publish QRoPE as an open-source Quantyra research repository and bounded evidence paper. The correct posture is:

> patent-pending, reproducible, evidence-disciplined, and limited to the filed method plus repository-backed validation packets.

The incorrect posture is:

> QRoPE proves broad quantum advantage or quantum transformer superiority.

## Support map

| Public statement | Provisional support | Repository support | Publication decision |
| --- | --- | --- | --- |
| QRoPE uses phase-wrap positional residuals and mod-8/mod-12 signed margins. | Specification paragraphs `[0009]-[0015]`. | `docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md` | Allowed. |
| SQR is the product of the mod-8 and mod-12 signed margins. | Specification paragraphs `[0010]-[0015]`. | `docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md` | Allowed. |
| A small circuit can encode or witness the QRoPE score through a ZZ-style expectation statistic. | Specification paragraphs `[0021]-[0022]` and `[0079]-[0085]`. | Stage 4 hardware-validation materials. | Allowed when described as a bounded witness, not as a full transformer. |
| Validation should use frozen packets, fixed rows/shots, raw counts, backend metadata, and offline recomputation. | Specification paragraphs `[0023]-[0024]` and `[0093]-[0100]`. | Automated terminal packet and Stage 4 packet records. | Allowed and preferred. |
| The repo contains a Stage 4 real-noisy-hardware positive result. | Filed specification supports the validation method and result classes. | `docs/research/q-rope-stage4-real-hardware-validation-result-v1.md` | Allowed only as a packet/backend/date/calibration-specific result. |
| The IBM backend name and job id are evidence metadata. | Filed specification supports backend metadata and raw-count records, but does not need a specific backend/job id as an invention claim. | Stage 4 result record. | Allowed in an evidence appendix if desired; not needed in abstract-level claims. |
| QRoPE proves broad quantum advantage. | Not supported. | Not supported. | Prohibited. |
| QRoPE has demonstrated transformer-scale superiority. | Not supported. | Not supported. | Prohibited. |
| QRoPE has demonstrated general cross-backend robustness. | Not supported by one bounded hardware packet. | Not supported. | Prohibited unless later replicated across backends. |

## Manuscript claim frame

The manuscript may say:

- QRoPE defines a phase-wrap positional scoring method.
- The method is patent-pending under U.S. provisional application `64/068,121`.
- The repo provides deterministic validation packets and offline recomputation artifacts.
- The Stage 4 result is a bounded real-hardware validation for the recorded packet/backend/date/calibration context.
- The evidence supports further research and replication.

The manuscript must not say:

- QRoPE is a proven replacement for RoPE in production transformers.
- QRoPE proves quantum advantage.
- QRoPE establishes cross-backend hardware superiority.
- The Stage 4 packet generalizes beyond its frozen packet/backend/date/calibration context.

## Release verdict

The repository is suitable for public open-source release after these artifacts are present:

- `LICENSE` with `AGPL-3.0-only`;
- `PATENTS.md` with provisional application `64/068,121`;
- public-facing `README.md` with the bounded claim frame;
- `CITATION.cff`;
- contributor, security, and conduct files;
- this support audit.

The publication should proceed as a bounded evidence release, not as an unrestricted superiority claim.
