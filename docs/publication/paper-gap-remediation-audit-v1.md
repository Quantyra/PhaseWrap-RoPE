# PhaseWrap-RoPE paper gap remediation audit v1

Status: `PASS_LOCAL_REMEDIATION`

Audit date: `2026-05-18`

Objective: address the gaps discovered in the paper audit.

## Prompt-to-artifact checklist

| Gap from review | Artifact evidence | Status |
| --- | --- | --- |
| Missing formal citations and bibliography. | `docs/publication/qrope-paper-v1.md` References section; `docs/publication/references.bib`. | Addressed. |
| Method section too thin. | `docs/publication/qrope-paper-v1.md` Method section with formulas and Algorithm 1. | Addressed. |
| Hardware result under-contextualized. | `docs/publication/qrope-paper-v1.md` Hardware validation result section includes provider, backend, job id/task ids, timestamps, calibration metadata where available, packet id, rows, shots, metrics, and outcome. The active provider-aware sweep now summarizes committed IBM Fez product-state, Amazon Braket/Rigetti product-state, IBM Fez CX, and Amazon Braket CX evidence on Rigetti Cepheus, IQM Garnet, and IQM Emerald while deferring additional IBM lanes and excluding unavailable IonQ targets. | Addressed. |
| Figures lacked numbered captions/source notes. | Figures now have Figure 1, Figure 2, and Figure 3 captions; Figure 3 names its source data file and comparison scope. | Addressed. |
| Repetitive boundary language. | Claim boundary is consolidated in Related work and claim boundary; Limitations section is shorter. | Addressed. |
| Repository memo style. | Reproducibility section now names verifier entry point, default inputs, and default output. | Addressed. |
| Hallucinated citation risk. | References use primary arXiv pages and IBM Quantum documentation URLs with access date. | Addressed. |
| External review flagged provisional-number/date credibility. | `docs/publication/patent-status-note-v1.md`, `PATENTS.md`, `README.md`, and paper now use conservative acknowledgement-receipt wording and note final Filing Receipt pending. | Addressed. |
| External review flagged product-state witness overclaim. | Paper and README now distinguish the product-state angle-encoding/readout witness from the separate entangling CX witness family, and both remain bounded to recorded packet/backend/date/calibration-specific evidence. | Addressed. |
| External review flagged recomputation vs replication. | Paper now distinguishes saved-count recomputation from independent replication. The publication docs also record the bounded IBM/Braket evidence posture and the Amazon Braket/IonQ unavailable/not-run status. | Addressed. |

## Remaining non-blocking work

- Convert Markdown paper to venue-specific format after selecting a venue.
- Add DOI or release tag after final public release tagging.
- Add cross-backend replication only after new evidence exists.
