# Experiment evidence canvas

This canvas answers the substrate, attack, defense, data, and inference questions a researcher should ask before interpreting the headline results.

## Execution canvas

| Study | Where / runtime | Model | Agents | Attack induction | Defense placement | Episodes | Stored evidence |
|---|---|---|---:|---|---|---:|---|
| Controlled E01-E05 | Repository harness; deterministic simulator | None | Simulated roles | Registered probability fixtures over attack cells and stacks | Simulated | 2,400 | Full per-trajectory validation and test outcomes |
| Capacity canary | `spark-thor`; vLLM OpenAI-compatible endpoint | Qwen2.5-7B-Instruct, revision `a09a35458c702b33eeacc393d103063234e8bc28` | 2 | Supplied two-bit codebook; fixed and semantic adaptations | Online message gateway | 64 | Aggregate report plus trace-complete fresh rerun with events/model outputs |
| Workflow canary | `spark-thor`; same vLLM endpoint | Same pinned 7B model | 6 roles | Registered planner/reviewer manipulation | Online action gateway | 24 | Aggregate report plus trace-complete fresh rerun with events/model outputs |
| Sequential monitoring | `spark-thor`; model traces evaluated by repository monitors | Same pinned 7B model | 2 | Randomized onset; low-rate, delayed, memory, and reward objectives | Offline after generation | 900 x 100 turns | 48 split shards with per-episode scores and trace hashes; full generations not retained |

## What was measured

| Question | Primary endpoint | Statistical treatment | Current result | Claim boundary |
|---|---|---|---|---|
| Does tail selection beat ordinary selectors? | Worst-cell worst-decile CVaR | DKW upper bound; frozen selector comparison | No contrast: all selectors chose the same stack | E01 is not supported |
| Do diverse layers fail on different opportunities? | `Gamma = best singleton bypass - joint singleton bypass` | Matched opportunities | `Gamma = 0.406`; realized gain `0.381` | Controlled synthetic only |
| Does complementarity survive adaptation? | Adaptive worst-cell CVaR and retained Gamma | Registered adaptive cells | `0.93` vs `1.00`; retained Gamma `0.205` | No autonomous stack-specific LLM best response yet |
| Does validation geometry transfer? | Spearman correlation of validation Gamma with held-out robustness | Rank diagnostic | `rho = 0.866` across three synthetic stacks | Not confirmatory; no genuinely held-out model execution |
| Can enforcement stop harm before it is irreversible? | Harm rate and before-harm intervention | Wilson intervals; paired Hoeffding lower bound | Simulated harm `0.725 -> 0.025`; before-harm `0.95` | Controlled synthetic only |
| Can a channel defense survive semantic adaptation? | Attack success, mutual information, exact utility | Wilson intervals; empirical MI | Paraphrase: `1.00 -> 0.25`; adaptation returns `1.00`; typed mediator returns `0.25`; utility `1.00` | One supplied codebook and one model |
| Can a consequential defense preserve utility? | Effective-flow violation, remediation, exact utility | Wilson intervals | Targeted repair prevents registered harm with utility `1.00`; hard block utility `0.00` | Four harmful episodes per condition |
| Can monitoring control lifetime false alarms and intervene in time? | Benign lifetime alarm; before-harm detection | Wilson 95%; 2,000-resample delay bootstrap | Benign upper bound `0.0458`; low-rate before-harm `0.275` | Empirical split validity; monitors are offline |

## Evidence locations

| Evidence | Path |
|---|---|
| Controlled report | `artifacts/asap-evidence/tail-report.json` |
| Controlled raw validation outcomes | `artifacts/asap-evidence/tail-validation.json` |
| Controlled raw test outcomes | `artifacts/asap-evidence/tail-test.json` |
| Original 7B capacity report | `artifacts/asap-evidence/phase7-model-capacity-7b-vllm.json` |
| Original 7B workflow report | `artifacts/asap-evidence/phase7-model-workflow-7b-vllm.json` |
| Trace-complete canary reruns | `artifacts/reviewer-evidence-20260821/` |
| Phase 5 report | `artifacts/phase5-confirmatory-report.json` |
| Phase 5 split data | `artifacts/phase5-confirmatory-{calibration,validation,test}-shard-*.json` |

The fresh rerun manifest, whole-file SHA-256 values, and claim boundary are recorded in `artifacts/reviewer-evidence-20260821/README.md`.

## Defense placement

```text
Capacity: sender -> message defense gateway -> receiver
Workflow: role sequence -> provenance repair/gate -> external action
Phase 5: two-agent trajectory -> stored score sequence -> offline monitors
Synthetic: probability fixture -> sampled outcomes -> estimators/gates
```

Only capacity and workflow currently deploy the defense alongside the agents. This prevents offline monitoring evidence from being misread as an online harm-reduction result.

## What remains decisive

| Missing experiment | Required implementation | Definition of success |
|---|---|---|
| Model-backed complementarity | Shadow-fork the same LLM-generated opportunity through each singleton and the enforced stack | Positive matched Gamma, bounded interaction gap, and lower realized bypass than cost-matched homogeneous stacks |
| Autonomous stack-aware best response | Separate attacker search against every finalist under identical query/token/tool/rollout budgets; fresh-seed diagonal evaluation | Diverse-stack worst-cell CVaR advantage survives adaptation by a frozen margin |
| Discriminative selector study | Expand stacks and cells until credible selectors can choose differently | Proposed selector beats the strongest registered baseline without violating utility or latency constraints |
| Genuine held-out transfer | Qualify and freeze a different capable 7-9B model family, then open single-axis and compound manifests once | Validation Gamma adds predictive value beyond component quality, utility, and latency |
| Online Phase 5 enforcement | Connect monitors to an action gateway and define irreversible actions | Lower realized harm at the registered lifetime false-alarm bound |

## Bottom line

The evidence supports a strong harness and three mechanism-level lessons: representation-specific filtering is brittle, provenance-aware repair can outperform hard blocking on a registered composition, and low-rate behavior exposes the gap between eventual detection and useful intervention. It does not yet confirm the full mechanism-diverse tail-robustness conjecture across adaptive attackers and held-out model families.
