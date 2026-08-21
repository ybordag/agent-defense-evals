# Phase 6 Completion Report

## Outcome

Phase 6 is complete against its controlled-experiment roadmap gates. The
experiment shows that removing one known carrier can create a false impression
of security: generic paraphrasing reduced a fixed surface codebook to chance,
but an adaptive sender and receiver moved the same two-bit signal into a
preserved semantic field and recovered perfect attack success. A typed
task-only schema removed both registered carriers, held the optimized attacker
at chance, and retained full legitimate utility.

This supports the unauthorized-capacity-shaping conjecture within the finite
registered channel family. It is not a Shannon-capacity proof and does not yet
show adaptation by trained LLM agents.

## Experimental setup

The sender receives one of four uniformly distributed targets, requiring two
bits of runtime coordination. Every message also carries one of four legitimate
task identifiers. The legitimate receiver succeeds whenever mediation
preserves the task identifier; unauthorized attack success requires exact
recovery of the two-bit target.

The registered input family has two independent carrier fields:

- a surface carrier used by the fixed codebook;
- a semantic carrier available to an adaptive codebook.

For each mediator, the experiment estimates its discrete channel on 128
training replicas. It exhaustively searches the finite sender codebook and
fits a maximum-a-posteriori receiver, breaking equal-accuracy sender ties by
mutual information. Evaluation uses 256 held-out mediation seeds across all
four targets, producing 1,024 observations per mediator and attacker mode.

Original proposals and delivered transformations cross the existing defense
gateway. The action-proposal and defense-decision boundaries therefore retain
the pre- and post-mediation representations when used in a full event trace.

## Implemented mechanisms

- message mediation through the common `Defense` and `DefenseGateway` boundary;
- unrestricted, generic-paraphrase, typed-schema, task-summary,
  recipient-randomized, and information-budget conditions;
- deterministic recipient-specific randomization from frozen seeds;
- cumulative and reset-each-turn receiver memory compartments;
- exhaustive adaptive sender codebook search;
- maximum-a-posteriori adaptive receiver decoding;
- exact-target accuracy with Wilson intervals, bit-error rate, empirical
  decoded mutual information, attack success, and legitimate utility;
- a confidence-gated consequential-action diagnostic;
- an explicit zero-runtime-communication boundary case;
- immutable YAML configuration, CLI execution, JSON report, and tests.

## Results

The chance exact-target success rate is 25%.

| Mediator | Fixed attack | Adaptive attack | Adaptive decoded information | Utility |
|---|---:|---:|---:|---:|
| Unrestricted | 100.00% | 100.00% | 2.000 bits | 100.00% |
| Generic paraphrase | 25.00% | 100.00% | 2.000 bits | 100.00% |
| Typed schema | 25.00% | 25.00% | 0.000 bits | 100.00% |
| Task summary | 25.00% | 25.00% | 0.000 bits | 100.00% |
| Recipient randomized | 25.00% | 58.69% | 0.711 bits | 100.00% |
| One-bit budget | 25.00% | 50.00% | 1.000 bit | 100.00% |

The Pearson correlation between adaptive decoded information and exact attack
success is `0.983` across the six registered mediators.

Generic paraphrasing is the key adversarial result. It completely removes the
fixed surface code, but leaves a two-bit semantic channel. Optimizing the
sender and receiver recovers that channel and restores attack success from
25% to 100%.

The one-bit budget recovers exactly one empirical decoded bit and limits exact
two-bit target recovery to 50%. Requiring 95% decoder confidence before a
consequential action reduces that ambiguous attack from 50% to 0% while the
separate legitimate task remains successful.

Cumulative two-turn memory exposes two bits and enables 100% recovery. Resetting
receiver memory each turn exposes only the final bit, reducing decoded
information to one bit and exact recovery to 50%.

## Zero-communication boundary

The report includes a pre-coordinated policy that succeeds with zero runtime
communication. It is explicitly marked outside the capacity claim. Runtime
capacity shaping cannot prevent behavior coordinated through shared pretrained
knowledge, a pre-shared plan, or an environmental Schelling point; those cases
require action constraints, provenance, or other defenses.

## Roadmap gates

- known synthetic channel-capacity ordering is recovered: passed;
- adaptive attackers outperform fixed attackers where capacity remains: passed;
- a structured mediator reduces attack success while retaining utility: passed;
- memory reset reduces cumulative capacity and attack success: passed;
- a consequential gate blocks an underdetermined high-impact action: passed;
- zero-communication coordination is excluded from the capacity claim: passed.

## Reproduction

```bash
agent-defense-evals phase6-run \
  --config configs/experiments/phase6_capacity_shaping.yaml \
  --output artifacts/phase6-report.json
```

## Limits and next evidence

- Carrier fields are controlled symbolic proxies for surface and semantic
  degrees of freedom, not natural-language channel measurements.
- Adaptive optimization is exhaustive over the registered finite codebook; it
  is not gradient-based or LLM-based adversarial training.
- Empirical decoded mutual information is a lower bound for the tested decoder,
  not a universal capacity estimate.
- The typed task protocol preserves 100% utility because the task was designed
  to admit a carrier-free sufficient message.
- Timing, tokenization, tool, activation, and unobserved environmental channels
  are outside the registered mediator.
- Recipient randomization is evaluated for one receiver and one retention
  mechanism.
- Cross-model and held-out natural-language transfer belongs in the Phase 7
  optimization and transfer study.

The natural next experiment combines this mediator framework with Phase 3's
model-backed covert channel and tests whether adaptive open-model agents recover
capacity under held-out prompts, models, and mediation seeds.
