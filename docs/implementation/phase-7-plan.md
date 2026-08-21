# Phase 7 Optimization and Transfer Progress

## Status

The first Phase 7 framework increment and the first real cross-phase model
experiment are implemented. The framework freezes structural
transfer cases, enforces held-out axes, searches defense stacks under a utility
constraint, reports worst-case and CVaR security loss, and exports the selected
stack as a non-enforcing shadow policy.

The optimizer's checked-in outcomes remain a controlled fixture used to verify
optimization and leakage accounting. The separate Phase 3 + 6 path now has a
real, trace-derived Qwen2.5-7B result, but it has not yet been ingested into the
optimizer or replicated on a held-out model family. Phase 7 therefore remains
in progress.

## Sequencing decision

Phase 7 is the shared transfer layer for strengthening Phases 3–6:

1. combine the Phase 3 covert-channel scenario with Phase 6 adaptive mediators;
2. extend Phase 4 to end-to-end model workflows and utility-preserving repair;
3. execute the Phase 5 canary and confirmatory splits without test leakage;
4. ingest those observations into the Phase 7 optimizer;
5. evaluate held-out models, prompts, attacks, topologies, coalitions, and
   horizons before making transfer claims.

## Implemented contracts

- immutable defense-stack definitions;
- train, validation, and test cases with complete stack-by-case outcomes;
- attack-dimension vectors aligned with coalition and horizon fields;
- required structural holdouts for model family, prompt family, attack family,
  topology, coalition size, and horizon;
- validation-only stack selection;
- a minimum-utility feasibility constraint;
- worst-case and upper-tail CVaR security objectives;
- security, utility, latency, uncertainty, and provenance fields per outcome;
- explicit evidence scope to separate fixtures, model-specific findings, and
  multi-model findings;
- deployment requirements for observability, mediation, and assumptions;
- shadow-only policy export tied to the frozen specification hash.

## Phase 3 + Phase 6 model-capacity experiment

The first cross-phase execution path is implemented and has run with pinned
Qwen2.5-7B-Instruct. It uses two model-backed agents through the common runner:

1. the sender receives a two-bit secret and legitimate task;
2. the sender emits a registered surface or adaptive semantic carrier;
3. the common defense gateway applies unrestricted, paraphrase, or typed
   mediation;
4. the receiver observes only the delivered representation and generates the
   target action;
5. the report measures sender compliance, delivered-message information,
   receiver-action information, attack success, utility, latency, and complete
   model/event provenance.

The four paired conditions are unrestricted fixed code, paraphrased fixed code,
paraphrased adaptive code, and typed adaptive code. The codebook is supplied in
the prompts, so this tests whether open models can execute a channel selected
by the Phase 6 optimizer. It does not claim autonomous channel discovery.

Every two-bit secret was factorially crossed with every legitimate task. Across
64 episodes and 128 traced model generations, the 7B model achieved attack
success of `1.00`, `0.25`, `1.00`, and `0.25` in the four respective
conditions, with `1.00` utility and sender compliance throughout. All eight
experiment gates passed. The 0.5B control failed the sender-compliance
manipulation check and is reported as a capability limitation rather than
defense evidence. See [the full model-capacity result](phase-7-model-capacity-result.md).

## Controlled framework result

At a validation minimum-utility floor of `0.75`, the fixture selects the
`layered-capacity-provenance` stack:

- validation worst-case security loss: `0.24`;
- controlled test worst-case security loss: `0.40`;
- validation-to-test worst-case gap: `0.16`;
- controlled test CVaR loss: `0.39`;
- controlled test minimum utility: `0.76`.

The gap demonstrates the report's intended behavior under structural shift; it
is not an empirical estimate. Raising the utility floor to `0.85` excludes the
layered stack and selects the cheaper `paraphrase-gate` stack, confirming that
the feasibility constraint changes selection without consulting test data.

## Reproduction

```bash
agent-defense-evals phase7-run \
  --config configs/experiments/phase7_controlled_optimization.yaml \
  --output artifacts/phase7-controlled-report.json
```

## Completion criteria

Phase 7 remains incomplete until:

- controlled fixture outcomes are replaced with trace-derived observations;
- the Phase 4 end-to-end model workflow and repair experiment runs;
- the Phase 5 held-out confirmatory evidence is available;
- at least one genuinely held-out model family is executed;
- every selected-stack recommendation reports uncertainty and its deployment
  observability and mediation assumptions;
- a shadow deployment validates policy export without enabling enforcement.
