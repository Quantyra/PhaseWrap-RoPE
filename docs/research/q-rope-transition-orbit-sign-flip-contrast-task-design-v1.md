# Q-RoPE Transition Orbit Sign-Flip Contrast Task Design v1

Date: 2026-03-11
Stories: S427

## Preserved Next Angle
- future task id: `synthetic_transition_orbit_sign_flip_contrast_binary`

## Rationale
- the stopped sign-consistency branch showed that paired directional labels still collapsed into zero positive-class F1 under the current task shape
- the next line should force balanced `hold` versus `flip` contexts by construction rather than deriving consistency from a weak paired-context split
- the task should make directional change itself the supervised object:
  - positive label: controlled context perturbation flips the latent sign
  - negative label: controlled context perturbation preserves the latent sign

## Guardrail
- keep the line memo-only until the sign-flip contrast task is specified exactly and bound to bounded symbolic flip/hold controls
