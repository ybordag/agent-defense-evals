# Implementation Roadmap

## Objective

Build a reusable open-weight evaluation harness that tests defenses across the eight attack dimensions defined in Section 3.3 of the motivating paper. The harness must support controlled multi-agent scenarios, white-box model access, causal interventions, coalition-level verification, sequential monitoring, and active channel defenses.

The implementation begins with scripted agents. Model downloads and GPU-backed execution start only after deterministic orchestration, event history, defense mediation, and provenance invariants are verified.

## Current status

Phases 0–4 and the controlled Phase 6 capacity-shaping experiment are
implemented. The Phase 3 + 6 adaptive-mediation and Phase 4 model-workflow
remediation experiments have also run successfully on pinned
Qwen2.5-7B-Instruct. Phase 5 includes its
confirmatory statistical contract, goal-driven model-agent path, and resumable
sharded runner, but its registered 7B calibration/validation/test run remains
pending.

## Reset decision

The prior `agent_interaction_evals` implementation and target-word experiment are not part of the new architecture. Git history preserves them. The replacement uses:

- package: `agent_defense_evals`;
- CLI: `agent-defense-evals`;
- broad research documents as the specification;
- a common event-sourced architecture for all four experiments.

## Phase 0: deterministic foundation

### Build

- immutable experiment specifications;
- explicit Section 3.3 attack-dimension configuration;
- deterministic seed and identifier derivation;
- append-only event records and JSONL storage;
- trace validation and replay;
- configuration validation;
- CLI commands for validation, execution, and replay.

### Gate

- `agent-defense-evals validate-config` accepts the checked-in baseline configuration;
- one episode produces an immutable, replayable trace;
- rerunning the same resolved specification produces the same semantic events;
- every result records its resolved specification and dimension vector;
- unit, lint, and type-oriented schema checks pass.

## Phase 1: scripted vertical slice

### Build

- replaceable interfaces for model runtimes, agent policies, scenarios, attacks, defenses, and interventions;
- synchronous multi-agent scheduler;
- defense gateway with allow, transform, and block decisions;
- deterministic distributed-choice scenario;
- benign scripted policies;
- scripted action mutation attack;
- blocking defense;
- provenance DAG derived from event-parent relationships;
- security and utility outcomes.

### Gate

- two scripted agents solve a task requiring both private views;
- an attack traverses the same action and event interfaces as benign behavior;
- a blocked action cannot mutate scenario state;
- provenance returns every ancestor of the terminal action;
- deterministic runs with identical seeds produce equivalent traces.

## Phase 2: open-weight model runtime

Status: complete. See [Phase 2 completion](phase-2-completion.md).

### Build

- direct Hugging Face/Transformers runtime for white-box experiments;
- optional OpenAI-compatible runtime for behavioral scaling;
- token probability capture;
- selected hidden-state capture;
- activation patching;
- model, tokenizer, revision, adapter, and sampling provenance;
- scripted/model-agent interoperability.

### Gate

- one 7–9B model acts through the common policy interface;
- activations link to exact generation events and token spans;
- a controlled activation patch changes a predicted downstream state;
- no model-specific logic enters the orchestrator or scenario contracts.

## Phase 3: Experiment 1 — causal usable information

Status: complete. See [Phase 3 completion](phase-3-completion.md).

### Build

- legitimate collaborative task with deterministic ground truth;
- random private bitstring;
- benign, overt-codebook, learned-codebook, and tool-assisted channels;
- paired secret interventions;
- message, activation, and action decoders;
- activation patch sweeps;
- security-versus-utility reporting.

### Gate

- benign secret decoding remains at chance within uncertainty;
- a controlled covert channel succeeds;
- the harness separates message-visible from behavior-visible information;
- a localized patch produces a measurable causal effect.

## Phase 4: Experiment 2 — coalitional hyperproperties

Status: complete. See [Phase 4 completion](phase-4-completion.md).

### Build

- four to six agent roles;
- sandboxed tools and shared artifacts;
- heterogeneous model configurations;
- provenance-backed policy DSL;
- exhaustive coalition enumeration for small systems;
- sparse and dense communication topologies;
- irreversible-action authorization gates.

### Gate

