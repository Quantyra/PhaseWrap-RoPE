# External review response v1

Status: `CLAUDE_REVIEW_ACTIONED_REPO_SIDE_PASS`

Date: `2026-05-18`

## High-priority corrections made

| Review issue | Response |
| --- | --- |
| Patent language was too detailed. | Public wording now states the basic patent-pending status and U.S. provisional application number. |
| Product-state witness was overframed as quantum evidence. | README and paper now state that the current Stage 4 circuit is a product-state angle-encoding/readout witness with no entangling gate, and that it is not evidence of entanglement, quantum speedup, or nonclassical interference. |
| Thresholds `cos(pi/4)` and `cos(pi/6)` lacked motivation. | Paper now explains that these are one-step angular thresholds for periods 8 and 12. |
| Control condition was undefined. | Paper now defines the additive single-band readout control and the cross-band product witness. |
| Reproducibility was really recomputation. | Paper now distinguishes saved-count recomputation from independent replication. |
| README lacked quickstart. | README now includes a no-credential local method check, verifier command, expected verifier output, and reviewer path. |
| Paper referenced verifier/evidence artifacts that were not staged for public review. | The public evidence bundle is prepared for publication: `src/qrope/automated_stage_gates.py`, `scripts/verify_stage4_hardware_packet.py`, and Stage 4 JSON packet files under `logs/automated_stage_gates/stage4_hardware_packet/`. |
| AGENTS.md rendered a literal `\r\n`. | Fixed. |

## Remaining hardware evidence blockers

- The entangling CX witness is implemented and unit-tested, but no credentialled hardware CX run has been completed.
- Cross-backend and cross-date replication lanes are defined and logged, but remain blocked pending credentials, backend selection, completed raw counts, metadata, and verifier output.

## Additional cleanup completed

- Process-heavy `epics/` and `stories/` archives moved under `docs/governance/`.
- A replication ledger was added at `docs/publication/replication-ledger-v1.md` with machine-readable state in `logs/automated_stage_gates/replication_lanes/replication-ledger.json`.
- Publication charts were refreshed and a replication-status chart was added.
- arXiv/OSF/Zenodo release is not required for the current repository posture and is not treated as a blocker.

The remaining hardware items require credentialled execution and should not be represented as complete until new packet evidence exists.
