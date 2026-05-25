# PhaseWrap-RoPE roadmap

Status: `negative_results_publication_roadmap`

Date: `2026-05-23`

This roadmap turns external feedback into implementation tracks. The positive replacement line is closed; the active goal is a negative-results publication package that does not broaden the current claim boundary.

Canonical decision: [PhaseWrap research program decision](publication/phasewrap-research-program-decision-v1.md).

Execution freeze: [PhaseWrap execution freeze](publication/phasewrap-execution-freeze-v1.md).

| Track | Status | Next action |
| --- | --- | --- |
| Framing and motivation | In progress | Keep the public answer to "why quantum hardware?" explicit: the score is classical; hardware is a bounded readout witness/probe. |
| Core API | In progress | Expose and test the stable `qrope.scoring` API before migrating stage internals. |
| Dependency hygiene | In progress | Keep provider dependencies optional through extras and document base versus hardware installs. |
| Repository structure | Done | Root `stories/` and `epics/` removed from the public method repository; planning artifacts are retained outside this repo. |
| Documentation site | In progress | API documentation now starts at `docs/api/scoring.md`; next step is publishing the docs tree through GitHub Pages or ReadTheDocs. |
| Standard benchmark | Protocol ready | Implement the predeclared benchmark in `docs/research/q-rope-standard-benchmark-protocol-v1.md` before any stronger RoPE-facing claim. |
| Hardware-specific claim test | Protocol ready | Implement the preregistered same-packet comparison in `docs/research/q-rope-hardware-specific-claim-test-v1.md` before claiming a hardware-specific contribution beyond witness behavior. |
| Negative-results publication | Active | Prepare the essential Stage 67-96 methodology paper described in `docs/publication/negative-results-publication-roadmap-v1.md`; treat score theory and evidence hygiene as optional follow-ons. |
| PhaseWrap-positive execution | Frozen | Do not add new positive-replacement stages unless a reopen gate in `docs/publication/phasewrap-research-program-decision-v1.md` is predeclared. |
| External publication | Planned | Prepare arXiv/OSF/blog outreach only after the negative-results framing and verifier gate remain green. |
