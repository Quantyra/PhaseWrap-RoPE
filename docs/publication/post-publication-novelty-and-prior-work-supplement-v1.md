# Post-Publication Novelty And Prior-Work Supplement v1

Status: `ANALYZED_WITH_PRIMARY_SOURCE_CHECK`

Date: `2026-05-25`

Repository: public `Quantyra/PhaseWrap`

Related review matrix: [post-publication review decision matrix v2](post-publication-review-decision-matrix-v2.md)

## Question

Is the PhaseWrap methodology warning novel?

Specifically: is it new to warn that a retrieval benchmark can look solved because an assistance pipeline, support-recovery mechanism, copy route, or no-position control is doing the work rather than the claimed positional encoding?

## Short Answer

No, the general warning is not novel.

The broad concern is already established under shortcut learning, spurious-cue exploitation, controlled evaluation, control tasks for probes, and NoPE/NoPos positional-encoding studies.

The defensible PhaseWrap contribution is narrower: a fully auditable worked example showing this concern inside one staged positional-retrieval research program, with exact score theory, frozen artifacts, no-position controls, failed promotion gates, Stage 80/81 support-routing findings, and explicit claim boundaries.

## Primary-Source Check

| Prior-work area | Representative source | What it establishes | Relevance to PhaseWrap |
| --- | --- | --- | --- |
| Shortcut learning | Geirhos et al. (2020), "Shortcut Learning in Deep Neural Networks" | Deep networks can solve benchmarks through shortcuts that differ from the intended mechanism. | PhaseWrap's assistance-pipeline confound is a specific shortcut-learning case. |
| NLI heuristics | McCoy et al. (2019), "Right for the Wrong Reasons" | Models can perform well on standard examples while relying on syntactic heuristics that fail on controlled challenge sets. | Supports the need for controls that break unintended solving paths. |
| Spurious cues in argument reasoning | Niven and Kao (2019), "Probing Neural Network Comprehension of Natural Language Arguments" | BERT's benchmark performance can be explained by spurious statistical cues. | Direct precedent for saying benchmark success is not mechanism evidence by itself. |
| Probe control tasks | Hewitt and Liang (2019), "Designing and Interpreting Probes with Control Tasks" | A probe should score high on the intended task and low on a control task; otherwise interpretation is weak. | Closest methodological analogue to requiring `no_position` and other method-nonspecific controls. |
| Word order and MLMs | Sinha et al. (2021), "Order Word Matters Pre-training for Little" | Strong downstream behavior can persist despite word-order perturbations. | Supports caution around assuming explicit order mechanisms are doing the work. |
| Transformers without explicit positions | Haviv et al. (2022), "Transformer Language Models without Positional Encodings Still Learn Positional Information" | Causal transformer LMs without explicit positional encodings remain competitive and can infer position implicitly. | Direct prior warning that explicit positional encodings are not always the load-bearing component. |
| NoPE length generalization | Kazemnejad et al. (2023), "The Impact of Positional Encoding on Length Generalization in Transformers" | NoPE is a required baseline in positional-encoding length-generalization claims and can outperform explicit schemes in studied settings. | Direct positional-encoding precedent for PhaseWrap's `no_position` control concern. |
| NoPE context limits and tuning | Wang et al. (2024), "Length Generalization of Causal Transformers without Position Encoding" | NoPE can generalize beyond explicit position encodings in some settings, but has limits and attention-distraction failure modes. | Shows the NoPE story is active, nuanced prior work rather than an isolated observation. |

## Novelty Decision

| Claim candidate | Decision | Rationale |
| --- | --- | --- |
| "Shortcut learning can make benchmark success misleading." | `not_novel` | Established by broad ML methodology literature. |
| "Control tasks/no-position controls are necessary for interpretation." | `not_novel` | Established by probe-control and NoPE/NoPos literature. |
| "NoPE or NoPos can perform strongly despite no explicit positional encoding." | `not_novel` | Established by Haviv et al., Kazemnejad et al., Wang et al., and related work. |
| "PhaseWrap Stage 80/81 show support-routed repairs solve phase-cued retrieval for `no_position` too." | `repo_specific` | This is specific to the PhaseWrap artifact trail and should be presented as a worked example. |
| "The PhaseWrap repo gives an auditable negative-results packet around this failure mode." | `potential_contribution` | The combination of frozen packets, exact score theory, staged failures, no-position controls, and claim cards is the publication value. |
| "External positional-encoding papers are suspect." | `do_not_claim` | A paper should not be called suspect without reproducing its experiments and controls. The acceptable claim is category-level: papers lacking NoPE/control baselines have weaker support for strong mechanism claims. |

## Publication Guidance

The methodology paper should say:

> This warning is an instance of established shortcut-learning and control-task concerns. PhaseWrap contributes a worked negative-results case study in positional retrieval benchmarks, not a new conceptual category.

The methodology paper should not say:

> PhaseWrap discovers that no-position controls can invalidate positional-encoding benchmarks.

The paper may say:

> Positional-encoding studies that omit no-position or method-nonspecific controls provide weaker evidence for mechanism-specific claims, especially on synthetic retrieval or passkey-style tasks where auxiliary routing or copy paths may solve the benchmark.

The paper should avoid naming external papers as "suspect" unless PhaseWrap actually reproduces them under stronger controls.

## Recommended Citation Set

The current methodology paper should cite, at minimum:

- Geirhos et al. (2020) for shortcut learning.
- Hewitt and Liang (2019) for control-task methodology.
- McCoy et al. (2019) and Niven and Kao (2019) for controlled challenge sets and spurious cues.
- Haviv et al. (2022), Kazemnejad et al. (2023), and Wang et al. (2024) for NoPE/NoPos positional-encoding precedents.
- Sinha et al. (2021) for word-order robustness in masked language model pretraining.

These entries are now recorded in [references.bib](references.bib).

## Sources Checked

- Geirhos et al. (2020), Nature Machine Intelligence: `https://doi.org/10.1038/s42256-020-00257-z`
- Hewitt and Liang (2019), ACL Anthology: `https://aclanthology.org/D19-1275/`
- McCoy et al. (2019), ACL Anthology: `https://aclanthology.org/P19-1334/`
- Niven and Kao (2019), ACL Anthology: `https://aclanthology.org/P19-1459/`
- Sinha et al. (2021), ACL Anthology: `https://aclanthology.org/2021.emnlp-main.230/`
- Haviv et al. (2022), ACL Anthology: `https://aclanthology.org/2022.findings-emnlp.99/`
- Kazemnejad et al. (2023), NeurIPS: `https://proceedings.neurips.cc/paper_files/paper/2023/hash/4e85362c02172c0c6567ce593122d31c-Abstract-Conference.html`
- Wang et al. (2024), ACL Anthology: `https://aclanthology.org/2024.findings-acl.834/`
