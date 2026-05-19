# QRoPE paper gap remediation audit v1

Status: `PASS_LOCAL_REMEDIATION`

Audit date: `2026-05-18`

Objective: address the gaps discovered in the paper audit.

## Prompt-to-artifact checklist

| Gap from review | Artifact evidence | Status |
| --- | --- | --- |
| Missing formal citations and bibliography. | `docs/publication/qrope-paper-v1.md` References section; `docs/publication/references.bib`. | Addressed. |
| Method section too thin. | `docs/publication/qrope-paper-v1.md` Method section with formulas and Algorithm 1. | Addressed. |
| Hardware result under-contextualized. | `docs/publication/qrope-paper-v1.md` Hardware validation result section includes provider, backend, job id, timestamps, calibration metadata, qubit count, packet id, rows, shots, metrics, and outcome. The completed hardware comparison figure and report now summarize both witness families. | Addressed. |
| Figures lacked numbered captions/source notes. | Figures now have Figure 1, Figure 2, and Figure 3 captions; Figure 3 names its source data file and comparison scope. | Addressed. |
| Repetitive boundary language. | Claim boundary is consolidated in Related work and claim boundary; Limitations section is shorter. | Addressed. |
| Repository memo style. | Reproducibility section now names verifier entry point, default inputs, and default output. | Addressed. |
| Hallucinated citation risk. | References use primary arXiv pages and IBM Quantum documentation URLs with access date. | Addressed. |
| External review flagged provisional-number/date credibility. | `docs/publication/patent-status-note-v1.md`, `PATENTS.md`, `README.md`, and paper now use conservative acknowledgement-receipt wording and note final Filing Receipt pending. | Addressed. |
| External review flagged product-state witness overclaim. | Paper and README now state the Stage 4 circuit is a product-state angle-encoding/readout witness with no entangling gate. | Addressed. |
| External review flagged recomputation vs replication. | Paper now distinguishes saved-count recomputation from independent replication. The publication docs also record the completed cross-backend comparison sweep. | Addressed. |

## Remaining non-blocking work

- Convert Markdown paper to venue-specific format after selecting a venue.
- Add DOI or release tag after final public release tagging.
- Add cross-backend replication only after new evidence exists.
