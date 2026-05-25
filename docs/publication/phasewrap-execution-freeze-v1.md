# PhaseWrap Execution Freeze v1

Status: `PHASEWRAP_POSITIVE_EXECUTION_FROZEN`

Date: `2026-05-25`

## Decision

The fixed-period PhaseWrap positive-replacement research line is frozen. The repo may continue as a negative-results, methodology, scoring-API, verifier, and evidence-preservation package.

## Allowed Work

- methodology paper preparation;
- score-theory appendix cleanup;
- evidence-hygiene documentation;
- verifier hardening;
- failed-run retention and artifact hygiene;
- documentation, README, citation, and release-note cleanup;
- externally publishing the negative-results package after the verifier remains green.

## Disallowed Work By Default

- new synthetic stages intended to find a PhaseWrap-positive replacement result;
- new hardware spending intended to strengthen a model-improvement claim;
- README, paper, or metadata language implying RoPE replacement;
- support-routing or copy-expert repairs presented as positional-method success when `no_position` also solves;
- Stage 219 language that omits probability/calibration degradation;
- patent/IP prominence as scientific credibility.

## Reopen Requirements

Any new PhaseWrap-positive execution must cite one of the reopen gates in `phasewrap-research-program-decision-v1.md` before implementation:

- `Transformer gate`;
- `Hardware gate`;
- `New-method gate`.

The reopen brief must predeclare:

- task family;
- baselines and controls, including `no_position`;
- metrics, including rank, probability, and calibration;
- confidence-interval method;
- failed-run retention rules;
- claim boundary and explicit non-claims.

## Publication Boundary

Until a reopen gate is satisfied, public materials should summarize PhaseWrap as:

> a negative-results and methodology package showing that assistance pipelines can repair retrieval tasks without isolating the positional mechanism under test.

They should not summarize it as a RoPE replacement, quantum advantage, production transformer improvement, or broad hardware-robustness result.
