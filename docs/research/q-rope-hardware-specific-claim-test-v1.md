# PhaseWrap-RoPE Hardware-Specific Claim Test v1

Date: `2026-05-23`

Status: `preimplementation_protocol`

## Purpose

This protocol addresses the core reviewer challenge: if `SQR = m8 * m12` is exactly CPU-computable, what does live hardware add?

The current answer is bounded and conservative: hardware adds a noisy-readout witness and provider audit trail, not computational necessity. A stronger hardware-specific contribution requires a preregistered same-packet comparison that shows the hardware variant contributes behavior beyond the exact classical feature and product-state readout.

## Promotion Question

On the same frozen packet and interpretation code, does the CX hardware readout provide a statistically stable improvement over:

- exact classical `m8*m12`;
- direct mod-24 lookup;
- product-state hardware readout;
- matched noisy simulator controls based on backend properties?

## Minimum Design

The first implementation should use one small, capped experiment:

- same rows, seeds, and templates for product-state and CX circuits;
- same shot count per template;
- predeclared bitstring-order calibration;
- backend-property noise model archived before submission;
- classical exact baseline computed from `qrope.scoring`;
- shot-resampling intervals from raw counts;
- bootstrap intervals over rows;
- no post-hoc filtering beyond predeclared failed-job exclusion rules.

## Claim Gate

A positive result may support only this claim:

> On the tested backend/date/calibration window, the CX readout produced a bounded noisy-witness improvement over the matched product-state readout and predeclared noisy-simulator controls.

It does not support:

- quantum advantage;
- a need for quantum computation to evaluate PhaseWrap;
- broad cross-backend robustness;
- transformer-scale model improvement.

## Stop Condition

If CX does not beat product-state and backend-property noisy-simulator controls under the same packet and intervals, the hardware lane remains a witness/audit lane only. The paper should keep the current conservative framing and avoid hardware-specific contribution language.
