# External review response v1

Status: `CLAUDE_REVIEW_ACTIONED_INITIAL_PASS`

Date: `2026-05-18`

## High-priority corrections made

| Review issue | Response |
| --- | --- |
| Provisional application number looked inconsistent with USPTO provisional series conventions. | Public wording changed to conservative acknowledgement-receipt language. `docs/publication/patent-status-note-v1.md` now records that the Electronic Acknowledgement Receipt lists `64/068,121`, while USPTO MPEP 503 lists provisional series codes as `60/` through `63/`; final Filing Receipt review remains pending. |
| Filing date appeared future-dated. | The current repo date is `2026-05-18`; the receipt date is not future-dated as of this response. Public wording now uses the concrete receipt timestamp. |
| Hardware run occurred before the USPTO receipt. | `docs/publication/patent-status-note-v1.md` now separates the internal hardware execution timeline, USPTO receipt timeline, and later public release timeline. |
| Product-state witness was overframed as quantum evidence. | README and paper now state that the current Stage 4 circuit is a product-state angle-encoding/readout witness with no entangling gate, and that it is not evidence of entanglement, quantum speedup, or nonclassical interference. |
| Thresholds `cos(pi/4)` and `cos(pi/6)` lacked motivation. | Paper now explains that these are one-step angular thresholds for periods 8 and 12. |
| Control condition was undefined. | Paper now defines the additive single-band readout control and the cross-band product witness. |
| Reproducibility was really recomputation. | Paper now distinguishes saved-count recomputation from independent replication. |
| README lacked quickstart. | README now includes a no-credential local method check, verifier command, expected verifier output, and reviewer path. |
| Paper referenced verifier/evidence artifacts that were not staged for public review. | The public evidence bundle is prepared for publication: `src/qrope/automated_stage_gates.py`, `scripts/verify_stage4_hardware_packet.py`, and Stage 4 JSON packet files under `logs/automated_stage_gates/stage4_hardware_packet/`. |
| AGENTS.md rendered a literal `\r\n`. | Fixed. |

## Not yet done

- Execute and report the implemented entangling-gate witness variant on hardware.
- Run cross-backend and cross-date replications.
- Move internal process/governance materials into a cleaner public structure.
- Wait for CI to complete on GitHub and respond to any failures.
- Post an arXiv/OSF preprint and mint a Zenodo DOI.

These remaining items require new execution, repo restructuring, or external publication steps and should not be represented as complete.
