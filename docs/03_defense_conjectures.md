# Defense Conjectures

## 1. Coverage summary

In the table below, **P** means the conjecture directly operationalizes or controls the dimension. **S** means the dimension can be varied or measured, but the mechanism does not by itself solve it. A dash indicates that the dimension is outside the primary scope.

| Conjecture | Detectability | Locality | Cascading | Composition | Horizon | Attribution | Directness | Reversibility |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. Causal usable information | P | P | S | P | S | P | S | — |
| 2. Coalitional hyperproperties | S | P | P | P | P | P | P | P |
| 3. Anytime-valid evidence | P | S | S | P | P | S | P | S |
| 4. Capacity shaping | P | S | P | P | P | — | — | S |

## 2. Conjecture 1: causal usable-information monitoring

### Statement

Steganographic communication that is statistically undetectable at the message layer can still be measured when the defender evaluates its causal effect on receiver internal state and downstream behavior.

Let:

- \(S\) be protected or unauthorized information;
- \(X\) be legitimate task context;
- \(A_C\) be the actions of a receiver or coalition \(C\);
- \(I_{\mathcal V}\) be information usable by a specified decoder class.

Define unauthorized usable flow:

\[
\Phi_C = I_{\mathcal V}(S;A_C\mid X).
\]

The causal null is:

