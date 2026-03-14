# Q-RoPE Bridge Anchor-Order Hardening Cycle Synthesis v1

## Outcome
- The first bridge-task candidate, `synthetic_positional_anchor_order_response`, survived the full bounded hardening cycle.
- The witness stayed ahead of the bounded symbolic control on mean `mae` and mean `rank_correlation` in the base packet and in each retained-model hardening packet.

## Mean Packet Trail
- Base:
  - witness: `mae 0.104561`, `rank_correlation 0.123543`
  - control: `mae 0.117350`, `rank_correlation -0.403263`
- `token_permutation=cdab`:
  - witness: `mae 0.108051`, `rank_correlation 0.268066`
  - control: `mae 0.132873`, `rank_correlation -0.372960`
- `pair_reindex=1`:
  - witness: `mae 0.156054`, `rank_correlation 0.163170`
  - control: `mae 0.162997`, `rank_correlation -0.111888`
- `slot_swap=1`:
  - witness: `mae 0.139765`, `rank_correlation 0.170163`
  - control: `mae 0.153458`, `rank_correlation -0.349650`
- `pair_reindex=7`:
  - witness: `mae 0.119600`, `rank_correlation 0.195804`
  - control: `mae 0.141610`, `rank_correlation -0.282051`

## Interpretation
- The result is still local and synthetic.
- It is stronger than ordinary transfer evidence because it is the first preserved bridge-task line aimed at anchor-relative positional order.
- It is still not a hardware or publication claim.
