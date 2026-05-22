# PhaseWrap-RoPE Stage 104 Matched Packet Execution Package v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 104 turns the Stage 103 metric requirement into a concrete matched-packet execution evidence package.

Stage 103 requires canonical `q0q1` `raw_counts_by_row` files for every Stage 99 and Stage 100 matched packet after Stage 101 calibration passes. Stage 104 emits one execution JSON template per matched packet and enforces an all-or-none interpretation rule over complete provider/lane/template comparator groups.

## Reviewer Command

```bash
python scripts/run_stage104_matched_packet_execution_package.py
```

This writes:

- `logs/automated_stage_gates/stage104_matched_packet_execution_package/manifest.json`
- `logs/automated_stage_gates/stage104_matched_packet_execution_package/results.json`
- `logs/automated_stage_gates/stage104_matched_packet_execution_package/summary.csv`
- `logs/automated_stage_gates/stage104_matched_packet_execution_package/packet_execution_templates/*.json`

## Result

Current decision:

`MATCHED_PACKET_EXECUTION_TEMPLATES_PREPARED_CALIBRATION_AND_COUNTS_REQUIRED`

Stage 104 prepares `20` packet execution templates:

- `10` Stage 99 product-state packets;
- `10` Stage 100 CX/parity packets.

The package also validates `4` matched groups: each provider/lane/template group must contain PhaseWrap, RoPE-like, sinusoidal-like, ALIBI-like, and no-position/control packets with matching row-set hashes, row counts, shot counts, and two-qubit fixed-width metadata.

Each template includes:

- packet ID, provider, lane, encoding family, circuit template, and expected shot count;
- backend and calibration metadata placeholders;
- job/task ID and timestamp placeholders;
- one row entry per packet row;
- OpenQASM 3 row programs;
- empty canonical `q0q1` count placeholders.

## Interpretation Rule

Stage 103 interpretation requires:

- Stage 101 known-state calibration pass;
- canonical `q0q1` `raw_counts_by_row` files for every Stage 99 and Stage 100 matched packet;
- complete PhaseWrap/RoPE-like/sinusoidal-like/ALIBI-like/no-position groups under each provider, source lane, and circuit template;
- no cherry-picking of only successful packets or favorable families.

## Claim Boundary

Supported:

- per-packet execution JSON templates for all matched Stage 99 and Stage 100 packets;
- validation that each provider/lane/template group contains the full fixed-width comparator family set;
- a complete handoff contract for calibrated `raw_counts_by_row` evidence;
- an all-or-none interpretation guard for the matched fixed-width hardware comparison.

Excluded:

- real matched packet hardware counts;
- completed Stage 101 calibration;
- a noisy-hardware robustness result;
- a PhaseWrap advantage claim.

## Next Gate

After Stage 101 calibration passes, execute all Stage 99 and Stage 100 matched packets, fill every Stage 104 template with canonical `q0q1` row counts and metadata, then rerun Stage 103 with `--execution-dir`.
