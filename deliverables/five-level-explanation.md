# What we built and learned, at five levels

## 1. Like I am five

Imagine several helpful robots building something together. Each robot may do a safe-looking job, but their jobs can accidentally combine into something dangerous. Two robots might also pass secret messages.

We built a test playground with different kinds of guards. One guard changes messages, one only allows messages in safe boxes, and one fixes dangerous plans before they happen. We learned that no guard is best at everything. The safest team uses guards that make different mistakes, and we must test the hardest cases instead of only asking whether things are usually fine.

## 2. Teenager

An AI-agent team is like a group project in which members can chat, share documents, use tools, and take actions. A harmful result can emerge even when no single message looks obviously harmful. Agents can also hide coordination in wording, timing, memory, or tool use.

We built a common evaluation harness that varies how visible, distributed, delayed, and reversible an attack is. It compares defenses while checking that the agents still complete the real task. Our early experiments show three things:

1. Changing the wording defeats a simple secret code, but an attacker can switch to meaning-based codes; restricting communication to typed fields stopped the registered channel.
2. Checking every action separately can miss a harmful workflow; repairing the action using its provenance stopped the harmful composition without destroying the task.
3. A monitor can have very few false alarms and still react too late to slow, low-rate attacks.

We have evidence that these defense mechanisms work in the tested cases, but not yet that our full method is best across models and adaptive attackers.

## 3. Undergraduate

The central problem is distribution shift across multi-agent attack scenarios. An attack scenario specifies properties such as detectability, locality, cascade, composition, horizon, attribution, directness, and reversibility, plus model, prompt, topology, coalition, and carrier. A pooled average can look good while one conditional scenario has severe failures.

We propose selecting a layered defense under a utility constraint using worst-scenario tail loss rather than mean loss alone. Tail risk is measured by the worst 10% of outcomes in each scenario. Layer count is not enough: two layers are valuable only when they fail on different matched opportunities. We measure that non-overlap with a complementarity statistic, Gamma, and separately measure whether enforcing the layers together changes the trajectory in a harmful way.

The repository implements a shared contract for models, agents, attacks, defenses, traces, splits, seeds, and success gates. Evidence has three tiers:

- Controlled simulations validate estimators, split discipline, and failure geometry.
- Qwen2.5-7B canaries test covert-channel mediation and six-role workflow repair online.
- A 900-episode, 100-turn study evaluates three sequential monitors offline.

The strongest current outcomes are mechanism-level: Gamma was 0.406 in the controlled complementarity test; typed mediation reduced the registered adapted channel from 2 bits to 0 with exact utility retained; targeted workflow repair prevented the registered harm with exact utility retained; and low-rate before-harm detection was only 27.5%. Selector superiority and compound held-out transfer were not established.

## 4. Graduate student

Let a defense stack be pi, task utility be U(pi), latency be T(pi), and security loss in attack scenario g be L(pi,g). The selector minimizes an upper confidence bound on the worst-scenario, worst-decile conditional loss, subject to a minimum utility floor and operational constraints. The attacker is represented by a stack-aware response BR(pi,g), so robustness must be evaluated after re-optimization against each finalist stack.

Risk sensitivity alone can select redundant layers. For singleton bypass events F_A and F_B, we therefore estimate

Gamma(A,B) = min(P(F_A), P(F_B)) - P(F_A intersect F_B).

Positive Gamma means the two failure sets are non-nested. Because actual enforcement alters future states, we also estimate an interaction gap between the realized stack bypass rate and the matched singleton intersection. The strong hypothesis is that validation Gamma predicts held-out realized tail gain beyond component quality, utility, and latency, provided the advantage survives equal-budget adaptive search and consequential deployment.

The experiments use immutable manifests, paired seeds, frozen validation/test boundaries, trace hashing, Wilson intervals for binomial endpoints, empirical worst-decile Conditional Value at Risk (CVaR) with DKW upper bounds, paired Hoeffding lower bounds, bootstrap delay intervals, and pre-specified compound gates. The controlled suite produces useful evidence for complementarity and before-harm intervention, but E01 has no selector contrast and E04 fails its compound gate. The online 7B canaries validate mediation and repair paths with small samples. The monitoring study controls the registered benign lifetime-alarm rate but exposes a low-rate detection deficit.

The correct conclusion is not “the conjecture is confirmed.” It is that the estimands and online defense paths are executable, several mechanisms are promising, and three decisive confirmatory experiments are now precisely specified.

## 5. PhD or professor

The proposed contribution is a falsifiable conjunction, not a new tail-risk functional. Existing CVaR, worst-group optimization, confidence sequences, and steganographic channel measures are necessary but individually insufficient for multi-agent defense selection. The additional variable is validation-time common-mode failure geometry under matched opportunities, coupled to an explicit deployment-interaction estimand and an adaptive game.

The target claim is:

> Among utility- and cost-matched defense stacks, validation complementarity predicts held-out realized conditional-tail gain beyond singleton quality, but only when the advantage persists under equal-budget stack-aware best response, bounded enforcement interaction, and frozen single-axis plus compound transfer tests.

This suggests three causal/experimental requirements. First, model-backed shadow forks should expose the same pre-defense LLM-generated event to each singleton and the enforced stack, making joint bypass and interaction identifiable on matched opportunities. Second, adaptive evaluation must be diagonal: independently optimize an attacker against each stack on validation seeds under identical budgets, freeze the search procedure, and test only its corresponding stack on fresh seeds. Third, transfer must use a truly distinct model family and sufficiently many candidate stacks to estimate whether Gamma contributes predictive value after controlling for singleton robustness, utility, latency, and attack-scenario difficulty.

The present data do not identify that full claim. Controlled fixtures show Gamma = 0.406 and a realized gain of 0.381, with a positive 0.025 interaction gap. Small Qwen2.5-7B canaries show carrier adaptation and utility-preserving typed mediation/repair. The sequential study shows that registered lifetime type-I control can coexist with 27.5% low-rate before-harm detection. These observations motivate the conjecture and validate measurement paths; they do not establish cross-model robustness, autonomous best-response resistance, or selector advantage.

The conjecture would be falsified by any of the following: complementarity collapsing on LLM-generated matched forks; stack-specific attack search erasing the tail advantage; harmful enforcement interaction; no selector contrast against registered baselines; or validation Gamma failing to predict compound held-out gain. That falsifiability, and the strict separation of mechanism evidence from robustness evidence, is the scientific value of the current work.
