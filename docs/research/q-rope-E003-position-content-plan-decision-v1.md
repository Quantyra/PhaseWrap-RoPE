# Q-RoPE E003 Position-Content Plan Decision v1

Date: 2026-03-14
Stories: S1364-S1365

## BLUF
- `synthetic_positional_content_gated_offset_selection_response` passes to one bounded local implementation cycle only.
- The line remains closed until the plan constraints above are honored.
- The stop rule is strict: if either content-only or position-only collapse appears, the line stops immediately.

## Decision
- `PASS_TO_ONE_BOUNDED_LOCAL_IMPLEMENTATION_CYCLE_ONLY`

## What Is Now Frozen
- task:
  - `synthetic_positional_content_gated_offset_selection_response`
- witness:
  - `V_future_relational_witness_positional_content_gated_offset_selection`
- bounded symbolic control:
  - additive and bounded-quadratic regressor over declared query summaries, per-candidate content summaries, per-candidate offset summaries, and bounded aggregate ambiguity summaries only
- candidate-count range:
  - `3`, `4`, `5`
- content-class bound:
  - `3`
- writable scope:
  - `src/qrope/synthetic.py`
  - `src/qrope/run.py`
  - `tests/test_synthetic.py`
  - `tests/test_run_real_mode.py`
- fixed packet:
  - backend `sim_quantum_statevector`
  - seeds `42`, `123`, `777`

## Next Step
- Implement the bounded candidate only inside the frozen scope.
- Run exactly one fixed three-seed packet if the implementation clears all diagnostics and audits.
- Stop immediately if the control matches or beats the witness on both declared mean gate metrics.