\[
H_0:
P(A_C\mid do(S=s),X)
=
P(A_C\mid do(S=s'),X).
\]

The alternative is that changing \(S\), while holding authorized inputs fixed, systematically changes receiver behavior or a causally relevant internal representation.

### Why it may be true

A perfectly secure stegosystem can match the benign message distribution, but useful collusion must affect a receiver or environment. Open weights permit the harness to inspect and patch activations associated with that use.

### Testable predictions

1. Message-only detection can remain at chance while secret information is decodable from receiver activations or actions.
2. Activation patching between paired secret interventions reduces secret-dependent behavior.
3. Causal or behavioral features transfer better than text signatures to a held-out encoding scheme.

### Assumptions

- The secret can be varied experimentally.
- The receiver’s consequential behavior is observable.
- The experiment can control or pair relevant context and randomness.
- White-box claims require access to the receiver weights and activations.

### Falsification

The conjecture is falsified in the tested setting if collusion succeeds but controlled secret interventions produce no measurable change in any captured receiver state, action, or environment consequence.

### Boundary

The conjecture does not address harmful coordination that needs no varying private information—for example, agents following a pre-coordinated policy derived from shared training.

## 3. Conjecture 2: multi-agent safety is a coalitional hyperproperty

### Statement

Safety of individual agent traces does not imply safety of their composition. Multi-agent safety must be expressed over coalitions and counterfactual sets of execution traces.

A representative property is:

\[
\forall C,\ |C|\le k,\quad
\tau \equiv_{\text{authorized inputs}} \tau'
\Rightarrow
\operatorname{Obs}_{\bar C}(\tau)
=
\operatorname{Obs}_{\bar C}(\tau').
\]

This requires executions differing only in unauthorized inputs available to coalition \(C\) to remain equivalent at protected outputs.

### Strong bounded-separator form

Under complete mediation, faithful provenance, a Markov factorization over the provenance graph, and bounded graph treewidth \(w\), verifying relevant noninterference properties across minimal separators of size at most \(w+1\) may be sufficient to bound global coalition information flow.

This stronger form is intentionally conjectural. Its value is that it offers a path from exponential coalition enumeration to graph-structured verification.

### Why it may be true

Heterogeneous attacks exploit dependencies between individually acceptable artifacts. Provenance captures those dependencies, and hyperproperties express the comparison across executions that ordinary per-trace policies cannot.

### Testable predictions

1. Per-agent monitors accept a meaningful fraction of jointly harmful workflows.
2. Coalition-level provenance properties detect those workflows before the prohibited terminal action.
3. On sparse graphs satisfying the assumptions, separator verification matches exhaustive coalition checking with fewer checks.

### Assumptions

- Relevant communication and state changes are mediated and logged.
- Agent and artifact identities are stable.
- Environment transitions have well-defined security semantics.
- The separator claim additionally requires the graph-factorization assumptions.

### Falsification

The general conjecture is weakened if per-agent properties suffice across the heterogeneous benchmark. The strong separator form is falsified by one missed violation relative to exhaustive enumeration under all stated assumptions.

### Boundary

Unobserved side channels, dense shared state, or incorrect provenance edges can invalidate the verification argument.

## 4. Conjecture 3: anytime-valid coalition evidence

### Statement

Long-horizon collusion among stochastic agents is better monitored through an anytime-valid evidence process than through fixed per-turn or fixed-window thresholds.

Let \(z_t\) be a stepwise coalition score constructed from activations, causal effects, provenance, actions, or hyperproperty residuals. An idealized evidence process is:

\[
E_T
=
\prod_{t=1}^{T}
\frac{p_1(z_t\mid z_{<t})}
     {p_0(z_t\mid z_{<t})}.
\]

Under a calibrated benign null:

\[
P_0\left(\sup_T E_T\ge 1/\alpha\right)\le\alpha.
\]

The empirical conjecture is that coalition-level scores exhibit positive log-evidence drift under attacks, including attacks that distribute weak signals across time.

### Why it may be true

Collusion may create small conditional deviations that are individually inconclusive but persistent. Sequential evidence can accumulate those deviations while controlling the probability of ever producing a false alarm.

### Testable predictions

1. Fixed per-turn thresholds either accumulate false alarms or require thresholds that miss slow attacks.
2. The evidence process maintains its preregistered lifetime false-alarm rate under optional stopping.
3. On attack episodes, the evidence crosses threshold before irreversible harm more often than baselines at the same lifetime error level.

### Assumptions

- The null evidence increments are conditionally calibrated.
- Benign distribution shift is represented or detected sufficiently to preserve calibration.
- Attacks change at least one measured conditional distribution or consequence.

### Falsification

The conjecture fails if causally effective attack episodes have no positive evidence drift on held-out conditions or if benign drift invalidates lifetime error control.

### Boundary

Sequential testing cannot extract evidence from observations whose attacked and benign conditional distributions are identical.

## 5. Conjecture 4: unauthorized-capacity shaping

### Statement

When covert communication may be undetectable, the appropriate control target is unauthorized channel capacity rather than message classification.

Let a mediator \(K_r\) transform communication, potentially using a defender-controlled random seed. Define residual capacity:

\[
C_{\mathrm{unauth}}
=
\sup_{\text{sender, receiver}}
I(S;\hat S\mid K_r).
\]

If an attack requires \(b\) bits of runtime coordination and the cumulative capacity over horizon \(T\) satisfies:

\[
T C_{\mathrm{unauth}} < b,
\]

then attack success should be bounded and should decline as the capacity deficit increases.

### Why it may be true

Communication-dependent coordination requires information transfer. A task-specific mediator, rate budget, compartmentalized memory, and consequential-action gate can reduce the communication available for unauthorized purposes.

### Testable predictions

1. Attack success tracks estimated cumulative capacity more consistently than message anomaly scores.
2. Generic paraphrasing leaves substantial residual capacity for some schemes.
3. Typed or task-sufficient mediation reduces capacity more strongly, although at a measurable utility cost.
4. Attack success declines when the residual budget falls below the task’s coordination requirement.

### Assumptions

- The attack needs runtime information exchange.
- The capacity estimator is challenged by optimized senders and receivers.
- Unmediated side channels are absent or separately measured.
- The legitimate task admits a lower-information protocol.

### Falsification

The conjecture is weakened if attack success remains high at near-zero measured capacity, if adaptive attackers consistently recover capacity, or if useful task performance collapses before security improves.

### Boundary

Pre-coordinated behavior, shared pretrained knowledge, or environmental Schelling points may enable harmful coordination with negligible runtime information transfer.

## 6. Relationship among the conjectures

The conjectures are complementary rather than competing.

1. Causal usable information supplies a coalition-level signal that can survive message-level undetectability.
2. Hyperproperties place that signal in a formal execution and provenance context.
3. Anytime-valid evidence accumulates weak signals across stochastic, long-horizon episodes.
4. Capacity shaping and action gates intervene where evidence is insufficient or consequences are irreversible.

The combined defense is therefore layered:

\[
\text{observe} \rightarrow
\text{verify} \rightarrow
\text{accumulate evidence} \rightarrow
\text{mediate or contain}.
\]
