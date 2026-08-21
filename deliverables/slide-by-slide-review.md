# Slide-by-slide research review

Deck: `beyond-average-case-safety.pptx`

## Global assessment

The revised deck now makes one defensible argument: average-case evaluation is insufficient for multi-agent defense; a useful selector must consider conditional tail loss, non-overlapping failure sets, adaptive response, and operational utility. The deck does not claim that this selector has already won. It separates controlled harness validation, small online 7B mechanism canaries, and an offline sequential-monitoring study from the three confirmatory experiments that remain.

The new title, **Beyond Average-Case Safety**, is stronger than a method-first title because it states the problem and gives the audience a reason to care before introducing the proposed machinery.

## Per-slide review

| Slide | Role in the argument | Researcher/interviewer review | Evidence boundary retained in the revision |
|---:|---|---|---|
| 1 | Title and thesis | The title is memorable and problem-led; the subtitle makes collusion and covert coordination explicit. Author, project, and date are visible. | Makes no empirical claim. |
| 2 | Define the system-level failure | Establishes why component safety is not system safety: acceptable local actions can compose into prohibited outcomes. The trajectory diagram gives the evaluator a concrete unit of analysis. | Frames a threat model rather than claiming frequency in production. |
| 3 | Map Section 3.3 into the harness | Converts eight attack-variation dimensions into experimental axes and explains why pooled averages hide vulnerable cells. This directly answers the prompt's request to optimize specific dimensions. | The dimensions organize tests; they are not asserted to be exhaustive. |
| 4 | Separate attack mechanisms | Distinguishes covert coordination from heterogeneous/compositional system attacks and shows why one detector cannot cover both. | Lists registered mechanisms and carriers, not all possible covert channels. |
| 5 | State the proposal | Introduces worst-cell CVaR, a utility floor, failure diversity, and stack-aware response in one selection rule. The slide now uses readable notation and plain-language definitions. | Presents a selection conjecture, not a proven optimum. |
| 6 | Isolate the novelty | Separates established tools from the new falsifiable claim: validation failure geometry should predict realized held-out gain. This prevents novelty from resting on CVaR alone. | Calls the relationship a conjecture and names its falsifiers. |
| 7 | Show the common harness | Demonstrates that all five tests share manifests, paired seeds, trace schemas, and frozen gates. This is the key reproducibility slide. | A common contract does not imply identical causal estimands across experiments. |
| 8 | Disclose what actually ran | Answers where, which model, agent count, sample size, online/offline placement, and evidence tier. This should be spoken slowly because it calibrates every later conclusion. | Explicitly labels controlled fixtures, 7B canaries, and offline monitoring. |
| 9 | Explain attack induction and deployment | Shows how agents are made to coordinate or compose harmful workflows and where the defense sits relative to messages/actions. | Scaffolded attacks test registered mechanisms; they are not autonomous best responses. |
| 10 | Define outcome measurement | Connects attack success, mutual information, irreversible harm, utility, confidence intervals, tail bounds, and matched effects to the conjecture. | Statistical procedures quantify registered endpoints; small canaries remain imprecise. |
| 11 | Covert-channel result | Teaches the first new thing: paraphrasing can break a fixed code while failing against semantic adaptation; a typed mediator removes the registered capacity without utility loss. | 64 Qwen2.5-7B episodes; does not cover timing, tools, memory, or environmental channels. |
| 12 | Workflow-remediation result | Teaches the second new thing: local checks miss composition, hard blocking destroys utility, and provenance-aware repair can preserve the benign objective. | 24 episodes across six roles; mechanism demonstration, not a population estimate. |
| 13 | Sequential-monitoring result | Teaches the third new thing: lifetime false-alarm control and before-harm detection are different goals; low-rate attacks are the weak cell. | Frozen 560-episode test; monitors were offline and none demonstrated superiority. |
| 14 | Controlled-gate scorecard | Summarizes all five registered controlled questions while making the negative E01 and E04 results impossible to miss. | The footnote states that passing synthetic gates is not stochastic-agent robustness. |
| 15 | Complementarity result | Shows that diverse layers have non-overlapping failures, then separately reports the enforcement interaction gap. This prevents counterfactual complementarity from being mistaken for deployed performance. | The result is from controlled fixtures; model-backed shadow forks remain required. |
| 16 | Negative results | Makes scientific discipline visible: no selector contrast and no established transfer. This increases credibility more than hiding favorable diagnostics would. | Favorable secondary statistics cannot override failed primary gates. |
| 17 | Evidence ledger | Gives the audience a clean three-way distinction: established mechanism paths, bounded measurements, and open confirmatory claims. | Concludes “strong mechanism evidence; incomplete robustness evidence.” |
| 18 | Decision program | Ends with three experiments that can confirm or falsify the conjecture: model-backed complementarity, equal-budget best response, and held-out transfer. | Optimization is claimed only if the advantage survives all three. |

## Interviewer-facing strengths

- The deck answers the operational questions directly: execution environment, model revision, agent roles, attack induction, defense placement, data storage, and analysis.
- It contains three teachable findings rather than a list of conjectures.
- Negative results are preserved and determine the scope of the conclusion.
- The final slide converts limitations into a concrete research program.

## Remaining risks to anticipate in discussion

- The 7B canaries are small and scaffolded; they demonstrate pathways rather than general rates.
- Phase 5 monitoring is offline, so it cannot establish end-to-end intervention benefit.
- The strongest claim still needs LLM-generated matched shadow forks, autonomous stack-specific attack search, and a genuinely distinct held-out model family.
- The selector objective is meaningful only if the utility floor, attack-cell registry, and attacker budgets are defensible before the test set is opened.

