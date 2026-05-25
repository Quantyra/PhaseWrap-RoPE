# External review response v1

Status: `HISTORICAL_REVIEW_RESPONSE_NEGATIVE_RESULTS_REFRAME`

Date: `2026-05-23`

Current note: the standalone replacement paper draft referenced below has been withdrawn from the current public branch. The repository is being reframed for negative-results publication: the positive replacement line is closed, while the evidence package, quickstart summary, verifier scripts, and raw artifacts remain the reviewer base.

## High-priority corrections made

| Review issue | Response |
| --- | --- |
| Provisional application number looked inconsistent with USPTO provisional series conventions. | The repo retains a factual low-prominence patent status note, while README/release front matter no longer uses patent status as a credibility signal. Receipt-specific identifiers are retained only in internal IP records. |
| Filing date appeared future-dated. | The current repo date is `2026-05-18`; the receipt date is not future-dated as of this response. Public wording now uses the concrete receipt timestamp. |
| Hardware run occurred before the USPTO receipt. | `docs/publication/patent-status-note-v1.md` now separates the internal hardware execution timeline, USPTO receipt timeline, and later public release timeline. |
| Product-state witness was overframed as quantum evidence. | README and public evidence notes state that the product-state Stage 4 circuit is an angle-encoding/readout witness with no entangling gate, and that it is not evidence of entanglement, quantum speedup, or nonclassical interference. The repository also reports an entangling CX witness family, still with bounded packet/backend/date/calibration-specific claims only. |
| Thresholds `cos(pi/4)` and `cos(pi/6)` lacked motivation. | The evidence package explains that these are one-step angular thresholds for periods 8 and 12. |
| Control condition was undefined. | The evidence package defines the additive single-band readout control and the cross-band product witness. |
| Reproducibility was really recomputation. | The public review path distinguishes saved-count recomputation from independent replication. |
| README lacked quickstart. | README now includes a no-credential local method check, verifier command, expected verifier output, and reviewer path. |
| Paper referenced verifier/evidence artifacts that were not staged for public review. | The public evidence bundle is prepared for review: `src/qrope/automated_stage_gates.py`, `scripts/verify_stage4_hardware_packet.py`, `scripts/verify_stage4_hardware_sweep.py`, Stage 4 JSON packet files under `logs/automated_stage_gates/stage4_hardware_packet/`, and a provider-aware sweep manifest that passes for active IBM Fez product-state, Amazon Braket/Rigetti product-state, IBM Fez CX, and Amazon Braket CX records on Rigetti Cepheus, IQM Garnet, and IQM Emerald while listing additional IBM targets as deferred and IonQ as an excluded unavailable target. |
| Default packet and sweep evidence paths could be confused. | `stage4_hardware_packet/` remains the default single-packet reviewer path, and the same IBM Fez 2026-05-17 pass is also preserved under `stage4_hardware_packet_ibm_fez_20260517_pass/`; the sweep manifest points to the immutable named directory. |
| CI was not aligned to the public reviewer path or README verifier drift. | CI now runs the bounded publication-review suite on Python 3.11/3.12, skips optional Perceval-dependent tests when Perceval is unavailable, and checks the README expected single-packet verifier summary against the actual verifier output. |
| Stronger classical and attention baselines were requested. | Stage 5 now includes mod-24 lookup, direct `m8`/`m12`/`m8*m12`, shallow regression-tree, RoPE-style, sinusoidal, and ALiBI-style attention-scoring baselines. The result is reported as a bounded baseline closure: the current synthetic label is exactly recoverable by mod-24 lookup and direct product features. |
| A non-tautological downstream benchmark was needed after Stage 5. | Stage 6 mixes token/content compatibility with phase-wrap positional signal. Mod-24 lookup and direct phase features are no longer exact, and `phasewrap_rope_attention` has the lowest MAE on the fixed toy packet. Because the PhaseWrap model sees `phase_label` directly, the repository frames this as an oracle phase-feature sanity check. |
| A compact toy transformer ablation was requested. | Stage 7 now swaps the PhaseWrap positional term into a four-layer attention-only toy transformer on a synthetic length-extrapolation retrieval packet. `phasewrap_rope_4layer` has the best argmax retrieval ranking on that fixed packet, while `rope_4layer` is better on target-probability calibration. |
| A RoPE-facing benchmark lane was needed to justify keeping the name. | Stage 8 adds a local phase-cued Needle-style retrieval packet with five seeds, bootstrap intervals, RoPE-like/ALiBI-like/sinusoidal/no-position baselines, and a period-pair ablation. It supports continued RoPE-facing research, not a production replacement claim. |
| Reviewers asked why the CX variant was chosen and whether packet generation would be reusable. | README and quickstart materials state that CX is the smallest entangling extension of the product-state witness and that the current packet generation pipeline is open in `src/qrope/automated_stage_gates.py`, with cleaner researcher-facing API packaging deferred. |
| A one-click reviewer verification path was requested. | README now includes a Colab badge pointing to `docs/notebooks/phasewrap_rope_verify.ipynb`, a one-cell notebook that runs local verifier scripts and prints JSON summaries. |
| A stronger live-hardware replacement packet was needed before spending claims on hardware. | The reduced-scope signal was promoted to the full IBM Fez 4096-shot replacement path. Stages 216-218 merge `21/21` result-count templates, validate unique `q1q0` known-state calibration, and report `FULL_REPLACEMENT_HARDWARE_POSITIVE_PHASEWRAP_ADVANTAGE` across all four seed/template comparison groups. README, quickstart summary, replication ledger, release checklist, and Zenodo/CFF metadata describe this as a bounded two-qubit packet result only. |
| Later review argued that the cumulative downstream record did not support the replacement framing. | Accepted. The current publication roadmap is now negative-results first: the essential paper carries the Stage 67-96 methodology arc, Stage 11 is appendix or optional note material, and Stage 216-218 is retained as hardware-audit infrastructure rather than model-improvement evidence. |
| Later review flagged patent prominence as inconsistent with a credibility-first nonprofit research strategy. | Accepted. Public-facing research materials now keep patent status as a low-prominence legal mention and separate from scientific claims. Patent prosecution and conversion strategy is outside this repository. |
| Filing records clarified that the USPTO records are provisional applications. | Accepted. The repo mentions the filings factually, excludes receipt-specific identifiers and confirmation numbers, and does not treat the filings as evidence of novelty, eligibility, hardware advantage, or model-improvement claims. |
| AGENTS.md rendered a literal `\r\n`. | Fixed. |

## Not yet done

- Prepare the negative-results publication package before any new public release.
- Draft the essential retrieval-benchmark methodology paper carrying the Stage 67-96 arc.
- Decide whether Stage 11 score theory remains an appendix or becomes a short optional standalone note.
- Decide whether the evidence-hygiene material warrants an optional follow-on note after the methodology paper stabilizes.
- Refresh the release DOI/archive only after the negative-results release is cut.
- Move internal process/governance materials into a cleaner public structure.
- Post arXiv/OSF material only under negative-results or methodology framing.

These remaining items require new execution, repo restructuring, or external publication steps and should not be represented as complete.
