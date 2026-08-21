# Agent Defense Evals Documentation

## Purpose

This documentation describes an open-weight evaluation harness for multi-agent security. It connects a broad research program—collusion, steganography, heterogeneous attacks, provenance, and containment—to a concrete first implementation.

The repository implements Phases 0–4, the Phase 5 anytime-evidence framework,
and the controlled Phase 6 capacity-shaping experiment. Phase 5's frozen,
resumable 7B confirmatory run is ready but has not yet been executed.

## Research program

1. [Problem and objectives](01_problem_and_objectives.md)
2. [Theoretical foundations](02_theoretical_foundations.md)
3. [Defense conjectures](03_defense_conjectures.md)
4. [Experimental program and transferability](04_experimental_program_and_transfer.md)
5. [System architecture](05_system_architecture.md)
6. [Codebase design](06_codebase_design.md)
7. [References](07_references.md)

## Implementation

- [Implementation roadmap](implementation/roadmap.md) defines the repository reset, staged architecture, experiment order, and acceptance gates.
- [Phase 2 runtime and environment plan](implementation/phase-2-environments.md) defines the local white-box path and DGX cluster boundary.
- [Phase 2 completion report](implementation/phase-2-completion.md) records the implementation, acceptance evidence, and remaining scope limits.
- [Phase 3 completion report](implementation/phase-3-completion.md) records the paired-channel results, held-out transfer test, and 7B causal patch sweep.
- [Phase 4 completion report](implementation/phase-4-completion.md) records the coalition, topology, provenance, irreversible-gate, and heterogeneous-model results.
- [Phase 5 plan and first increment](implementation/phase-5-plan.md) records the sequential evidence design, controlled results, and open-model integration plan.
- [Phase 6 completion report](implementation/phase-6-completion.md) records the mediator, adaptive-codebook, memory-budget, action-gate, and capacity results.
- [Phase 7 optimization and transfer progress](implementation/phase-7-plan.md) records the held-out split, robust-objective, defense-stack search, and shadow-policy framework.
- [Phase 3 + 6 model-capacity result](implementation/phase-7-model-capacity-result.md) records the balanced Qwen2.5-7B adaptive-channel experiment and small-model capability control.

## Reading order

For the project rationale, read the problem statement, conjectures, and experimental program. For implementation, read the roadmap, system architecture, and codebase design documents.

## Scope rule

The broad documents define the target harness. Each experimental implementation must state which conjecture and Section 3.3 dimensions it tests and must not generalize beyond its model, scenario, observability, and intervention assumptions.
