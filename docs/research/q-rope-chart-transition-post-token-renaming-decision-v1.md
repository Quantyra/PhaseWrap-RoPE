# Chart-transition post-token-renaming decision

## Decision
- stop the current chart-transition execution branch
- return the line to memo-only posture

## Why
The hardening rule for this step was straightforward: the witness needed to remain stronger than the strongest current symbolic baseline under a fixed label-preserving token renaming. It did not. The witness kept a stronger rank signal, but it lost on the primary metric, so the branch no longer has the robustness value required for continued execution on the current task.

## Consequence
- do not add more controls to this task
- do not broaden this task to remote or benchmark work
- preserve only the mechanism insight that ordered transition structure mattered under the original token convention
