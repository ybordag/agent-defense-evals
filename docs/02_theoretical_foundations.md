# Theoretical Foundations

## 1. Why existing defenses are insufficient individually

Relevant defenses fall into ten families:

1. message-level steganalysis;
2. paraphrasing and channel normalization;
3. downstream behavioral or utility comparison;
4. white-box activation probes;
5. distributed tracing and provenance graphs;
6. temporal-logic runtime verification;
7. information-flow control and taint tracking;
8. least privilege, capability gates, and zero trust;
9. counterfactual interventions and randomized canaries;
10. quorums, circuit breakers, isolation, and rollback.

These mechanisms operate at different layers. Message detectors attempt to recognize attacks. Information-flow and formal controls prevent disallowed transitions. Provenance supports correlation and attribution. Capacity controls change what communication can carry. Circuit breakers limit harm after evidence crosses a threshold.

No single family handles the difficult corner described in Section 3.3: low detectability, non-local execution, multi-step composition, long horizon, weak attribution, and irreversible consequences.

## 2. Information-theoretic steganography

Classical steganographic security treats detection as a hypothesis test between a benign cover distribution and a stegotext distribution. Relative entropy, usually KL divergence, measures the statistical distinction available to the observer.

If:

\[
P_{\mathrm{cover}}(M)=P_{\mathrm{stego}}(M),
\]

then no passive monitor observing only \(M\) can distinguish the two distributions better than chance under the model assumptions.

Perfectly secure steganography using minimum-entropy coupling demonstrates that nontrivial information can be embedded while preserving an arbitrary cover distribution. This creates a hard limit for natural-language monitoring: “better classification” is not a complete response to a channel with zero statistical divergence.

The defensive consequences are:

- observe downstream behavior rather than only the signal;
- introduce controlled interventions;
- constrain the channel’s usable capacity;
- require independent authorization for irreversible effects.

## 3. Usable information and behavioral asymmetry

Mutual information describes statistical dependence but does not necessarily describe what a bounded agent can extract. Generalized usable-information frameworks restrict the decoder to a model class \(\mathcal V\).

The decision-theoretic steganographic gap asks whether a receiver obtains more task-relevant value from a signal than a sentinel can obtain. It shifts the focus from whether text looks suspicious to whether hidden information changes what an informed receiver can do.

The project extends this idea in two ways:

1. **Causal intervention:** vary the private variable while holding legitimate context fixed.
2. **White-box localization:** intervene on internal receiver states to test whether an activation region mediates the secret-dependent behavior.

This does not defeat information-theoretic undetectability at the message layer. It changes the observable layer from the message distribution to the consequences of the message within a receiver and environment.

## 4. Noninterference and hyperproperties

Many security requirements cannot be expressed as properties of one execution trace. Noninterference asks whether changing a secret input changes a public observation. It inherently compares executions.

Hyperproperties generalize ordinary trace properties to properties of sets of traces. They can express statements such as:

- two executions differing only in protected information must produce equivalent public behavior;
- no coalition below a threshold can reach a prohibited system state;
- an artifact creator and verifier must be independent across all valid trajectories.

This is a natural fit for multi-agent security. Each agent may satisfy its local policy, while the joint trace violates a coalition-level property.

## 5. Provenance and distributed intrusion detection

Microservice intrusion detection provides a useful systems analogy. Individual requests or logs can look benign while a long-range dependency graph reveals an intrusion. Provenance records how processes, data, messages, tools, and actions depend on one another.

For agent systems, provenance should include:

- agent identity and model configuration;
- message and delegation ancestry;
- memory reads and writes;
- retrieval inputs and returned artifacts;
- tool invocations and results;
- authorization decisions;
- environment state transitions;
- high-impact action attempts.

Provenance supports three project needs:

1. evaluating non-local and composed attacks;
2. identifying candidate responsible coalitions;
3. replaying and intervening on causal paths.

Provenance is not automatically complete. Unlogged side channels, timing, shared pretrained knowledge, physical effects, or external systems can violate its assumptions. Completeness of mediation must therefore be an explicit condition, not an implicit claim.

## 6. Sequential evidence and stochastic agents

LLM agents are stochastic, adaptive, and potentially long-lived. A per-turn detector with false-positive probability \(p\) can produce an unacceptable lifetime false-alarm probability after enough turns. Repeatedly inspecting an ordinary fixed-sample statistic also invalidates its nominal significance level.

An e-process is a nonnegative evidence process constructed so that, under the null:

\[
P_0\left(\sup_t E_t \ge 1/\alpha\right) \le \alpha.
\]

This provides validity under optional stopping: the operator may inspect continuously and stop when evidence is sufficient without inflating the lifetime false-alarm guarantee, provided the conditional calibration assumptions hold.

The project’s novel empirical question is not whether e-process theory is valid. It is whether coalition-level causal, activation, and provenance scores retain positive evidence drift across attacks and distribution shifts.

If they do, weak evidence can accumulate safely. If attacked and benign processes are identical on every measured feature and consequence, no sequential statistic can help.

## 7. Channel capacity and active mediation

Detection asks whether communication is suspicious. Capacity shaping asks how much unauthorized information a receiver can recover through the permitted channel.

Let a mediator \(K_r\), possibly randomized by a defender-controlled seed \(r\), transform a sender message before delivery. Define residual capacity conceptually as:

\[
C_{\mathrm{unauth}}
=
\sup_{\text{sender, receiver}}
I(S;\hat S\mid K_r).
\]

The supremum matters. Measuring one weak attacker is not evidence that the channel has low capacity. Sender and receiver must be optimized adversarially against the mediator using multiple seeds and restarts.

Capacity can be reduced through:

- typed task-specific protocols;
- least-information summaries;
- recipient-specific transformations;
- channel rate limits;
- memory reset or compartmentalization;
- removing unnecessary shared state;
- independent authorization at consequential sinks.

Generic paraphrasing is a baseline, not a guarantee. Semantic, syntactic, timing, and tool-mediated channels may survive paraphrase.

## 8. Formal guarantees versus empirical evidence

The project combines three kinds of claims.

### Mathematical guarantees

Examples include the impossibility of passive discrimination under identical observation distributions and lifetime error control for a correctly calibrated evidence process.

### Conditional systems guarantees

Examples include noninterference or coalition properties under complete mediation, authenticated identity, faithful logging, and specified environment semantics.

### Empirical generalization claims

Examples include whether a probe transfers to a new model family, whether a mediator withstands adaptive attackers, or whether causal scores exhibit positive drift under distribution shift.

The documentation and experiments must label these separately. Empirical success must not be presented as an unconditional theorem, and a theorem’s assumptions must not be treated as automatically satisfied by the implementation.
