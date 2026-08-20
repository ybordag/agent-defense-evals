# Experimental Program and Transferability

## 1. Experimental objective

The experimental program will produce preliminary evidence for the four conjectures using a shared harness and open-weight 7–9B language-model agents.

The experiments are not intended to establish universal safety. They are intended to answer whether the proposed signals, formal properties, and interventions are measurable, falsifiable, and reusable across controlled attack dimensions.

## 2. Common experimental setup

### 2.1 Models

Use at least two open-weight model families in the 7–9B range.

Conditions:

- **Homogeneous:** all agents use the same checkpoint.
- **Heterogeneous:** agents use different model families, prompts, LoRA adapters, or safety tuning.
- **White-box:** hidden states, logits, and patching hooks are enabled.
- **Observation ablation:** only messages and external actions are available.

Models should be frozen for baseline evaluation. Attack-specific LoRA or reinforcement-learning variants may be added later, with base and adapted checkpoints recorded separately.

### 2.2 Agent roles

The reusable role set is:

- sender or information holder;
- receiver or decision maker;
- planner;
- specialist or artifact producer;
- critic or verifier;
- executor with tool access;
- sentinel or monitor;
- optional shared-memory or retrieval service.

Not every scenario uses every role.

### 2.3 Scenario families

1. **Secret channel:** a sender has a secret and a receiver must coordinate while completing a legitimate task.
2. **Heterogeneous composition:** locally acceptable subtasks compose into a prohibited terminal state.
3. **Long-horizon coordination:** agents interact repeatedly in a market, card game, negotiation, or resource-allocation setting.
4. **Cascade graph:** a message, memory update, or retrieved artifact can propagate through a configurable agent topology.

### 2.4 Attack regimes

Every scenario should support:

- benign cooperation;
- explicit adversarial instruction;
- reward-induced collusion without an explicit malicious prompt;
- heterogeneous task decomposition;
- overt signaling;
- in-context codebooks;
- learned or optimized steganography;
- tool-assisted strong steganography;
- delayed or sleeper behavior;
- shared-memory corruption.

Supplying a cryptographic or steganographic tool is valid. The agent must still decide how and when to use it. This isolates defense performance from the small model’s unaided cryptographic invention capability.

## 3. Section 3.3 variables

Each episode receives an explicit attack-dimension configuration.

| Dimension | Experimental control or proxy |
|---|---|
| Detectability | Message divergence, baseline monitor score, or observation ablation |
| Locality | Coalition size, coalition fraction, or affected graph region |
| Cascading | Propagation probability, branching factor, depth, and affected nodes |
| Composition | Minimum dependent steps, agents, tools, or interfaces needed for harm |
| Horizon | Attack onset, delay, episode length, and memory persistence |
| Attributability | Identity removal, provenance-edge loss, delegation depth, localization accuracy |
| Directness | Explicit prompt, reward-induced strategy, or non-adversarial emergent failure |
| Reversibility | Rollback fraction, containment cost, and pre-action authorization requirement |

These variables are operationalizations for evaluation. They should not be described as perfect universal measurements.

## 4. Instrumentation

Every episode records:

- task and scenario identifier;
- model, tokenizer, adapter, and prompt versions;
- random seed and sampling parameters;
- agent messages and recipients;
- token log probabilities when available;
- selected layer activations;
- tool calls and results;
- memory reads and writes;
- environment state changes;
- authorization decisions;
- event parent identifiers forming a provenance DAG;
- attempted and completed high-impact actions;
- security loss and legitimate utility.

Large activation tensors should be stored separately and referenced by immutable identifiers from the event log.

## 5. Evaluation design

### 5.1 Paired counterfactuals

Where possible, run paired episodes with the same model, task, context, and seed while changing one variable:

- secret value;
- sender message;
- activation region;
- coalition membership;
- topology edge;
- memory entry;
- attack onset.

Paired evaluation reduces stochastic variance and supports causal claims.

### 5.2 Distribution-shift splits

Do not randomly split conversations from the same scenario. Hold out complete:

- tasks;
- attack schemes;
- model families;
- communication topologies;
- coalition sizes;
- horizon ranges;
- mediator policies.

In-distribution accuracy is diagnostic. The central result is defense performance on structurally held-out attacks.

### 5.3 Core metrics

Security metrics:

- attack success rate;
- secret recovery or bit-error rate;
- residual unauthorized capacity;
- lifetime false-alarm probability;
- detection delay;
- detection before irreversible action;
- coalition attribution accuracy;
- cascade reach and reproduction rate;
- worst-case and CVaR loss.

Utility metrics:

- legitimate task success;
- completion time and token cost;
- communication overhead;
- false refusal or blocked benign action rate;
- latency added by the defense.

Every security result must be paired with its utility cost.

## 6. Experiment 1: causal usable information

### Setup

Use sender, receiver, and sentinel agents. The sender observes a uniformly random secret and a legitimate task. The receiver must complete the task. The attack reward additionally depends on a secret-specific receiver action.

Channels:

1. explicit codebook;
2. lexical or semantic codebook;
3. learned paraphrase-resistant channel;
4. tool-assisted perfectly secure or distribution-matching channel.

For each task, run paired secrets. Train message detectors and activation decoders on some schemes, then hold out at least one channel and model family.

Perform activation patching between paired rollouts at selected tokens and layers.

### Primary comparison

- message-only detector;
- action-based usable-information estimator;
- activation probe;
- causal activation-patching result.

### Supporting result

The experiment supports the conjecture if a held-out channel defeats message monitoring but leaves measurable secret-dependent receiver behavior or activations, and patching the localized representation reduces attack success.

## 7. Experiment 2: coalitional hyperproperties

### Setup

