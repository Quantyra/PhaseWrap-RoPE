# Research note

## Scope
- Story: `S201`
- Task: `synthetic_dual_sector_content_agreement_binary`
- Candidate: `V_future_relational_witness_dual_content`
- Controls:
  - `V_control_symbolic_dual_sector_interaction`
  - `V_control_symbolic_dual_content_interaction`
  - `V_control_symbolic_dual_cross_interaction`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`

## Fixed packet result
- `V_future_relational_witness_dual_content`: mean accuracy `1.000000`, mean F1 `1.000000`
- `V_control_symbolic_dual_sector_interaction`: mean accuracy `0.500000`, mean F1 `0.666667`
- `V_control_symbolic_dual_content_interaction`: mean accuracy `0.500000`, mean F1 `0.666667`
- `V_control_symbolic_dual_cross_interaction`: mean accuracy `1.000000`, mean F1 `1.000000`

Summary CSV:
- `logs/ablation_runs/summary/dual_content_coupled_v1.csv`

## Interpretation
- The harder task succeeded in defeating the bounded sector-only and content-only controls.
- The branch did not survive the strongest approved control.
- `V_control_symbolic_dual_cross_interaction` matched the candidate exactly on all three seeds.

## Mechanism read
- The candidate did not win through a richer relational witness geometry.
- Its learned coefficients were dominated by `coupled_xnor` on every seed.
- That is the same effective decision structure exposed directly by the cross-family symbolic interaction control.

Representative witness coefficients:
- seed `42`: `coupled_xnor = 3.357266`
- seed `123`: `coupled_xnor = 3.357282`
- seed `777`: `coupled_xnor = 3.356917`

Representative control coefficients:
- `cross_same__same = +2.280363`
- `cross_same__diff = -2.280363`
- `cross_diff__same = -2.280363`
- `cross_diff__diff = +2.280363`

## Decision
- `NO-GO` for further execution on this task.
- The task remains a valid internal relational benchmark.
- It is no longer a uniqueness test for the witness branch.

## Evidence
- `logs/ablation_runs/future_relational_witness_dual_content-dualcontent-s42/metrics.json`
- `logs/ablation_runs/future_relational_witness_dual_content-dualcontent-s123/metrics.json`
- `logs/ablation_runs/future_relational_witness_dual_content-dualcontent-s777/metrics.json`
- `logs/ablation_runs/control_symbolic_dual_sector_interaction-dualcontent-s42/metrics.json`
- `logs/ablation_runs/control_symbolic_dual_sector_interaction-dualcontent-s123/metrics.json`
- `logs/ablation_runs/control_symbolic_dual_sector_interaction-dualcontent-s777/metrics.json`
- `logs/ablation_runs/control_symbolic_dual_content_interaction-dualcontent-s42/metrics.json`
- `logs/ablation_runs/control_symbolic_dual_content_interaction-dualcontent-s123/metrics.json`
- `logs/ablation_runs/control_symbolic_dual_content_interaction-dualcontent-s777/metrics.json`
- `logs/ablation_runs/control_symbolic_dual_cross_interaction-dualcontent-s42/metrics.json`
- `logs/ablation_runs/control_symbolic_dual_cross_interaction-dualcontent-s123/metrics.json`
- `logs/ablation_runs/control_symbolic_dual_cross_interaction-dualcontent-s777/metrics.json`
