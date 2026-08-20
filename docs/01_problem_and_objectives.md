# Problem and Objectives

## 1. Motivation

Multi-agent AI systems create security failures that cannot be reduced to the safety of their individual components. Agents may communicate through natural language, tools, shared memory, retrieval systems, files, timing, or modifications to a shared environment. Harm can therefore emerge even when each local message or action appears acceptable.

Three motivating cases are especially important:

- **Collusion:** multiple agents coordinate on behavior that disadvantages users, operators, or other agents.
- **Steganography:** agents encode information in apparently legitimate communication, possibly with no statistical distinction between benign and covert messages.
- **Heterogeneous attacks:** agents with different capabilities or policies decompose a harmful task into locally acceptable subtasks and recombine the results.

The research problem is to design an open-weight evaluation harness that varies the structure of these attacks, exposes internal and external system signals, and evaluates defenses under realistic stochasticity and distribution shift.

## 2. Section 3.3 dimensions

The motivating paper identifies eight orthogonal dimensions of attack variation.

### 2.1 Detectability

Whether an attack produces an observable signal at any available layer. This ranges from obvious aggregate anomalies to information-theoretically undetectable message distributions.

Detectability is a feasibility boundary. If attacked and benign observations have identical distributions, no passive detector using only those observations can reliably distinguish them. The defender must observe another layer, intervene actively, restrict capacity, or contain consequences.

### 2.2 Locality

Where an attack manifests: one agent, a coalition, a shared component, or the entire interaction graph.

This dimension matters because heterogeneous attacks can be safe at every node but unsafe in composition. Per-agent certification is structurally inadequate for non-local failures.

### 2.3 Cascading

Whether a compromise propagates beyond its initial entry point. Propagation may occur through messages, shared memory, retrieval stores, delegated tasks, tool outputs, or environment state.

Cascade behavior determines whether monitoring alone is sufficient or whether the system also needs isolation, circuit breakers, topology changes, and memory remediation.

### 2.4 Multi-step composition

Whether harm requires a sequence of individually acceptable actions across agents, tools, or interfaces.

Composition is central to heterogeneous attacks and agentic intrusion. A per-call monitor can accept every step while the trajectory reaches a prohibited state.

### 2.5 Time horizon

Whether an attack acts immediately or unfolds across turns, sessions, memory updates, or deployments.

Long horizons make fixed-window evaluation unreliable. Stochastic benign behavior produces repeated opportunities for false alarms, while an attacker can distribute weak signals across time.

### 2.6 Attributability

Whether harm can be traced to an agent, coalition, input, model, or system component.

Attribution degrades across delegation and transformation. It requires identity, tamper-evident event history, and causal provenance rather than retrospective inspection of final outputs alone.

### 2.7 Directness

Whether harm results from an explicit malicious instruction or emerges from incentives and interaction dynamics without a clearly malicious participant.

Defenses that require known attacker intent fail on reward-induced collusion, adversarial equilibria, and accidental but systematic coordination failures.

### 2.8 Reversibility

Whether damage can be undone, only contained, or not meaningfully remediated.

Reversibility determines where the system needs hard authorization boundaries. Leaked information cannot be “unleaked”; a later explanation or attribution does not reverse an irreversible action.

## 3. Which dimensions should be prioritized

The project will represent all eight dimensions, but the first demonstrations should prioritize five.

1. **Detectability**, because it determines whether passive monitoring is possible at all.
2. **Multi-step composition**, because agent systems naturally distribute actions across models and tools.
3. **Locality**, because per-agent testing misses coalition-level failure.
4. **Time horizon**, because stochastic generation and optional stopping create a distinctive statistical problem.
5. **Reversibility**, because it determines whether detection latency is tolerable.

Cascading and attributability should be instrumented from the beginning because the event and provenance design must support them. Directness should be varied as an experimental condition: explicit adversarial prompting, reward-induced behavior, and benign emergent failure.

## 4. Research objective

The program will test whether a layered defense can reduce worst-case tail harm across Section 3.3 dimensions while preserving legitimate multi-agent utility.

The outer objective is:

\[
\min_D \max_{\theta \in \Theta_{3.3}}
\operatorname{CVaR}_q\!\left[L(D,\theta)\right]
\]

subject to:

\[
U(D) \ge U_0,
\qquad
P_0(\text{alarm at any time}) \le \alpha,
\qquad
C_{\mathrm{unauth}}(D) \le B.
\]

Here:

- \(D\) is a defense configuration;
- \(\theta\) is an attack configuration over the eight dimensions;
- \(L\) is security loss;
- \(U\) is legitimate task utility;
- \(C_{\mathrm{unauth}}\) is residual unauthorized channel capacity;
- CVaR emphasizes low-frequency, high-impact failures rather than average accuracy.

## 5. Research questions

### RQ1: Causal observability

Can changes in secret information be detected through their causal effects on receiver activations and actions when the message distribution itself is indistinguishable from benign communication?

### RQ2: Coalition-level safety

Can provenance-backed hyperproperties detect heterogeneous, multi-step attacks that every per-agent monitor accepts?

### RQ3: Stochastic long-horizon monitoring

Can sequential evidence processes provide a lifetime false-alarm guarantee while accumulating weak, distributed indications of collusion?

### RQ4: Active channel control

Can a mediator reduce unauthorized channel capacity below the amount required for coordination without destroying legitimate task utility?

### RQ5: Transfer

Which conclusions survive changes in model family, task, attack scheme, topology, horizon, and available observability?

## 6. Desired contributions

The project aims to contribute:

1. A common open-weight multi-agent security harness.
2. Operational parameterizations of the Section 3.3 dimensions.
3. Four falsifiable defense conjectures.
4. Paired counterfactual and coalition-level evaluation methods.
5. A shared event and provenance schema suitable for both experiments and deployment instrumentation.
6. Preliminary empirical evidence from reproducible 7–9B agent demonstrations.

## 7. Interpretation boundaries

A positive result on 7–9B agents demonstrates that a proposed signal or intervention can work under stated conditions. It does not prove that the same probe, layer, threshold, or mediator transfers directly to larger agents.

A negative result is even narrower. Failure of a 7–9B model to invent or use an attack does not imply that the attack is impossible for more capable agents. For this reason, strong attack tools may be supplied to the agents. The evaluated object is the defense against an LLM-directed attack, not merely the model’s unaided ability to rediscover cryptography.
