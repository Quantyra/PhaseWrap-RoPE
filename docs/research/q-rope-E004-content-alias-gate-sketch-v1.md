# Q-RoPE E004 Content-Alias Gate Sketch v1

## BLUF
- The candidate should only open if alias pressure is real and bounded.
- Same-class distractors must be active by construction.
- One frozen symbolic family must span all allowed alias patterns.

## Gate Sketch
- require bounded candidate counts only
- require bounded content classes only
- require at least one same-class distractor in every active set
- require target-slot rotation so alias resolution cannot collapse into slot identity
- forbid raw token identity, latent ids, per-slot lookup tables, and count-specific symbolic families
- reject immediately if content-only bounded controls solve the task by construction
