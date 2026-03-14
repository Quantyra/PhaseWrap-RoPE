# AGENTS

This repository tracks work for Quantum Rotational Positional Embeddings (QRoPE) research. All contributors and agents must follow the protocols in the main `../Quantyra` repository, with any additional protocols defined here.

## Where Things Live
- Main protocols: `../Quantyra`
- QRoPE-specific protocols: `docs/protocols/`
- Process docs: `docs/process/`
- Research artifacts: `docs/`, `epics/`, `stories/`
- Templates: `templates/`
- Session state: `logs/checkpoint.json`

## Protocol Expectations
- Follow Quantyra research and documentation protocols first.
- Apply QRoPE repo-specific protocols in `docs/protocols/`.
- Keep all high-impact technical claims source-tagged and auditable.
- Record significant decisions as ADRs if adopted in this repo.
- Keep artifacts current as scope evolves.
- Link related artifacts directly in issues and PRs.

## Orchestrator Role
The Orchestrator (Codex) is responsible for:
- Enforcing protocol adherence and artifact quality.
- Coordinating across research, engineering, and documentation inputs.
- Maintaining traceability between protocols, decisions, and artifacts.
- Keeping repository structure clean and consistent.

## VP Of Research Proxy
- For this repository, the Orchestrator also operates as the VP-of-Research proxy when making research-program judgments.
- The governing protocols for that role are `docs/protocols/vp-of-research-proxy.md` and `docs/protocols/portfolio-saturation-and-review.md`.
- Program-level judgments from the proxy must remain:
  - auditable,
  - bounded by repository protocols,
  - consistent with epic/story/evidence/checkpoint state.

## Working Guidance
- Keep artifacts concise, explicit, and reproducible.
- Prefer primary sources and clear separation of sourced facts vs inference.
- Escalate unresolved scientific contradictions instead of forcing closure.

