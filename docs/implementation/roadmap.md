# Implementation Roadmap

## Objective

Build a reusable open-weight evaluation harness that tests defenses across the eight attack dimensions defined in Section 3.3 of the motivating paper. The harness must support controlled multi-agent scenarios, white-box model access, causal interventions, coalition-level verification, sequential monitoring, and active channel defenses.

The implementation begins with scripted agents. Model downloads and GPU-backed execution start only after deterministic orchestration, event history, defense mediation, and provenance invariants are verified.

## Current status

Phases 0–4 are implemented. Scripted configurations cover benign collaboration, blocked action mutation, paired covert-channel evaluation, and coalition-level artifact-flow verification. Model-backed configurations cover vLLM, direct Qwen2.5-7B-Instruct execution, activation probing, causal layer replacement, and heterogeneous local-policy auditing. Phase 5, anytime-valid evidence, is the next implementation target.

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

Phase 5 is the next implementation increment. It will add long-horizon episodes, randomized attack onset, persistent state, streaming evidence scores, and lifetime false-alarm evaluation while retaining the common event, model, defense, and provenance interfaces established in Phases 0–4.
