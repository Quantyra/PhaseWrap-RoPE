# Q-RoPE E011 Clause-Intersection Gate Sketch v1

Date: 2026-03-18
Stories: S1607-S1609

## Gate Sketch
- The task must contain two explicit bounded clauses that are both decision-critical.
- Neither clause may determine the final target alone.
- One frozen symbolic family only.
- Block by default:
  - token-id shortcuts
  - slot-id shortcuts
  - clause-pattern lookup tables
  - per-count symbolic families
  - transformer surrogates

## Expected Diagnostics
- `coarse_clause_intersection_state_null_pass`
- `within_clause_intersection_state_variation_pass`
- `clause_one_only_null_pass`
- `clause_two_only_null_pass`
- `joint_intersection_nontrivial_pass`
- `candidate_set_nontrivial_pass`
- `bounded_candidate_count_pass`
- `clause_intersection_noncollapse_pass`
