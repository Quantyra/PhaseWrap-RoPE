# Reproducible Review Environment

Status: public review environment path.

The base package is intentionally separated from live hardware-provider dependencies. Reviewers can verify the saved evidence packets and inspect the scoring API without IBM, Braket, or Quandela credentials.

## Python

Recommended Python: `3.11` or newer.

## Core Install

```bash
python -m pip install -e .
```

This installs the package and base dependencies only. It is enough for `qrope.scoring` and most saved-artifact inspection.

## Reviewer Install

```bash
python -m pip install -r requirements-review.txt
python -m pip install -e .
```

`requirements-review.txt` pins the dependency versions used for the public review verifier path in this workspace. It avoids live provider SDKs so a reviewer does not need cloud credentials or hardware-driver setup.

Run the publication package verifier:

```bash
python scripts/verify_publication_package.py
```

Run the focused public-review tests:

```bash
python -m pytest tests/test_scoring_api.py tests/test_publication_package_verifier.py tests/test_publication_paper_export.py tests/test_stage216_218_full_replacement_interpretation.py
```

## Optional Provider Installs

Install provider stacks only for live hardware work:

```bash
python -m pip install -e ".[ibm]"
python -m pip install -e ".[braket]"
python -m pip install -e ".[hardware]"
```

The publication verifier and saved-result interpretation do not require provider credentials.
