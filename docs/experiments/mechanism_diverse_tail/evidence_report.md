# Mechanism-Diverse Tail Robustness: Evidence Report

## Executive verdict

This report evaluates the bounded conjecture that mechanism-diverse defense
stacks, selected using utility-constrained worst-scenario tail risk, can reduce
common-mode failure under compound multi-agent attacks.

The evidence is deliberately separated into three levels:

1. **Controlled synthetic runs** validate estimators, selectors, split locking,
   and known-positive/known-negative fixtures. They do not establish robustness
   of LLM agents.
2. **Model-backed canaries** establish that the attacks, defenses, and evidence
   paths execute against a pinned 7B open model. They are exploratory and too
   small for confirmatory tail claims.
3. **Frozen held-out evidence** supports only the endpoint actually registered.
   The completed Phase 5 study supplies held-out sequential-monitoring evidence,
   not a held-out test of the full mechanism-diverse conjecture.

The overall conjecture is therefore **not yet confirmed**. The current evidence
supports the feasibility of the harness and three component mechanisms, while
identifying adaptive semantic channels, low-rate attacks, common-mode failure,
and cross-model transfer as the critical remaining tests.

## Evidence ledger

| Experiment | Current evidence | Sample | Result | Claim status |
|---|---|---:|---|---|
| E01 selector comparison | Controlled trajectory experiment | 1,200 validation + 1,200 sealed test trajectories | All five selectors choose `diverse-stack`; proposed advantage is 0.00 | Inconclusive by design; no selector-superiority claim |
| E02 failure complementarity | Controlled matched attack panels plus structural/model precursors | 2,400 controlled trajectories; 41 coalitions × 4 scripted topologies; 64 model-backed channel episodes | Diverse-stack joint bypass 0.031 versus 0.631 homogeneous; realized bypass 0.056 versus 0.650 | Synthetic gate passes; LLM-agent complementarity untested |
| E03 adaptive best response | Controlled adaptation plus 7B registered-codebook canary | 2,400 controlled trajectories; 64 Qwen2.5-7B episodes | Controlled adaptive worst-scenario CVaR 0.93 versus 1.00 homogeneous; registered semantic adaptation defeats paraphrase in the 7B canary | Synthetic gate and model manipulation check pass; autonomous best response untested |
| E04 compound held-out transfer | Controlled structural holdout | 3 synthetic predictive stacks; 3 compound synthetic scenarios | Validation complementarity/held-out robustness Spearman 0.866; compound gate fails because E01 has no advantage | Not supported; blocked on discriminative validation design and a held-out 7–9B family |
| E05 irreversibility and sequential validity | Controlled enforcement plus frozen held-out Phase 5 evidence and 7B workflow precursor | 2,400 controlled trajectories; 900 Qwen2.5-7B sequential episodes; 24 Qwen2.5-7B vLLM workflow episodes | Synthetic harm 0.725 → 0.025; before-harm intervention 0.95; Phase 5 before-harm rates 0.275–1.00 | Synthetic gate passes; model-backed end-to-end diverse enforcement remains unconfirmed |

## Conjecture and primary estimands

For stack \(\pi\), attack scenario \(g\), stack-aware attacker \(a\), and stochastic
trajectory \(\omega\), the proposed selector minimizes an uncertainty-adjusted
worst-scenario upper-tail loss subject to operational constraints:

\[
\hat\pi = \arg\min_{\pi:\,\mathrm{LCB}(U_\pi)\ge u_{\min}}
\max_g \mathrm{UCB}\!\left[
\operatorname{CVaR}^{\mathrm{upper}}_q
Z(\pi,g,BR(\pi,g),\omega)
\right].
\]

The selector is not the full scientific claim. The distinctive mechanism claim
is that failure diversity measured on fixed matched attack panels predicts
closed-loop and held-out robustness. For singleton bypass indicators \(F_j\):

\[
\Gamma_\pi(g)=\min_j P(F_j=1\mid g)
-P(\cap_j F_j=1\mid g).
\]

Every experiment must additionally report actual stack bypass \(p_\pi\), realized
gain \(\min_j p_j-p_\pi\), and interaction gap \(p_\pi-p_\cap\). This prevents a
counterfactual singleton intersection from being mistaken for deployed-stack
performance.

## Controlled E01–E05 execution

The new runner generated a manifest of 2,400 unique assignments bound to
implementation revision `19abf75`: 1,200 validation trajectories and 1,200
test trajectories. Test execution required the frozen selection artifact and
verified specification, manifest, validation-artifact, and selection hashes.

