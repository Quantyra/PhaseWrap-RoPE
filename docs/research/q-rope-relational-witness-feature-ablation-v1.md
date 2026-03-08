# Q-RoPE Relational Witness Feature-Ablation v1

## Scope
- Story: `S164`
- Task: `synthetic_sector_parity_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Candidate: `V_future_relational_witness`
- Settings:
  - `full`
  - `group_A_sector_means`
  - `group_B_sign_contrasts`
  - `group_C_magnitude_contrasts`
  - `group_D_task_contrast`

## Mean results
| Setting | Mean accuracy | Mean F1 | Mean task contrast | Anti-collapse | Forbidden inputs absent |
| --- | ---: | ---: | ---: | --- | --- |
| `full` | `1.000000` | `1.000000` | `-0.005529` | `true` | `true` |
| `minus_group_A` | `1.000000` | `1.000000` | `-0.005529` | `true` | `true` |
| `minus_group_B` | `0.984375` | `0.985075` | `-0.005529` | `true` | `true` |
| `minus_group_C` | `1.000000` | `1.000000` | `-0.005529` | `true` | `true` |
| `minus_group_D` | `1.000000` | `1.000000` | `-0.005529` | `true` | `true` |

## Primary read
The witness branch survived the bounded feature-group ablation packet cleanly.

The only measurable degradation came from removing:
- `group_B_sign_contrasts`

Even there, the drop was small.

## What this rules out
### Not a `delta_task` shortcut
Removing `group_D_task_contrast` did not reduce performance.

So the current positive packet cannot be explained as:
- the head reading one prepacked task-style scalar and ignoring the rest.

### Not dependent on raw sector means alone
Removing `group_A_sector_means` also left the packet unchanged.

So the current result is not being carried only by the raw sector means.

## What this implies
The current witness schema is:
- not narrowly brittle around one single approved feature group
- but also highly redundant

The strongest current signal is that:
- sign-contrast features matter somewhat
- the remaining approved groups appear substitutable under the present task

## Coefficient pattern
Under the full witness model, the largest mean absolute coefficients were on derived contrasts rather than raw means.

Most prominent full-model groups:
- sign contrasts
- magnitude contrasts
- `delta_task`

Raw means had smaller coefficients, and removing them did not hurt the packet.

## Correct interpretation
This is a positive internal-reliance result.

What is stronger now:
- the branch is not driven by `delta_task` alone
- the branch survives removal of three of the four approved feature groups without collapse
- anti-collapse and forbidden-input constraints still hold everywhere

What is still not justified:
- benchmark expansion
- remote execution
- claiming that all approved features are equally necessary

## Bottom line
The witness branch remains active.
The bounded ablation packet strengthened validity by ruling out the narrowest shortcut explanation.
The next step should be another memo-level decision about whether the remaining uncertainty is worth one more bounded control or whether the branch is strong enough for a later non-benchmark synthetic extension.
