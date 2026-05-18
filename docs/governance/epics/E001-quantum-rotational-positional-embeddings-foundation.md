# Epic

## Epic ID and title
E001 - Quantum Rotational Positional Embeddings foundation

## Problem statement
Current quantum attention work uses positional methods such as additive sinusoidal signals, fixed Rx positional gates, learned positional states/angles, or no explicit positional encoding in some architectures. A standardized, benchmarked RoPE-like relative-phase mechanism for quantum attention remains underdefined in current practice. We need a rigorous and reproducible QRoPE program that tests whether relative-phase inductive bias improves hybrid quantum attention under NISQ constraints.

## Research questions
- Can a RoPE-like relative phase encoding improve hybrid quantum attention without increasing qubit count or circuit depth beyond practical NISQ limits?
- Under what unitary constraints does positional contribution reduce to relative displacement `(j - i)`?
- What tradeoffs emerge between accuracy gains, noise sensitivity, and hardware cost?
- How does QRoPE compare to additive sinusoidal PE and fixed-Rx PE baselines?

## Goals
- Define and formalize a relative-phase positional method for query-key overlap in hybrid quantum attention.
- Establish a publishable baseline experiment that isolates positional effects.
- Produce a defensible novelty and evidence record before strong external claims.

## Non-goals
- Product claims without validated benchmark evidence.
- Deep-circuit approaches that violate NISQ practicality for baseline experiments.
- Publication drafting before novelty gate and reproducibility gate are satisfied.

## Scope
- Theoretical framing of position unitary `P(i)` and relative-phase behavior.
- Hybrid architecture experiments with QASA-style and/or QMSAN-style baselines.
- Reproducibility-ready benchmark protocol for small-to-medium sequence tasks.

## Success metrics
- Proof sketch or theorem note showing relative-offset dependence conditions.
- Baseline experiment matrix completed with positional ablations.
- Measurable improvement versus no-PE and fixed/additive PE baselines on at least one selected benchmark track.
- Full evidence and novelty log with claim-level source tagging.

## Methods and approach
- Define token encoding `E(x_i)` and position unitary `P(i)` (phase or paired-rotation family).
- Construct `|q_i>` and `|k_j>` with positional unitaries applied inside query-key pathway.
- Estimate overlaps with shallow quantum-compatible similarity methods.
- Run controlled ablations on positional mechanism while holding architecture constant.

## Data sources and tools
- arXiv and peer-reviewed ML venues.
- Open-source benchmark implementations and model cards.
- Quantyra planning templates and process protocols.

## Ethics, privacy, and compliance
- Maintain source transparency and uncertainty labeling.
- Avoid overstated claims from preliminary findings.
- Keep decision logs auditable for internal review.

## Deliverables
- QRoPE concept note and formal method specification.
- Prior-art and novelty scan memo.
- Benchmark protocol and ablation matrix.
- Seed evidence log and checkpoint state.

## Stakeholders
- Chief Science Officer
- VP of Research
- Quantyra research contributors

## Dependencies
- Protocol alignment with `../Quantyra`.
- Access to literature and baseline implementations.

## Risks and mitigations
- Risk: Relative-phase claim does not hold under chosen circuit parameterization.
  Mitigation: prove conditions explicitly and constrain baseline method to valid family.
- Risk: Hardware overhead cancels accuracy gains.
  Mitigation: include gate-count/depth reporting in all benchmark runs.
- Risk: Prior-art overlap weakens novelty.
  Mitigation: complete targeted novelty scan before paper drafting.

## BDD specs (development epics only)
- Gherkin scenarios:
- Not applicable for this research-planning epic.

## Integration tests (development epics only)
- Not applicable for this research-planning epic.

## Evidence log
- `docs/evidence/E001-evidence-log.md`

## User stories
- S001 - Protocol baseline and scope lock
- S002 - Prior-art and benchmarked-gap mapping for QRoPE
- S003 - Relative-phase formalization and theorem conditions
- S004 - Minimal publishable experiment design and ablation grid
- S005 - Novelty decision memo and claim-boundary lock
- S006 - Ablation implementation runbook and configs
- S007 - Open-source and cloud platform decision
- S008 - Open-source release skeleton
- S009 - Implementation codebase selection and bootstrap
- S010 - First ablation batch execution
- S011 - Train/inference integration for real metrics
- S012 - Real data ingestion and slice rerun
- S013 - Real-data matrix expansion
- S014 - Real-mode replacement wave 1
- S015 - Amazon real-data ingestion and replacement wave 2
- S016 - Final dry-row replacement wave
- S017 - Statistical rigor and hardware expansion plan
- S018 - Summary v2 statistical reporting
- S019 - Quantum simulator backend integration
- S020 - Cloud account onboarding (HITL)
