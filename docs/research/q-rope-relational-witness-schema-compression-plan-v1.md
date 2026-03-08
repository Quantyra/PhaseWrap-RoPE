# Q-RoPE Relational Witness Schema-Compression Plan v1

## Scope
- Story: `S166`
- Branch: `V_future_relational_witness`
- Task: `synthetic_sector_parity_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Baseline comparator: current `full` witness schema

## Why this step exists
The bounded ablation packet showed two things at once:
- the branch is not a narrow `delta_task` shortcut
- the current approved feature schema is highly redundant

So the next useful question is not another generic robustness pass.

It is:
- can the witness win survive under a cleaner, less redundant schema?

## Fixed schema views
### `full`
Keep the current approved feature schema:
- `mu_P_small`
- `mu_P_large`
- `mu_N_small`
- `mu_N_large`
- `delta_sign_small`
- `delta_sign_large`
- `delta_mag_pos`
- `delta_mag_neg`
- `delta_task`

### `means_only`
Keep only raw sector means:
- `mu_P_small`
- `mu_P_large`
- `mu_N_small`
- `mu_N_large`

Mask all derived contrasts:
- `delta_sign_small`
- `delta_sign_large`
- `delta_mag_pos`
- `delta_mag_neg`
- `delta_task`

### `contrasts_only`
Keep only the direct relational contrasts:
- `delta_sign_small`
- `delta_sign_large`
- `delta_mag_pos`
- `delta_mag_neg`

Mask:
- all raw sector means
- `delta_task`

## Why `delta_task` is excluded from compressed views
The ablation packet already showed:
- removing `delta_task` does not weaken the branch

So leaving it inside a compressed view would only preserve redundant structure and weaken the interpretability of the control.

## Exact packet
Run the same three-seed packet under:
- `full`
- `means_only`
- `contrasts_only`

Keep fixed:
- task
- seeds
- backend
- split policy
- head family
- fitting rule

## Required outputs
For each schema view, emit:
- mean accuracy
- mean F1
- coefficient vector
- intercept
- retained feature list
- ablated feature list
- `anti_collapse_pass`
- `forbidden_inputs_absent`

## Interpretation rules
### Stronger branch outcome
The branch becomes structurally stronger if:
- `contrasts_only` stays close to `full`
- and `means_only` degrades materially

That would support the claim that the win lives in a cleaner relational core rather than overcomplete redundancy.

### Mixed outcome
If both compressed views stay near `full`, then:
- the task is likely easy enough that multiple linearly related views solve it
- the branch remains positive, but mechanism specificity stays weaker

### Weakening outcome
If both compressed views collapse materially, then:
- the current win may rely on overcomplete redundancy rather than a compact relational mechanism
- the branch should hold posture and not broaden

## What is explicitly not allowed
- new tasks
- new seeds
- rotated shadow packet expansion
- remote execution
- new candidate branches
- second-wave decompositions such as `sign_only` or `magnitude_only`

## Bottom line
This is one bounded compression control.
It asks whether the witness branch can keep its win on a cleaner relational schema before any broader move is considered.