| Experiment | Primary controlled result | Gate |
|---|---:|---|
| E01 | All five selectors choose `diverse-stack`; improvement 0.00 | **Inconclusive** |
| E02 | \(\Gamma=0.406\), realized gain 0.381, diverse versus homogeneous bypass difference 0.600 | **Pass (synthetic)** |
| E03 | Adaptive worst-scenario CVaR 0.93 diverse versus 1.00 homogeneous; difference 0.07 | **Pass (synthetic)** |
| E04 | Validation complementarity/held-out robustness Spearman 0.866; three compound scenarios | **Fail**, because the registered compound selector advantage is absent |
| E05 | Irreversible harm 0.725 → 0.025; harm reduction LCB 0.527; before-harm 0.95 | **Pass (synthetic)** |

E01 is a useful negative result: because every selector chose the same stack,
the fixture contains no evidence that the proposed hierarchical tail selector
is better than pooled mean, pooled CVaR, or worst-scenario mean selection. E04
correctly remains false rather than treating favorable rank correlation as a
complete transfer result.

The controlled benign stratum contained 40 episodes for the selected stack and
zero false alarms. Its Wilson upper bound is 0.063, which passes the synthetic
fixture's registered 0.10 ceiling but would not certify a 0.05 ceiling.

### Integrity identifiers

- specification: `bc15d847f4bdd0c015e47d37b6c1a41e20a6049a37c1affd9161193de312d1bf`
- manifest: `f3dc24f33ae1a0d6a82d539bde429ef10b898ec77f7ece252548d4364d0995a1`
- validation artifact: `2e714a367422a17fb211f2ae7ce8b4e371522da4d9c723eac3d150369d8a5c49`
- selection: `257b886a599ba5b1f0039be5608a77a534fd8bb327cfebf353d6e2d7383cdf75`
- test artifact: `bbc1ec7c9840703064a8be24135bc88a6f7fa02eb4545c6b26a71f7c6ff88198`
- final report: `5d4ce6c7e90317cc9531df344c8f324d01bdf934aa91a71204c571a786a3a184`

## Existing model-backed findings

### Covert channels defeat surface-only mediation

The pinned Qwen2.5-7B vLLM canary executes 16 episodes in each of four
conditions. Attack success is 1.00 for unrestricted communication, 0.25 after
generic paraphrasing of the fixed surface code, 1.00 after registered semantic
adaptation, and 0.25 under a typed mediator. Utility is 1.00 in every condition.

Interpretation: a defense that suppresses one representation does not suppress
the task-compatible channel capacity. A task-sufficient typed protocol is more
robust in this registered setting because it removes carrier degrees of freedom.
This is not evidence against unregistered tool, timing, state, or environmental
channels.

### Consequence-aware repair can dominate indiscriminate blocking

The pinned Qwen2.5-7B vLLM workflow canary contains four episodes per condition
and reproduces the earlier direct-Transformers result. The registered harmful
workflow succeeds under no defense and local-only checks. Hard blocking
prevents the harm but reduces exact utility to zero. Targeted provenance repair
prevents the harm while preserving exact utility at 1.00, and it does not
remediate any benign canary episode. Mean episode latency is 27.1--27.5 seconds.
The sample is too small for a general effect claim, but it validates the
end-to-end remediation path on the deployment runtime.

### Sequential validity is possible, but monitor superiority is not established

The frozen Phase 5 experiment contains 200 calibration, 140 validation, and 560
test episodes on pinned Qwen2.5-7B. Across the three benign test strata there
were zero lifetime alarms in 80 episodes each; the Wilson upper bound is 0.0458,
below the registered 0.05 threshold. Before-harm rates were 1.00 for delayed
triggers, 0.275 for low-rate attacks, and 0.75 for both memory-poisoning and
reward-induced attacks.

All three monitors calibrated to degenerate zero thresholds and produced the
same alarm rates. The e-process was often slower. The defensible conclusion is
bounded lifetime-error evidence under the registered exchangeability design,
not superiority of the e-process.

## Attack-dimension coverage

| Section 3.3 dimension | Executed precursor | New decisive test |
|---|---|---|
| Detectability | Visible, lexical, distribution-matched, fixed and semantic codebooks | Tool-mediated and distribution-matched best responses |
| Locality | Two-agent channels and six-role coalitions | Held-out coalition sizes and non-local shared state |
| Cascading | Chain, tree, sparse mesh, dense scripted topology | Model-backed propagation and containment |
| Multi-step composition | Six-role typed workflow | Deeper heterogeneous tool/action composition |
| Time horizon | 100-turn model-backed and 256-turn controlled streams | Longer horizons and delayed attacker adaptation |
| Attributability | Faithful provenance and localized responsible subgraphs | Degraded, missing, and adversarial provenance |
| Directness | Explicit, reward-induced, memory-poisoning | Emergent/no-explicit-attacker conditions |
| Reversibility | Registered irreversible step and action gate | Severity-weighted irreversible consequences under enforcement |

