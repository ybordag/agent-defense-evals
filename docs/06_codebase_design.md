# Codebase Design

## 1. Design principles

1. **Start independent of any existing code.** The initial package should be self-contained.
2. **Event sourcing first.** Every experiment depends on consistent traces and provenance.
3. **Interfaces before frameworks.** Model runtimes, scenarios, attacks, and defenses must be replaceable.
4. **Configuration is data.** An experiment must be reconstructable from a resolved configuration and seeds.
5. **Paired interventions are native.** Counterfactual execution is a core runner feature.
6. **Security and utility are co-equal outputs.** No defense result is complete without task impact.
7. **Online and offline analysis are distinct.** Runtime feasibility must not be confused with retrospective research analysis.

## 2. Proposed repository layout

```text
agent-defense-evals/
├── pyproject.toml
├── README.md
├── configs/
│   ├── models/
│   ├── scenarios/
│   ├── attacks/
│   ├── defenses/
│   └── experiments/
├── src/agent_defense_evals/
│   ├── core/
│   │   ├── events.py
│   │   ├── specifications.py
│   │   ├── trace.py
│   │   └── runner.py
│   ├── models/
│   │   ├── base.py
│   │   └── local_transformer.py
│   ├── agents/
│   │   ├── base.py
│   │   ├── roles.py
│   │   └── prompting.py
│   ├── orchestration/
│   │   ├── scheduler.py
│   │   ├── topology.py
│   │   └── gateway.py
│   ├── scenarios/
│   │   ├── base.py
│   │   ├── secret_channel.py
│   │   ├── heterogeneous_composition.py
│   │   ├── long_horizon.py
│   │   └── cascade_graph.py
│   ├── attacks/
│   │   ├── base.py
│   │   ├── codebook.py
│   │   ├── steganography.py
│   │   ├── heterogeneous.py
│   │   └── sleeper.py
│   ├── defenses/
│   │   ├── base.py
│   │   ├── causal_information.py
│   │   ├── hyperproperties.py
│   │   ├── sequential_evidence.py
│   │   ├── mediation.py
│   │   └── action_gates.py
│   ├── instrumentation/
│   │   ├── activations.py
│   │   ├── provenance.py
│   │   ├── telemetry.py
│   │   └── storage.py
│   ├── interventions/
│   │   ├── base.py
│   │   ├── secret_swap.py
│   │   ├── activation_patch.py
│   │   ├── message_replace.py
│   │   ├── memory.py
│   │   └── topology.py
│   └── evaluation/
│       ├── dimensions.py
│       ├── metrics.py
│       ├── statistics.py
│       ├── splits.py
│       └── optimizer.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── properties/
│   └── fixtures/
├── demos/
│   ├── invisible_message_visible_effect.py
│   ├── safe_parts_unsafe_whole.py
│   └── weak_signals_over_time.py
└── artifacts/
    ├── traces/
    ├── activations/
    ├── metrics/
    └── reports/
```

Generated artifacts should be excluded from version control except for small, intentional fixtures and report summaries.

## 3. Core data types

### 3.1 Event

```python
@dataclass(frozen=True)
class Event:
    event_id: str
    episode_id: str
    step: int
    logical_time: int
    actor_id: str
    recipient_ids: tuple[str, ...]
    kind: EventKind
    parent_ids: tuple[str, ...]
    payload_ref: str
    policy_labels: tuple[str, ...]
    risk_level: float
    reversible: bool
    activation_ref: str | None
```

Events should be append-only after creation. Corrections become new events rather than mutations.

### 3.2 Attack dimensions

```python
@dataclass(frozen=True)
class AttackDimensions:
    detectability_target: float | None
    coalition_size: int
    cascade_branching: float
    composition_depth: int
    horizon: int
    attribution_degradation: float
    directness: Directness
    reversibility: float
```

The type records experimental proxies. It does not assert that the values are universal measures.