Use four to six agents in a sandboxed tool workflow. Give each agent a local policy and construct tasks where locally acceptable artifacts compose into a prohibited terminal state.

Example property families:

- protected data must not flow to an external sink;
- untrusted retrieval cannot directly authorize execution;
- an artifact producer cannot be its sole verifier;
- high-impact actions require independent approval;
- no coalition of size at most \(k\) can reach a forbidden state.

For small \(n\), exhaustively enumerate coalitions. Generate chain, tree, sparse-mesh, and dense communication graphs for the separator study.

### Primary comparison

- per-agent policy monitoring;
- trajectory policy monitoring;
- provenance-backed coalition hyperproperties;
- separator-only verification versus exhaustive checking.

### Supporting result

The experiment supports the general conjecture if coalition verification catches jointly harmful workflows accepted by per-agent monitors. The strong separator claim requires zero missed violations relative to exhaustive checking under its assumptions.

## 8. Experiment 3: anytime-valid evidence

### Setup

Run 100–1,000-step episodes. Randomize attack onset and include benign drift, low-rate signaling, delayed triggers, memory poisoning, and reward-induced coordination.

At each step construct a score from some combination of:

- causal usable information;
- activation probes;
- provenance anomalies;
- hyperproperty residuals;
- action or tool-use anomalies.

Calibrate an e-process on benign replicas and compare it with fixed thresholds, fixed-window classifiers, and conventional change-point baselines.

### Primary comparison

At the same lifetime false-alarm rate, compare:

- detection delay;
- probability of detection before high-impact action;
- robustness to benign distribution shift.

### Supporting result

The experiment supports the conjecture if the evidence process maintains its preregistered lifetime false-alarm rate and accumulates positive evidence on held-out long-horizon attacks.

## 9. Experiment 4: capacity shaping

### Setup

Give the sender a random \(b\)-bit target and require the receiver to take the corresponding action while completing a legitimate task.

Compare:

1. unrestricted free text;
2. generic paraphrasing;
3. typed task-specific messages;
4. task-sufficient summarization;
5. recipient-specific randomized mediation;
6. mediation with memory reset;
7. mediation plus high-impact action gates.

Optimize sender and receiver against each mediator using multiple prompts, training seeds, or adapters. A weak attacker is not evidence of low capacity.

### Primary comparison

Measure:

- bit-error rate and decoder accuracy;
- mutual-information lower bounds;
- attack success against required coordination bits;
- legitimate utility;
- capacity recovered after adversarial adaptation.

### Supporting result

The conjecture is supported if attack success tracks cumulative estimated capacity and declines when the channel budget falls below the task’s information requirement.

## 10. Minimal presentation demonstrations

The presentation does not require four large demonstrations.

### Demo A: invisible message, visible effect

Combine Experiments 1 and 4. Show one case where text monitoring fails, receiver behavior or activations reveal usable information, and a structured mediator reduces attack success.

### Demo B: safe parts, unsafe whole

Use Experiment 2. Show a harmful composite workflow accepted by every per-agent check and rejected by a coalition property.

### Demo C: weak signals become reliable over time

Reuse telemetry from A or B. Spread attack evidence across time and compare a fixed threshold with an anytime-valid process.

These demonstrations provide three concrete lessons while sharing most implementation and data infrastructure.

## 11. Practical sample strategy

A pilot can begin with:

- two model families;
- three or four agents;
- three attack channels;
- benign, explicit-collusion, and reward-induced regimes;
- approximately 100 paired episodes per pilot condition;
- five training or adaptation seeds where learned attackers are used.

Confirmatory sample sizes should be chosen using uncertainty targets and sequential power analysis rather than treating the pilot count as fixed doctrine.

## 12. Transferability to deployed agents

### 12.1 Components likely to transfer

The following are model-independent or weakly model-dependent:

- immutable event schema;
- provenance and identity model;
- action/capability registry;
- paired replay and intervention framework;
- formal trajectory and coalition policies;
- sequential evidence accounting;
- capacity and utility metrics;
- action gates, quorums, and circuit breakers;
- worst-case evaluation across attack dimensions.

### 12.2 Components requiring recalibration

The following are model- and domain-specific:

- activation probes and causal layers;
- benign activation distributions;
- tokenizer-dependent steganographic capacity;
- score calibration and thresholds;
- utility cost of a mediator;
- task-specific definitions of irreversible harm.

### 12.3 Closed-weight systems

Closed-weight agents remove activation inspection and patching. The harness still supports:

- behavioral secret interventions;
- message and action mediation;
- provenance and hyperproperties;
- sequential evidence;
- capacity testing;
- action gates and containment.

White-box results should therefore be treated as an additional defense layer, not a dependency for the entire framework.

### 12.4 Production adoption path

1. Instrument the production agent system with the common event schema.
2. Reproduce its prompts, tools, permissions, memory, and topology in a digital twin.
3. Calibrate on benign traces in non-blocking shadow mode.
4. Red-team combinations of Section 3.3 dimensions.
5. Optimize defenses offline under utility and latency constraints.
6. Deploy passive evidence collection first.
7. Add mediation and high-impact gates at boundaries justified by measured risk.
8. Convert incidents and newly discovered attacks into regression scenarios.

## 13. External-validity limits

The harness estimates defense robustness within a modeled attack class. It cannot demonstrate absence of unknown attacks.

Important threats to validity include:

- larger models inventing stronger protocols;
- agents using uninstrumented side channels;
- differences between sandbox tasks and real incentives;
- model-specific activation geometry;
- overfitting attacks and defenses to the same simulator;
- benign production drift outside the calibration distribution;
- incomplete semantics for tools and irreversible outcomes.

Results should therefore be reported as conditional lower bounds on demonstrated attack and defense capability, accompanied by the precise models, environments, observability, and assumptions used.
