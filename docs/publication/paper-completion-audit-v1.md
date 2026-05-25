# PhaseWrap-RoPE paper completion audit v1

Status: `LOCAL_PAPER_PACKAGE_READY_FOR_FINAL_EXPORT`

Audit date: `2026-05-23`

Objective: compile the research work, update the paper, and polish it up to completion without overstating the evidence.

## Completion checklist

| Requirement | Evidence inspected | Verdict |
| --- | --- | --- |
| Main manuscript states the strongest supported result. | `docs/publication/qrope-paper-v1.md` abstract, hardware section, limitations, reproducibility appendix, artifact references, and exported HTML at `docs/publication/qrope-paper-v1.html`. | Complete locally. |
| Full IBM Fez replacement result is included. | Stages 216-218 artifacts under `logs/automated_stage_gates/`; manuscript full replacement section; quickstart summary; replication ledger; `docs/publication/figures/qrope-full-replacement-metrics-v1.png`. | Complete locally. |
| Calibration is represented honestly. | Stage 217 validates unique `q1q0` known-state calibration before Stage 218 metrics; paper and README distinguish this from future-provider calibration packets. | Complete locally. |
| Claims remain bounded. | Manuscript, README, support audit, release checklist, and Zenodo/CFF metadata exclude production transformer superiority, RoPE replacement, quantum advantage, and broad cross-backend robustness. | Complete locally. |
| Reviewer entry points are current. | `README.md`, `docs/publication/quickstart-results-summary-v1.md`, `docs/publication/replication-ledger-v1.md`, and `docs/publication/external-review-response-v1.md`. | Complete locally. |
| Release metadata reflects the current evidence package. | `CITATION.cff` and `.zenodo.json` include the Stage216-218 full IBM Fez replacement comparison and bounded claim language. | Complete locally. |
| Publication figures are regenerated. | `scripts/generate_publication_figures.py` regenerates the publication figures, including the full replacement metrics chart. | Complete locally. |
| Reviewable manuscript export exists without external tooling. | `scripts/export_publication_paper.py` exports `docs/publication/qrope-paper-v1.md` to `docs/publication/qrope-paper-v1.html` using only the Python standard library. | Complete locally. |
| Local paper package has a one-command verification gate. | `scripts/verify_publication_package.py` checks required files, Stage216-218 manifest decisions, public claim strings, forbidden secret/account fragments, Markdown local links, exported HTML local links, and exported HTML images. | Complete locally. |
| External feedback has a public roadmap. | `docs/roadmap.md` tracks framing, core API, dependency hygiene, structure cleanup, standard benchmark, hardware-specific claim testing, and publication follow-up. | Complete locally. |
| Paper-critical code path is regression-tested. | `tests/test_stage216_218_full_replacement_interpretation.py` locks Stage216 merge, Stage217 calibration, and Stage218 positive metric interpretation. | Complete locally. |
| Public local links are not broken in touched release docs and the exported paper. | `scripts/verify_publication_package.py` checks Markdown local links and exported HTML local links/images. | Complete locally. |
| Live credentials and allocated-instance identifiers are not exposed in public docs. | Pattern scan over public docs and touched code/test surfaces does not find the live IBM CRN/account fragments. | Complete locally. |

## Current evidence conclusion

The current paper can claim a bounded two-qubit hardware result: in the full IBM Fez 4096-shot replacement packet, PhaseWrap has lower normalized noise-sensitivity delta than the best matched positional baseline and the matched nonzero null control in all four seed/template comparison groups, after Stage 217 validates the `q1q0` known-state calibration order.

The paper must not claim production transformer superiority, broad RoPE replacement, quantum advantage, or broad cross-backend robustness. Those remain future research questions.

## Verification commands last run

```powershell
python -m py_compile src\qrope\scoring.py src\qrope\ibm_runtime_utils.py src\qrope\env_utils.py src\qrope\stage212_full_replacement_hardware_submission.py src\qrope\stage213_full_replacement_job_status_poll.py src\qrope\stage214_full_replacement_result_collector.py src\qrope\stage215_full_replacement_allocated_instance_resubmission.py src\qrope\stage216_full_replacement_merged_result_counts.py src\qrope\stage217_full_replacement_calibration_validation.py src\qrope\stage218_full_replacement_hardware_metric_interpreter.py scripts\run_stage215_full_replacement_allocated_instance_resubmission.py scripts\run_stage216_full_replacement_merged_result_counts.py scripts\run_stage217_full_replacement_calibration_validation.py scripts\run_stage218_full_replacement_hardware_metric_interpreter.py scripts\generate_publication_figures.py
python scripts\export_publication_paper.py
python scripts\verify_publication_package.py
python -m pytest tests\test_scoring_api.py tests\test_stage11_phasewrap_theory.py tests\test_stage12_ruler_retrieval.py tests\test_publication_package_verifier.py tests\test_publication_paper_export.py tests\test_stage216_218_full_replacement_interpretation.py --basetemp .pytest_tmp
```

Observed verifier result: `PUBLICATION_PACKAGE_VERIFY_PASS`.

Observed test result: `27 passed`.

## Remaining external publication steps

These are not missing research evidence, but they are required before a public venue submission or refreshed public release:

- convert the exported HTML or Markdown manuscript to the selected venue-specific format;
- refresh Zenodo metadata after the `v0.2.43` public release is archived;
- add arXiv/OSF identifiers after submission/acceptance;
- rerun broader independent hardware replications only if the desired claim expands beyond the current bounded result.
