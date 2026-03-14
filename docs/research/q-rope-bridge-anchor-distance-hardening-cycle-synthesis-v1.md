# Q-RoPE Bridge Anchor-Distance Hardening Cycle Synthesis v1

## Outcome
- `anchor-distance` survived the full bounded hardening cycle.
- It is a weaker bridge survivor than `anchor-order`.

## Why It Is Weaker
- The witness beat the bounded control on the declared stop rule, but the rank signal stayed poor.
- Base and most structural packets had negative mean rank correlation for both models.
- The line therefore preserves a relevance-bridge foothold, not a strong bridge result.

## Mean Packet Trail
- Base:
  - witness: `mae 0.164006`, `rank_correlation -0.266667`
  - control: `mae 0.207028`, `rank_correlation -0.933333`
- `token_permutation=cdab`:
  - witness: `mae 0.138297`, `rank_correlation 0.200000`
  - control: `mae 0.215227`, `rank_correlation -0.600000`
- `pair_reindex=1`:
  - witness: `mae 0.124019`, `rank_correlation -0.666667`
  - control: `mae 0.127504`, `rank_correlation 0.066667`
- `slot_swap=1`:
  - witness: `mae 0.212503`, `rank_correlation -0.333333`
  - control: `mae 0.218497`, `rank_correlation -0.266667`
- `pair_reindex=7`:
  - witness: `mae 0.122907`, `rank_correlation -0.466667`
  - control: `mae 0.144214`, `rank_correlation -0.466667`
