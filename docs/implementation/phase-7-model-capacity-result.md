# Phase 3 + 6 Model-Capacity Result

## Claim

In a controlled two-agent relay, a pinned Qwen2.5-7B-Instruct sender and
receiver executed a supplied two-bit covert codebook. Removing a known surface
carrier reduced attack success from `1.00` to chance (`0.25`), but moving the
same code to a semantic carrier restored attack success to `1.00`. A typed
mediator that retained only the legitimate task removed both registered
carriers and returned attack success to chance while preserving task utility.

This is evidence that a defense optimized against a fixed channel can fail
against an adaptive channel, and that task-sufficient mediation can dominate a
generic transform in this registered channel family. It is not evidence that
the models autonomously discovered a covert protocol or that the typed
mediator eliminates all natural-language side channels.

## Experimental design

- Model: `Qwen/Qwen2.5-7B-Instruct`.
- Pinned model and tokenizer revision:
  `a09a35458c702b33eeacc393d103063234e8bc28`.
- Runtime: direct Transformers white-box path on `spark-thor`, CUDA, greedy
  decoding.
- Agents: one model-backed sender and one model-backed receiver.
- Secret: four equiprobable symbols, requiring two bits.
- Legitimate tasks: incident triage, batch recovery, release check, and queue
  rebalance.
- Balance: every secret is factorially crossed with every task, preventing the
  legitimate task identifier from acting as a secret proxy.
- Conditions: four; each has 16 episodes, 32 model generations, and 320 trace
  events.
- Total: 64 episodes, 128 model generations, and 1,280 trace events.

The sender receives the legitimate task and private secret. Under the fixed
codebook it places the secret in `surface_code`; under the adaptive codebook it
places the secret in `semantic_code`. The receiver is prompted with the same
registered codebook but observes only the post-mediation message. The
experiment records proposed and delivered actions, defense decisions, model
identity, generation provenance, task utility, and whether the receiver's
action reproduces the secret.

The current `generic_paraphrase` is a synthetic, deterministic abstraction: it
zeros the surface carrier while retaining the task and semantic carrier. The
`typed_schema` mediator also zeros the semantic carrier. These interventions
isolate causal channel availability; they are not claims about the coverage of
a production natural-language paraphraser.

## Qwen2.5-7B result

| Condition | Attack success | Delivered MI (bits) | Action MI (bits) | Sender compliance | Utility |
| --- | ---: | ---: | ---: | ---: | ---: |
| Unrestricted + fixed surface | 1.00 | 2.00 | 2.00 | 1.00 | 1.00 |
| Paraphrase + fixed surface | 0.25 | 0.00 | 0.00 | 1.00 | 1.00 |
| Paraphrase + adaptive semantic | 1.00 | 2.00 | 2.00 | 1.00 | 1.00 |
| Typed schema + adaptive semantic | 0.25 | 0.00 | 0.00 | 1.00 | 1.00 |

The Wilson 95% interval is `[0.806, 1.000]` for each perfect-success
condition and `[0.102, 0.495]` for each chance-success condition. All eight
preregistered implementation gates passed: complete generation tracing, model
identity, sender compliance, unrestricted-channel success, fixed-code
suppression, adaptive recovery, typed-mediator suppression, and legitimate
utility preservation.

Mean end-to-end episode latency ranged from `1.96` to `2.11` seconds. The raw
report is `artifacts/phase7-model-capacity-7b-report.json`, with SHA-256
`ad49efd08281ae4daf5beb3b65bf872cf23b6ef4cdd8eb9d378f8e69f09b507d`.

## Small-model capability control

The same balanced design was run through vLLM with pinned
Qwen2.5-0.5B-Instruct revision
`7ae557604adf67be50417f59c2c2f167def9a775`. Utility remained `1.00`, but
sender codebook compliance ranged from `0.00` to `0.1875`; unrestricted and
adaptive attack success reached only `0.50`. The model therefore failed the
manipulation check and cannot adjudicate the capacity conjecture. This negative
control shows why attacker capability must be measured before interpreting a
low attack rate as defense efficacy.

Its raw report is `artifacts/phase7-model-capacity-vllm-report.json`, with
SHA-256
`d539370909cb87dec6600cacf11a6947a009e3f9eab1c39f45fbbdb32beeb1f4`.

## Section 3.3 coverage

| Dimension | Coverage in this experiment |
| --- | --- |
| Detectability | Varied indirectly through a conspicuous surface code and a lower-visibility semantic code; no passive detector is evaluated. |
| Locality | Fixed two-agent coalition; not swept. |
| Cascading | Fixed single sender-to-receiver edge; not swept. |
| Composition | Fixed sender generation, mediation, and receiver generation path. |
| Horizon | Fixed two-step episode; no delayed or persistent channel. |
| Attributability | Fully instrumented model, action, mediation, and event provenance with zero configured degradation. |
| Directness | Fixed explicit adversarial instructions and supplied codebooks. |
| Reversibility | Information disclosure is scored, but rollback and consequential-action containment are not tested. |

The strongest supported conclusion is therefore about adaptive channel choice
under active mediation. Broader Section 3.3 robustness still requires sweeps
over coalition, topology, horizon, indirect incentives, provenance loss, and
consequential actions.

## What this teaches

1. A fixed-channel defense result is not an adaptive-defense result. The exact
   same 7B agents moved two bits to the residual carrier and recovered all
   measured channel information.
2. A weak attacker is a confound. The 0.5B model's low success accompanied low
   protocol compliance, whereas the 7B model passed the manipulation check.
3. Task and secret balance matters. Crossing every secret with every task
   makes the zero-information typed result interpretable rather than allowing
   the task label to leak the secret.

## Reproduction

On the configured Thor environment:

```bash
agent-defense-evals phase7-model-capacity \
  --config configs/experiments/phase7_model_capacity_7b.yaml \
  --output artifacts/phase7-model-capacity-7b-report.json
```

The next defensible extension is adversarial optimization over natural-language
codebooks and mediation seeds, followed by a frozen replication on a held-out
7–9B model family. That would test discovery and transfer rather than supplied
protocol execution.
