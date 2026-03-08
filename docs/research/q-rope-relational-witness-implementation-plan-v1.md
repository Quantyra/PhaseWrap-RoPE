# Q-RoPE Relational Witness Implementation Plan v1

## Scope
- story: `S157`
- candidate: `V_future_relational_witness`
- baseline: `V0`
- task: `synthetic_sector_parity_binary`
- backend: `sim_quantum_statevector`

## Writable files
Only these files may change in the implementation phase:
- `src/qrope/synthetic.py`
- `src/qrope/qsim.py`
- `src/qrope/run.py`
- focused tests in `tests/`

No remote adapters, reporting pipelines, or broader benchmark configs may change.

## Required implementation units
### Dataset unit
Reuse:
- `synthetic_sector_parity_binary`

No new dataset family is allowed in this phase.

### Quantum feature unit
Produce only the approved sector-first feature schema:
- `mu_P_small`
- `mu_P_large`
- `mu_N_small`
- `mu_N_large`
- `delta_sign_small`
- `delta_sign_large`
- `delta_mag_pos`
- `delta_mag_neg`
- `delta_task`

### Witness-head unit
Add one candidate:
- `V_future_relational_witness`

Head requirements:
- logistic-regression-equivalent only
- no hidden layer
- fixed feature order
- auditable coefficients and intercept

### Baseline unit
Reuse:
- `V0`

No second baseline is allowed.

## Required diagnostics
Each witness-head run must emit:
- feature ordering
- per-feature coefficient values
- intercept
- per-sector response summary
- `delta_task`
- `anti_collapse_pass`
- explicit proof that forbidden inputs are absent

## Required tests
Add focused tests for:
- witness feature extraction order
- sector-parity run diagnostics carrying coefficient audit outputs
- forbidden-input absence at the runner boundary

## Packet boundary
The first and only implementation packet after code lands must be:
- seeds `42`, `123`, `777`
- `V0` vs `V_future_relational_witness`
- `sim_quantum_statevector`

No additional packet is approved in the same story.

## Stop conditions
Stop immediately if implementation pressure creates:
- hidden-layer expansion
- second candidate branch
- feature leakage beyond the approved schema
- hyperparameter search
- remote hooks

## Next step
Implement the bounded relational witness path and execute only the fixed first packet.
