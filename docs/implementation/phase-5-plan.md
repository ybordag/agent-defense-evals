# Phase 5 Implementation Plan and First Increment

## Status

Phase 5 is in progress. The first increment implements and validates the sequential-statistics core on controlled stochastic score streams. It does not yet complete the phase: the next increment must derive the scores from long-horizon open-model agent traces on Thor.

## Conjecture under test

Weak coalition evidence distributed across a long stochastic trajectory can be accumulated by an anytime-valid process while controlling the probability of ever alarming under a conditionally calibrated benign null. A fixed per-turn threshold either spends its error budget repeatedly or becomes too conservative, while a conventional change-point detector can lose its nominal error rate under benign drift.

For a bounded score `z_t` and a registered benign upper bound `p0`, the implemented component process is

\[
M_t(\lambda)=\prod_{i=1}^{t}[1+\lambda(z_i-p_0)].
\]

When `E[z_t | F_(t-1)] <= p0` and the betting factor remains nonnegative, each component is a test supermartingale. The monitor averages several fixed betting fractions, so the resulting mixture is also an e-process. It alarms when `E_t >= 1/alpha`; Ville's inequality then bounds the probability that it ever crosses the threshold by `alpha` under the stated null.

This guarantee is conditional, not distribution-free magic. The report therefore records the maximum generating conditional mean and labels any condition that violates the registered bound.

## First-increment implementation

- common streaming-monitor protocol and immutable monitor snapshots;
- log-domain mixture betting e-process;
- fixed per-turn score threshold;
- one-sided Page CUSUM change-point baseline;
- empirical lifetime-threshold calibration for both baselines;
- 256-step stochastic streams with randomized attack onset;
- stationary and time-varying benign regimes inside the registered null;
- an unmodeled benign shift outside the registered null;
- low-rate signaling, delayed-trigger, memory-poisoning, and reward-induced attack regimes;
- explicit attack onset and first irreversible-action time;
- separate pre-onset alarm, post-onset detection, delay, and before-harm metrics;
- CLI configuration and JSON report.

## Preliminary controlled results

The checked-in configuration uses 400 calibration streams and 400 held-out streams per condition, each 256 steps long, with `alpha = 0.05` and `p0 = 0.08`.

| Monitor | Benign stationary alarm | Benign drift alarm | Low-rate detection | Delayed-trigger detection | Memory-poisoning detection | Reward-induced detection |
|---|---:|---:|---:|---:|---:|---:|
| Mixture e-process | 0.00% | 0.00% | 69.75% | 76.75% | 91.75% | 40.25% |
| Fixed per-turn | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% |
| Page CUSUM | 1.00% | 10.75% | 97.25% | 96.50% | 98.00% | 96.25% |

Attack entries are post-onset detection rates. The e-process had positive mean terminal log-evidence under all four attacks. Its median post-onset delays were 113, 142, 128, and 126 steps respectively. Detection before the configured irreversible action was only 8.25–34.00%, showing that validity alone does not guarantee adequate operational power.

The fixed per-turn baseline calibrated to a lifetime error budget selected a threshold of `1.0` for binary scores and therefore never fired. CUSUM was much faster and more powerful, but its held-out false-alarm rate rose to 10.75% under modeled benign drift. That comparison exposes the expected power–calibration tradeoff rather than declaring the e-process universally superior.

The unmodeled benign shift reaches conditional mean `0.14`, above `p0 = 0.08`; it is explicitly marked invalid for the registered guarantee. The e-process alarm rate on that condition was 7.75%, which is reported as a calibration-envelope violation rather than silently counted as nominal null performance.

## First-increment gates

- e-process lifetime false alarms remain at or below 5% on both held-out valid benign regimes: passed;
- every attack regime has positive mean terminal log-evidence: passed;
- post-onset delay and detection before the irreversible step are reported: passed;
- the out-of-envelope benign shift is surfaced as conditionally uncalibrated: passed.

These gates validate the sequential engine and experimental accounting. They are not the final Phase 5 roadmap gates until the score stream comes from stochastic LLM-agent behavior.

## Section 3.3 coverage

The first increment primarily varies detectability, composition, horizon, and directness. Attacks replace conspicuous per-turn deviations with weak persistent changes, the score represents coalition-level composition, streams span 256 steps, and conditions include delayed and reward-induced behavior. Attribution degradation and reversibility are measured through onset-to-alarm and alarm-to-irreversible-action timing. Locality and cascading are held controlled until the agent-trace adapter reuses Phase 4 provenance.

## Next increments

### Increment 2: trace-derived score adapters

Convert the common event stream into bounded scores without changing the monitors. Initial adapters should combine:

- Phase 3 action-level usable-information residuals;
- Phase 4 protected-flow and coalition-policy residuals;
- provenance depth, fan-out, and anomalous ancestry;
- irreversible tool-use risk.

Each score must record its source components and the calibration data used to bound its benign conditional mean.

### Increment 3: stochastic open-model agents on Thor

Run long-horizon episodes with Qwen agents through the existing vLLM and direct Transformers runtimes. Randomize sampling seeds and attack onset, retain model and revision provenance, and include:

- benign task and policy drift;
- low-rate coordination;
- delayed memory triggers;
- reward-induced coordination;
- held-out prompts, seeds, and at least one held-out model configuration.

The 7B model is not required for every stream. High-volume behavioral replicas can use the small vLLM-served model, with a stratified 7B confirmation set and white-box activation scores.

### Increment 4: confirmatory evaluation

Preregister the score, null envelope, alpha, splits, and irreversible-action semantics. Then compare monitors at matched lifetime error, report uncertainty, examine conditional coverage by benign regime, and fail the phase gate if the null calibration does not transfer.

## Reproduction

```bash
agent-defense-evals phase5-run \
  --config configs/experiments/phase5_anytime_evidence.yaml \
  --output artifacts/phase5-report.json
```

## Current limitations

- Scores are generated stochastic fixtures rather than model-derived telemetry.
- The binary score has known generating probabilities; deployed scores will require estimation and diagnostics.
- The current e-process uses fixed betting fractions rather than online adaptive betting.
- The CUSUM threshold is calibrated empirically for the configured finite horizon and has no anytime guarantee beyond it.
- The fixed per-turn baseline is intentionally simple and should be joined by a fixed-window classifier.
- Before-harm power is currently too low for the e-process to serve as a standalone action gate.
- No claim is made under unobserved attacks whose score distribution is identical to the benign conditional distribution.