### 3.3 Experiment specification

```python
@dataclass(frozen=True)
class ExperimentSpec:
    experiment_id: str
    model_specs: tuple[ModelSpec, ...]
    agents: tuple[AgentSpec, ...]
    scenario: ScenarioSpec
    attack: AttackSpec
    defenses: tuple[DefenseSpec, ...]
    dimensions: AttackDimensions
    capture: CaptureSpec
    interventions: tuple[InterventionSpec, ...]
    seed: int
```

The resolved spec should include defaults so it is sufficient for reproduction.

## 4. Primary interfaces

### 4.1 Model runtime

```python
class ModelRuntime(Protocol):
    def generate(
        self,
        request: GenerationRequest,
        capture: CaptureSpec,
    ) -> GenerationResult: ...

    def patch(
        self,
        patch: ActivationPatch,
    ) -> ContextManager[None]: ...
```

### 4.2 Agent policy

```python
class AgentPolicy(Protocol):
    def act(
        self,
        observation: Observation,
        state: AgentState,
    ) -> AgentAction: ...
```

Agent roles should be configuration and policy composition, not separate orchestration implementations.

### 4.3 Scenario

```python
class Scenario(Protocol):
    def reset(self, seed: int) -> ScenarioState: ...
    def observe(self, agent_id: str) -> Observation: ...
    def apply(self, actions: Sequence[AgentAction]) -> StepResult: ...
    def security_outcome(self) -> SecurityOutcome: ...
    def utility_outcome(self) -> UtilityOutcome: ...
```

### 4.4 Defense

```python
class Defense(Protocol):
    def before_event(
        self,
        proposed: ProposedEvent,
        context: DefenseContext,
    ) -> DefenseDecision: ...

    def after_event(
        self,
        event: Event,
        context: DefenseContext,
    ) -> Sequence[DefenseSignal]: ...
```

`DefenseDecision` supports allow, transform, delay, require approval, quarantine, block, and terminate.

### 4.5 Intervention

```python
class Intervention(Protocol):
    def applies(self, context: RunContext) -> bool: ...
    def apply(self, state: RunState) -> InterventionRecord: ...
```

Interventions must record targets and preserve a link to the source episode when values are patched across runs.

## 5. Runner behavior

The runner executes one resolved specification.

```python
def run_episode(spec: ExperimentSpec) -> EpisodeResult:
    state = initialize(spec)
    while not state.terminal:
        observations = state.scenario.observations()
        proposed_actions = state.agents.act(observations)
        decisions = state.gateway.evaluate(proposed_actions)
        step_result = state.scenario.apply(decisions.allowed_actions)
        state.event_store.append(step_result.events)
        state.online_analyses.update(step_result.events)
        state = state.advance(step_result)
    return finalize(state)
```

The actual implementation should make event creation explicit around every agent, gateway, tool, and environment transition.

## 6. Paired-run API

```python
pair = run_counterfactual_pair(
    base_spec=spec,
    intervention=SecretSwap(target="sender.secret", value=new_secret),
    invariants=[SameTask(), SameModels(), SameSamplingConfiguration()],
)
```

The paired-run result should include:

- invariant validation;
- aligned event sequences;
- divergence points;
- causal outcome differences;
- activation references eligible for patching.

Exact token alignment will not always be possible after stochastic divergence. The API should distinguish exact replay from statistically paired execution.

## 7. Provenance implementation

Derive provenance from event parent identifiers.

Initial queries:

- ancestors of a high-impact action;
- artifacts influenced by a protected input;
- agents in the minimal causal subgraph;
- paths from untrusted source to protected sink;
- graph separators between sources and sinks;
- propagation depth and affected-node count.

For small experiments, an in-memory directed graph is sufficient. Storage should be abstracted so larger runs can use a graph-capable backend later.

## 8. Defense implementations

### 8.1 Causal information

Offline initially:

- align paired episodes;
- train restricted decoders over messages, activations, and actions;
- estimate usable-information differences;
- run activation patch sweeps;
- report confidence intervals and held-out transfer.

### 8.2 Hyperproperties

Begin with a small policy DSL over events and graph relations.

Example concepts:

- `never(source -> sink)`;
- `requires_independent_approval(action, count=2)`;
- `creator_must_not_be_sole_verifier(artifact)`;
- `equivalent_public_output(pair, secret_only_difference=True)`.

Compile policies into trace-pair or graph queries. Avoid building a general theorem prover in the first version.

### 8.3 Sequential evidence

Define an interface that consumes timestamped scores and emits:

- current e-value;
- cumulative evidence;
- calibration status;
- alarm decision;
- evidence-source attribution.

The implementation must test supermartingale or calibration assumptions on benign validation streams rather than relying only on attack performance.

### 8.4 Mediation

Mediators implement the defense transformation interface and record both original and delivered messages under appropriate access controls.

Initial mediators:

- generic paraphrase;
- typed schema;
- task-sufficient summary;
- rate limit;
- recipient-specific randomized transformation;
- memory compartmentalization.

## 9. Configuration strategy

Use human-readable configuration files for models, scenarios, attacks, and defenses. Resolve them into validated immutable dataclasses before execution.

Important properties:

- explicit version fields;
- no hidden environment-dependent defaults;
- deterministic seed derivation;
- configuration hash stored with results;
- defense order declared explicitly;
- separate train, calibration, validation, and test splits.

## 10. Testing strategy

### Unit tests

- event immutability;
- configuration validation;
- deterministic seed derivation;
- defense ordering;
- intervention targeting;
- metric calculations.

### Property tests

- provenance graph remains acyclic where required;
- every external action has an authorization ancestor;
- paired-run invariants are preserved;
- event identifiers are unique;
- blocked actions cannot affect environment state.

### Integration tests

- two scripted agents complete a benign scenario;
- a known secret channel is detected by the expected oracle;
- a coalition violation is found in a fixed fixture;
- an e-process remains below alarm threshold on a deterministic null fixture;
- a mediator reduces a scripted channel’s capacity.

### Adversarial regression tests

Every demonstrated attack becomes a versioned fixture with:

- attack configuration;
- expected security outcome;
- defense behavior;
- accepted utility range;
- exact or statistical reproducibility tolerance.

## 11. Implementation milestones

### Milestone 1: deterministic skeleton

- event schema;
- resolved specification;
- scripted agents;
- orchestrator;
- scenario interface;
- event storage;
- basic provenance graph.

### Milestone 2: local model integration

- one 7–9B model adapter;
- structured actions;
- token/logit capture;
- selected activation hooks;
- reproducibility metadata.

### Milestone 3: Experiment 1 — causal usable information

- secret-channel scenario;
- codebook and tool-assisted channels;
- message and activation decoders;
- paired secret intervention;
- one mediator;
- security/utility report.

### Milestone 4: Experiment 2 — coalitional hyperproperties

- heterogeneous workflow;
- tool sandbox;
- policy DSL;
- coalition enumeration;
- provenance-backed violation localization.

### Milestone 5: Experiment 3 — anytime-valid evidence

- long-horizon runner;
- benign calibration streams;
- sequential evidence process;
- fixed-threshold baselines;
- lifetime false-alarm and delay report.

### Milestone 6: robust evaluation

- second model family;
- held-out attack and topology splits;
- capacity adaptation study;
- CVaR optimizer;
- reproducible presentation results.

## 12. Definition of a successful first version

The first version is successful when it can run the same agents and scenarios under multiple attack and defense configurations and produce:

- an immutable trace;
- a provenance graph;
- security and utility metrics;
- a Section 3.3 dimension record;
- at least one paired causal intervention;
- one coalition property result;
- one lifetime evidence result;
- one mediator capacity result;
- a fully resolved reproduction configuration.