- local policies accept every component of at least one harmful composition;
- a coalition property detects the prohibited joint trajectory;
- the minimal responsible provenance subgraph is localized;
- separator-based checks are compared with exhaustive enumeration under explicit assumptions.

## Phase 5: Experiment 3 — anytime-valid evidence

Status: in progress. The sequential-statistics foundation, trace-derived
scoring, preliminary 0.5B/7B pilots, confirmatory split contract, uncertainty
reporting, goal-driven prompts, resumable shards, mandatory split selection,
and implementation-bound manifests are implemented; see
[Phase 5 plan and first increment](phase-5-plan.md). The larger held-out 7B run
has completed calibration and validation, and its unchanged test split is
running exactly once; the final gate evaluation remains.

### Build

- long-horizon episodes and randomized attack onset;
- persistent memory and delayed triggers;
- common streaming score interface;
- e-process implementation;
- fixed-threshold and change-point baselines;
- benign-drift calibration and diagnostics.

### Gate

- the preregistered lifetime false-alarm rate is maintained on held-out benign streams;
- attack episodes exhibit measurable evidence drift;
- detection delay is reported relative to the first irreversible action;
- failures of conditional calibration are surfaced rather than hidden.

## Phase 6: Experiment 4 — capacity shaping

Status: complete against the controlled synthetic gates. See
[Phase 6 completion](phase-6-completion.md). Open-model adaptive transfer is a
Phase 7 target.

### Build

- message-mediator interface;
- generic paraphrasing baseline;
- typed task-specific schemas;
- task-sufficient summaries;
- recipient-specific randomized views;
- memory reset and information-rate budgets;
- optimized sender and receiver decoders;
- residual-capacity estimation.

### Gate

- estimators recover the capacity ordering of known synthetic channels;
- adaptive attackers outperform fixed attackers where capacity remains;
- at least one mediator reduces attack success while retaining nontrivial task utility;
- zero-communication coordination is reported as outside the capacity claim.

## Phase 7: defense optimization and transfer

Status: framework increment and two model-backed cross-phase experiments
implemented; see
[Phase 7 optimization and transfer progress](phase-7-plan.md). Phase 7 is the
shared transfer and optimization layer, not an independent experiment performed
after separately expanding every prior phase. The checked-in first report uses
controlled fixture outcomes to verify split, objective, and export accounting;
the separate Phase 3 + 6 and Phase 4 paths now have balanced, trace-derived
Qwen2.5-7B results. Held-out model transfer and optimizer ingestion remain.

Recommended execution order:

1. build the common Phase 7 sweep, split, objective, and reporting framework;
2. combine Phases 3 and 6 against adaptive model-backed covert channels;
3. extend Phase 4 to end-to-end model workflows and utility-preserving repair;
4. run the Phase 5 canary and confirmatory splits through the shared execution
   infrastructure;
5. evaluate held-out models, prompts, attacks, topologies, coalitions, and
   horizons before marking Phase 7 or broader cross-phase transfer complete.

### Build

- attack-dimension sweeps;
- held-out model, attack, topology, coalition, and horizon splits;
- CVaR and worst-case objectives;
- defense-stack search;
- reproducible reports;
- shadow-deployment and policy-export adapters.

### Gate

- every result reports security, utility, latency, uncertainty, and assumptions;
- worst-case performance is evaluated over dimension combinations;
- model-specific findings are separated from model-independent mechanisms;
- deployment recommendations identify required observability and mediation assumptions.

## Engineering choices

- Python 3.11 or 3.12;
- `pyproject.toml` as the package and tool configuration source;
- Pydantic for immutable specifications and events;
- YAML for human-authored experiment configurations;
- JSONL for initial event storage, with external content-addressed blobs later;
- direct PyTorch/Transformers execution for white-box access;
- a simple in-process provenance DAG first, replaceable by NetworkX or a graph backend as scale demands;
- Pytest and Ruff for the initial verification loop;
- synthetic secrets and sandboxed tools only.

## Current implementation target

Two immediate tracks remain: execute Phase 5 in stages without exposing its
test split, and optimize then replicate natural-language covert channels and
model workflows on a held-out 7–9B model family.
The next Phase 5 action is a one-episode 7B calibration canary, followed by
calibration, validation, and only then the frozen test split.