## Reproduction

Mechanism-diverse E01--E05 suite:

```bash
.venv/bin/python -m agent_defense_evals phase7-tail-plan --config configs/experiments/phase7_tail_robustness_synthetic.yaml --output artifacts/asap-evidence/tail-manifest.json --implementation-revision 19abf75
.venv/bin/python -m agent_defense_evals phase7-tail-run --config configs/experiments/phase7_tail_robustness_synthetic.yaml --manifest artifacts/asap-evidence/tail-manifest.json --split validation --output artifacts/asap-evidence/tail-validation.json
.venv/bin/python -m agent_defense_evals phase7-tail-select --config configs/experiments/phase7_tail_robustness_synthetic.yaml --manifest artifacts/asap-evidence/tail-manifest.json --validation-results artifacts/asap-evidence/tail-validation.json --output artifacts/asap-evidence/tail-selection.json
.venv/bin/python -m agent_defense_evals phase7-tail-run --config configs/experiments/phase7_tail_robustness_synthetic.yaml --manifest artifacts/asap-evidence/tail-manifest.json --selection artifacts/asap-evidence/tail-selection.json --split test --output artifacts/asap-evidence/tail-test.json
.venv/bin/python -m agent_defense_evals phase7-tail-report --config configs/experiments/phase7_tail_robustness_synthetic.yaml --manifest artifacts/asap-evidence/tail-manifest.json --selection artifacts/asap-evidence/tail-selection.json --validation-results artifacts/asap-evidence/tail-validation.json --test-results artifacts/asap-evidence/tail-test.json --output artifacts/asap-evidence/tail-report.json
```

Controlled reruns:

```bash
.venv/bin/python -c 'from agent_defense_evals.cli import main; main()' phase3-run --config configs/experiments/phase3_causal_information.yaml --output artifacts/asap-evidence/phase3-controlled.json
.venv/bin/python -c 'from agent_defense_evals.cli import main; main()' phase4-run --config configs/experiments/phase4_coalitional_hyperproperties.yaml --output artifacts/asap-evidence/phase4-controlled.json
.venv/bin/python -c 'from agent_defense_evals.cli import main; main()' phase5-run --config configs/experiments/phase5_anytime_evidence.yaml --output artifacts/asap-evidence/phase5-controlled.json
.venv/bin/python -c 'from agent_defense_evals.cli import main; main()' phase6-run --config configs/experiments/phase6_capacity_shaping.yaml --output artifacts/asap-evidence/phase6-controlled.json
.venv/bin/python -c 'from agent_defense_evals.cli import main; main()' phase7-run --config configs/experiments/phase7_controlled_optimization.yaml --output artifacts/asap-evidence/phase7-controlled.json
```

Pinned 7B vLLM canaries:

```bash
.venv/bin/python -c 'from agent_defense_evals.cli import main; main()' phase7-model-capacity --config configs/experiments/phase7_model_capacity_7b_vllm.yaml --output artifacts/asap-evidence/phase7-model-capacity-7b-vllm.json
.venv/bin/python -c 'from agent_defense_evals.cli import main; main()' phase7-model-workflow --config configs/experiments/phase7_model_workflow_7b_vllm.yaml --output artifacts/asap-evidence/phase7-model-workflow-7b-vllm.json
```

## Sources and evidence files

- Schroeder de Witt et al., [Open Challenges in Multi-Agent Security](https://arxiv.org/abs/2505.02077), especially Section 3.3.
- Rockafellar and Uryasev, [Optimization of Conditional Value-at-Risk](https://uryasev.github.io/publications/).
- Sagawa et al., [Distributionally Robust Neural Networks for Group Shifts](https://arxiv.org/abs/1911.08731).
- Howard et al., [Time-uniform, nonparametric, nonasymptotic confidence sequences](https://arxiv.org/abs/1810.08240).
- Ramdas et al., [Game-theoretic statistics and safe anytime-valid inference](https://arxiv.org/abs/2210.01948).
- Motwani et al., [Secret Collusion among AI Agents](https://papers.neurips.cc/paper_files/paper/2024/file/861f7dad098aec1c3560fb7add468d41-Paper-Conference.pdf).
- Raw reports under `artifacts/`, including the frozen Phase 5 manifest,
  shards, and confirmatory report.
