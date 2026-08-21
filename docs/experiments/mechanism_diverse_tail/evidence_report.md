# Mechanism-Diverse Tail Robustness: Evidence Report

## Executive verdict

This report evaluates the bounded conjecture that mechanism-diverse defense
stacks, selected using utility-constrained worst-cell tail risk, can reduce
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
| E01 selector comparison | Controlled fixture rerun; new trajectory suite pending | 3 stacks × 9 aggregate fixture cases | Validation-only selector chooses the layered stack; fixture test CVaR is 0.39 versus 0.84 and 0.94 for baselines | Implementation-only until trajectory selector tournament completes |
| E02 failure complementarity | Structural and mediator precursors; matched-fork run pending | 41 coalitions × 4 scripted topologies; 64 model-backed channel episodes | Provenance/action gating and typed mediation block different registered mechanisms | Complementarity not yet estimated |
| E03 adaptive best response | Controlled adaptive search plus 7B registered-codebook canary | 1,024 controlled observations per mediator/mode; 64 Qwen2.5-7B episodes | Adaptive semantics bypass generic paraphrase (0.25 → 1.00); typed mediation holds attack success at 0.25 | Model-backed manipulation check, not autonomous best-response evidence |
| E04 compound held-out transfer | Structural holdout accounting only | 6 hand-authored test cases | Transfer accounting works, but cases are not model-generated | Blocked on a qualified held-out 7–9B model family and executed compound cells |
| E05 irreversibility and sequential validity | Frozen held-out Phase 5 evidence plus 7B workflow precursor | 900 Qwen2.5-7B sequential episodes; 24 direct-Transformers workflow episodes | Lifetime false-alarm gate passes; attack before-harm rates range from 0.275 to 1.00; targeted repair blocks registered harm with utility 1.00 | Sequential-validity precursor; end-to-end diverse enforcement remains unconfirmed |

## Conjecture and primary estimands

For stack \(\pi\), attack cell \(g\), stack-aware attacker \(a\), and stochastic
trajectory \(\omega\), the proposed selector minimizes an uncertainty-adjusted
worst-cell upper-tail loss subject to operational constraints:

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

The existing direct-Transformers Qwen2.5-7B workflow run contains four episodes
per condition. The registered harmful workflow succeeds under no defense and
local-only checks. Hard blocking prevents the harm but reduces exact utility to
zero. Targeted provenance repair prevents the harm while preserving exact
utility at 1.00. The sample is too small for a general effect claim, but it
validates the end-to-end remediation path.

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
