# Q-RoPE E009 Scope-Masking Implementation v1

Date: 2026-03-16
Stories: S1550-S1553

## Scope
- Implemented `synthetic_positional_scope_masked_reference_selection_response` inside the frozen E009 scope.
- Added the witness path, bounded symbolic control path, dataset loader wiring, and focused tests.
- Kept one symbolic family across candidate counts `4` and `5` with exactly one active local scope and one stronger out-of-scope distractor per accepted example.

## Notes
- The accepted generator uses one in-scope valid target plus one out-of-scope stronger apparent match that is invalidated only by scope masking.
- Scope remains auditable from declared positional-content summaries and does not use explicit scope ids or lookup tables.
- The runtime path uses a compact witness basis and a single frozen symbolic family across allowed scope patterns.

## Validation
- Exact E009 synthetic and real-mode tests passed before the packet run.
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py::test_positional_scope_masked_reference_selection_bundle_enforces_declared_diagnostics tests/test_run_real_mode.py::test_positional_scope_masked_reference_selection_witness_backend_runs tests/test_run_real_mode.py::test_positional_scope_masked_reference_selection_symbolic_control_freezes_basis -q`
- `3 passed`
- Repo-standard validation was started but not carried through to completion before the packet run.
