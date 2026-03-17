# Q-RoPE E007 Reference Revision Implementation v1

Date: 2026-03-16
Stories: S1486-S1489

## Scope
- Implemented `synthetic_positional_reference_revision_selection_response` inside the frozen E007 scope.
- Added the witness path, bounded symbolic control path, dataset loader wiring, and focused tests.
- Kept one symbolic family across candidate counts `4` and `5` while enforcing active stale-versus-current competition in every accepted candidate set.

## Notes
- The accepted generator requires one current-valid target, at least one stale analogue, one content-only distractor, and one position-only distractor.
- The stale/current distinction is bounded to the declared revision-validity rule rather than explicit lookup tables.
- The runtime path uses a compact witness basis and a single frozen symbolic family across revision patterns.
- No count-specific or revision-pattern-specific symbolic family was added during implementation.

## Validation
- Focused synthetic and real-mode tests passed before the packet run.
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- `348 passed`
