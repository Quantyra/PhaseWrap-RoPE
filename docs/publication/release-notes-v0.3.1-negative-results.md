# Release Notes: v0.3.1-negative-results

Status: `GITHUB_RELEASE_PUBLISHED_REPO_PUBLIC`

Date: `2026-05-25`

## Release Title

`PhaseWrap v0.3.1-negative-results`

## Summary

This release is the Zenodo-targeted public archive release for PhaseWrap's negative-results and methodology package. The positive RoPE-replacement line is closed. The repository preserves the evidence for that decision: score-theory limits, retrieval-benchmark failure modes, method-nonspecific assistance-pipeline repairs, bounded two-qubit hardware-readout audits, and reproducibility infrastructure.

## Main Artifacts

- `docs/publication/phasewrap-research-program-decision-v1.md`
- `docs/publication/phasewrap-methodology-paper-v1.md`
- `docs/publication/phasewrap-execution-freeze-v1.md`
- `docs/publication/phasewrap-decision-execution-audit-v1.md`
- `docs/publication/negative-results-publication-roadmap-v1.md`
- `docs/publication/quickstart-results-summary-v1.md`
- `scripts/verify_publication_package.py`

## Main Conclusion

Assistance pipelines can repair retrieval tasks without isolating the positional mechanism under test. In the PhaseWrap evidence trail, content-key redesigns, support recovery, hard/soft support-routed selectors, structural copy experts, and auxiliary heads repeatedly repaired retrieval without proving PhaseWrap-specific positional contribution. Several repairs also solved the same task for `no_position`.

## What This Release Supports

- Negative-results publication of the fixed-period PhaseWrap research line.
- A methodology warning for positional-encoding retrieval benchmarks.
- Stage 11 score-theory limits: period `24`, `10` distinct residue scores, alias growth, and Fourier support `[1, 2, 3, 5]`.
- Stage 80/81 support-routing warning: phase-cued retrieval is repaired for every tested method, including `no_position`.
- Stage 219 ranking parity in bounded retrieval bridges, with probability/calibration degradation.
- Stage 216-218 bounded hardware-readout audit evidence.
- Reproducible verifier and evidence-hygiene infrastructure.

## What This Release Does Not Support

- RoPE replacement.
- Production transformer superiority.
- Quantum advantage.
- Entanglement-based advantage.
- Broad cross-backend hardware robustness.
- Transformer-scale model improvement from two-qubit readout records.
- PhaseWrap-specific support-routing success when `no_position` also solves.
- Patent/IP status as scientific evidence.

## Verification

Before publishing this release, run:

```bash
python scripts/verify_publication_package.py
python -m pytest tests/test_publication_package_verifier.py tests/test_stage219_rope_substitution_gate.py
python scripts/check_readme_verifier_output.py
```

Expected outcomes:

- `PUBLICATION_PACKAGE_VERIFY_PASS`
- targeted pytest suite passes;
- README verifier output check passes;
- no receipt-specific identifiers or confirmation numbers appear in public-facing docs.

## Publication Boundary

This release has been published as a GitHub release in the public repository for Zenodo archival:

`https://github.com/Quantyra/PhaseWrap/releases/tag/v0.3.1-negative-results`

Do not post arXiv, create an OSF project, publish a blog post, or make a broader public announcement until the repository owner explicitly approves that external-publication step.
