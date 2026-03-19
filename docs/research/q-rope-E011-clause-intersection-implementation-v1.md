# Q-RoPE E011 Clause-Intersection Implementation v1

Date: 2026-03-19
Stories: S1614-S1617

## BLUF
- Implemented `synthetic_positional_clause_intersection_reference_selection_response` inside the frozen E011 scope.
- The implementation keeps one bounded clause-intersection symbolic family across candidate counts `4` and `5` with exactly two decision-critical clauses.
- The first packet is mixed, so the next valid move is retained nuisance hardening rather than stop or preserve.

## Writable Scope Used
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Validation
- focused E011 validation:
  - `3 passed in 161.56s (0:02:41)`
- repo-standard validation:
  - `360 passed in 1387.92s (0:23:07)`
