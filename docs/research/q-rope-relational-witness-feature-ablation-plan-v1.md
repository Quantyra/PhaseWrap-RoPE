# Q-RoPE Relational Witness Feature-Ablation Plan v1

## Scope
- Story: `S163`
- Branch: `V_future_relational_witness`
- Task: `synthetic_sector_parity_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Baseline comparator: full witness model on the same packet

## Why this step exists
The branch has already passed:
- the first bounded packet
- split-rotation hardening

The next remaining uncertainty is internal reliance.

We need to learn whether the witness result is:
- distributed across the approved relational schema
or
- carried mainly by one narrow feature group that would make the branch less credible.

## Fixed feature groups
### Group A: sector means
- `mu_P_small`
- `mu_P_large`
- `mu_N_small`
- `mu_N_large`

### Group B: sign contrasts
- `delta_sign_small`
- `delta_sign_large`

### Group C: magnitude contrasts
- `delta_mag_pos`
- `delta_mag_neg`

### Group D: task contrast
- `delta_task`

## Exact ablation packet
Run the same three-seed packet under five witness settings:
- `full`
- `minus_group_A`
- `minus_group_B`
- `minus_group_C`
- `minus_group_D`

For each setting:
- keep the same task
- keep the same train/test split policy
- keep the same head family
- keep the same fitting rule
- mask the ablated group to zero before fitting and inference

## Required outputs
For each ablation setting, emit:
- mean accuracy
- mean F1
- coefficient vector
- intercept
- per-group retained/ablated mask
- `anti_collapse_pass`
- `forbidden_inputs_absent`

Produce one summary memo that compares degradation against `full`.

## Bounded interpretation rule
### Strong distributed evidence
The branch remains structurally stronger if:
- more than one group matters materially
- no single derived shortcut fully explains the result

### Narrow dependence warning
The branch becomes validity-weaker if:
- `minus_group_D` alone collapses performance to near `V0`
and
- the other ablations do little or nothing

### Red-flag outcome
The branch should be reconsidered immediately if:
- ablation shows that one forbidden-in-spirit shortcut dominates the head
- or anti-collapse fails under any ablation condition

## What is explicitly not allowed
- new tasks
- new seeds
- remote execution
- new candidate branches
- new head families
- multi-step ablation cascades

## Split-rotation policy
Default packet:
- `split_rotation = 0`

Shadow packet policy:
- do not run `split_rotation = 1` for all ablations in this step
- only reopen rotated shadowing later if the first ablation packet creates a branch-changing conclusion

## Bottom line
This is one bounded internal-reliance test.
If the witness branch survives it cleanly, the branch becomes materially more credible.
If it fails, the branch should be narrowed or archived instead of broadened.
