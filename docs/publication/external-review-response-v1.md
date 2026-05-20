# External review response v1

Status: `CLAUDE_REVIEW_ACTIONED_INITIAL_PASS`

Date: `2026-05-18`

## High-priority corrections made

| Review issue | Response |
| --- | --- |
| Provisional application number looked inconsistent with USPTO provisional series conventions. | Public wording changed to conservative acknowledgement-receipt language. `docs/publication/patent-status-note-v1.md` now records that the Electronic Acknowledgement Receipt lists `64/068,121`, while USPTO MPEP 503 lists provisional series codes as `60/` through `63/`; final Filing Receipt review remains pending. |
| Filing date appeared future-dated. | The current repo date is `2026-05-18`; the receipt date is not future-dated as of this response. Public wording now uses the concrete receipt timestamp. |
| Hardware run occurred before the USPTO receipt. | `docs/publication/patent-status-note-v1.md` now separates the internal hardware execution timeline, USPTO receipt timeline, and later public release timeline. |
| Product-state witness was overframed as quantum evidence. | README and paper now state that the product-state Stage 4 circuit is an angle-encoding/readout witness with no entangling gate, and that it is not evidence of entanglement, quantum speedup, or nonclassical interference. The repository now separately reports an entangling CX witness family, still with bounded packet/backend/date/calibration-specific claims only. |
| Thresholds `cos(pi/4)` and `cos(pi/6)` lacked motivation. | Paper now explains that these are one-step angular thresholds for periods 8 and 12. |
| Control condition was undefined. | Paper now defines the additive single-band readout control and the cross-band product witness. |
| Reproducibility was really recomputation. | Paper now distinguishes saved-count recomputation from independent replication. |
| README lacked quickstart. | README now includes a no-credential local method check, verifier command, expected verifier output, and reviewer path. |
| Paper referenced verifier/evidence artifacts that were not staged for public review. | The public evidence bundle is prepared for publication: `src/qrope/automated_stage_gates.py`, `scripts/verify_stage4_hardware_packet.py`, `scripts/verify_stage4_hardware_sweep.py`, Stage 4 JSON packet files under `logs/automated_stage_gates/stage4_hardware_packet/`, and a provider-aware sweep manifest that passes for active IBM Fez product-state, Amazon Braket/Rigetti product-state, IBM Fez CX, and Amazon Braket CX records on Rigetti Cepheus, IQM Garnet, and IQM Emerald while listing additional IBM targets as deferred and IonQ as an excluded unavailable target. |
| Default packet and sweep evidence paths could be confused. | `stage4_hardware_packet/` remains the default single-packet reviewer path, and the same IBM Fez 2026-05-17 pass is also preserved under `stage4_hardware_packet_ibm_fez_20260517_pass/`; the sweep manifest points to the immutable named directory. |
| CI did not run the full unit suite or check README verifier drift. | CI now runs the full unit suite, skips optional Perceval-dependent tests when Perceval is unavailable, and checks the README expected single-packet verifier summary against the actual verifier output. |
| Stronger classical and attention baselines were requested. | Stage 5 now includes mod-24 lookup, direct `m8`/`m12`/`m8*m12`, shallow regression-tree, RoPE-style, sinusoidal, and ALiBI-style attention-scoring baselines. The result is reported as a bounded baseline closure: the current synthetic label is exactly recoverable by mod-24 lookup and direct product features. |
| A non-tautological downstream benchmark was needed after Stage 5. | Stage 6 now mixes token/content compatibility with phase-wrap positional signal. Mod-24 lookup and direct phase features are no longer exact, and `phasewrap_rope_attention` has the lowest MAE on the fixed toy packet. Because the PhaseWrap model sees `phase_label` directly, the paper frames this as an oracle phase-feature sanity check. |
| A compact toy transformer ablation was requested. | Stage 7 now swaps the PhaseWrap positional term into a four-layer attention-only toy transformer on a synthetic length-extrapolation retrieval packet. `phasewrap_rope_4layer` has the best argmax retrieval ranking on that fixed packet, while `rope_4layer` is better on target-probability calibration. |
| A RoPE-facing benchmark lane was needed to justify keeping the name. | Stage 8 adds a local phase-cued Needle-style retrieval packet with five seeds, bootstrap intervals, RoPE-like/ALiBI-like/sinusoidal/no-position baselines, and a period-pair ablation. It supports continued RoPE-facing research, not a production replacement claim. |
| Reviewers asked why the CX variant was chosen and whether packet generation would be reusable. | README, quickstart, and paper now state that CX is the smallest entangling extension of the product-state witness and that the current packet generation pipeline is open in `src/qrope/automated_stage_gates.py`, with cleaner researcher-facing API packaging deferred. |
| A one-click reviewer verification path was requested. | README now includes a Colab badge pointing to `docs/notebooks/phasewrap_rope_verify.ipynb`, a one-cell notebook that runs local verifier scripts and prints JSON summaries. |
| AGENTS.md rendered a literal `\r\n`. | Fixed. |

## Not yet done

- Mint a release DOI/archive after final public release tagging.
- Move internal process/governance materials into a cleaner public structure.
- Wait for CI to complete on GitHub and respond to any failures.
- Post an arXiv/OSF preprint and mint a Zenodo DOI.
- Add harder multi-seed downstream benchmarks. Stage 6, Stage 7, and Stage 8 now provide bounded synthetic packets, but broader downstream claims require standard retrieval tasks or small trained transformer experiments.
- Add repeated hardware evidence across dates/calibration windows. The current sweep verifier now maintains deterministic row-bootstrap and shot-resampling intervals for MAE/rank correlations from committed artifacts, but those intervals are not substitutes for independent reruns.

These remaining items require new execution, repo restructuring, or external publication steps and should not be represented as complete.
