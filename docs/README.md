# Agent Defense Evals Documentation

## Purpose

This documentation describes an open-weight evaluation harness for multi-agent security. It connects a broad research program—collusion, steganography, heterogeneous attacks, provenance, and containment—to a concrete first implementation.

The repository currently implements Phases 0–2: deterministic event history, scripted and model-backed multi-agent orchestration, defense mediation, provenance, high-throughput remote serving, and direct white-box activation intervention. Phase 3 begins the first defense-conjecture experiment.

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

## Reading order

For the project rationale, read the problem statement, conjectures, and experimental program. For implementation, read the roadmap, system architecture, and codebase design documents.

## Scope rule

The broad documents define the target harness. Each experimental implementation must state which conjecture and Section 3.3 dimensions it tests and must not generalize beyond its model, scenario, observability, and intervention assumptions.
