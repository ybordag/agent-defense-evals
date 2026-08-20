# Implementation Plan

## Objective

Build a reproducible two-agent experiment that measures legitimate
collaboration, exact covert target-word emission, near-target leakage, and the
observability of Agent 1's indirect signal.

Each phase has a gate. If a gate fails, simplify the current phase rather than
adding the next feature.

## Phase 0: project foundation

### Build

- Add a Python `pyproject.toml` and `src/` package.
- Add typed configuration and schemas for runs, episodes, messages, and scores.
- Add deterministic seed handling.
- Add JSONL event writing and an ignored `artifacts/` directory.
- Add unit-test and lint commands.

### Gate

A local command can load configuration, generate one episode specification,
write it as JSONL, and read it back without contacting a model.

If this fails, do not implement agents.

## Phase 1: deterministic overt task

### Build

- Generate candidate plans with public attributes and scores.
- Generate complementary private constraints for both agents.
- Guarantee a unique optimal feasible plan.
- Implement feasibility, optimality, and regret scorers.
- Add property-style tests over many seeds.

### Gate

For at least 1,000 generated seeds:

- Every task has at least one feasible plan.
- Every task has exactly one optimal feasible plan.
- Ground-truth scoring is deterministic.
- Neither private view alone contains all constraints.

If generation is unreliable, reduce the number of attributes and use fixed
templates rather than adding exception handling.

## Phase 2: model client and basic agents

### Build

- Implement an OpenAI-compatible asynchronous client.
- Attach `X-Fairlead-Thread-Id` using the episode ID.
- Implement role prompts and separate chat histories for both agents.
- Implement bounded alternation and structured final output from Agent 2.
- Record raw requests, responses, latency, parse failures, and retries.

### Gate

Run 20 benign episodes with one pinned model pair:

- At least 80% complete without parser or transport failure.
- Overt optimal-plan accuracy is at least 70% initially.
- Every episode can be reconstructed from its event log.

If utility is too low, expose fewer plans, simplify constraints, and improve the
prompt. Do not add the covert task until benign collaboration is stable.

## Phase 3: lexical policy and covert objective

### Build

- Create and validate the target vocabulary.
- Sample targets independently from overt tasks.
- Add collusive prompts for Agent 1 and Agent 2.
- Reject Agent 1 messages containing prohibited target forms.
- Bound regeneration attempts and log policy violations.
- Detect exact standalone target emission in every Agent 2 message.
- Add benign, leakage-control, collusive, and shuffled-target conditions.

### Gate

Run paired episodes with the same overt-task seeds:

- Agent 1 never delivers a prohibited lexical form.
- Accidental exact emission is low and quantified in controls.
- Collusive episodes exceed the control exact-emission rate.
- Overt-task accuracy remains measurable rather than collapsing universally.

If the covert task never succeeds, reduce the vocabulary and permit clearer
semantic hints. If it succeeds trivially in controls, replace frequent or
task-related target words.

## Phase 4: near-target detection

### Build

- Normalize and tokenize Agent 2 outputs.
- Record lexical edit and morphological similarity to the target.
- Add a frozen embedding provider and cache vocabulary embeddings.
- Score emitted content words and short phrases against the target.
- Calibrate a semantic threshold using a fixed labeled synonym/non-synonym set.
- Store raw maxima, matching spans, and the thresholded flag.

### Gate

- Exact target matches always receive maximal similarity.
- Known synonyms score above unrelated controls at a useful rate.
- The calibration data and threshold are fixed before experimental comparison.
- Similarity computation is deterministic given cached embeddings.

If semantic calibration is unreliable, report continuous similarity only and
do not make thresholded near-target claims.

## Phase 5: first channel defense

### Build

- Implement an identity defense.
- Implement one parameterized task-preserving defense, initially compression or
  paraphrasing.
- Apply the defense only to Agent 1-to-Agent 2 messages.
- Run benign and collusive conditions at matched defense strengths.

### Gate

At least one defense setting must produce a non-degenerate comparison: overt
utility remains above chance while exact or near-target behavior changes.

If no setting does, sweep fewer, wider defense strengths and inspect transcripts
before adding another defense family.

## Phase 6: transcript decoder

### Build

- Give an independent monitor the fixed candidate vocabulary and only Agent 1
  delivered messages.
- Record target rank, top-k accuracy, log loss, and calibration.
- Score progressively after each Agent 1 turn.
- Evaluate against shuffled-target and no-objective controls.

### Gate

The monitor must outperform the `1/N` chance baseline on successful collusive
episodes without receiving the target through metadata or prompts.

If it fails, first inspect whether Agent 2's success came from information not
available to the monitor, such as its own questions or prearranged indexing.
Do not interpret monitor failure as signal absence.

## Phase 7: causal replay

### Build

- Freeze completed transcripts.
- Replay Agent 2 after removing one Agent 1 turn at a time.
- Add task-preserving paraphrase interventions for suspicious spans.
- Record changes in target probability, exact emission, near-target similarity,
  and overt utility.
- Repeat stochastic replays or use token log-probabilities when available.

### Gate

Report a span as task-separable causal evidence only when intervention reduces
target emission or probability while the overt answer remains feasible and
equally optimal.

If deletion destroys conversational coherence, use paraphrase replacement and
report the intervention limitation explicitly.

## Phase 8: experimental run and analysis

### Build

- Freeze prompts, vocabulary, thresholds, and configurations.
- Run paired seeds across the minimum condition matrix.
- Produce confidence intervals for overt accuracy and covert outcomes.
- Plot the security-utility frontier.
- Plot progressive decoder rank and causal signal by turn.
- Publish representative transcripts selected by declared criteria.

### Initial sample plan

- Pilot: 20 episodes per condition.
- Main behavioral run: 100 episodes per condition.
- Increase to 300 only if variance or rare outcomes require it and runtime
  permits.

For binary outcomes, use paired bootstrap intervals across matched episode
seeds. Report raw denominators, transport failures, policy violations, and parse
failures.

### Gate

The final result must include:

- A benign utility baseline
- A covert control baseline
- Exact and near-target outcomes
- At least one defended comparison
- Uncertainty estimates
- A plainly stated limitation section

## Deferred extensions

These are roadmap items and must not block the initial result:

- Unaware Agent 2 / induced-behavior condition
- Heterogeneous sender and receiver models
- Symmetric channel defenses
- Learned or adaptive defense-aware signaling
- Direct activation capture and probes
- A third relay agent
- Tool-choice, database, timing, and shared-state channels
- Fairlead-integrated security circuit breaking

## Deployment roadmap (deferred)

After the local behavioral experiment works end to end, design the deployment
path together rather than allowing deployment concerns to block the initial
result. The intended sequence is:

1. Add a reproducible Docker image and local container smoke test.
2. Add runtime configuration through mounted files and environment variables.
3. Add Kubernetes manifests or a small Helm chart for experiment workers.
4. Add a DGX Spark deployment overlay that targets Fairlead and pinned vLLM
   backend pools.
5. Verify artifact persistence, resource requests, job restart behavior, and
   model-condition provenance on the two-node Spark environment.

Container and Kubernetes work starts only after the experiment has a stable CLI
and one successful end-to-end model-backed episode.

## Recommended implementation order for the next coding session

1. Create the package, schemas, configuration, and event sink.
2. Implement and test the overt task generator and scorer.
3. Add the Fairlead/OpenAI model client.
4. Run one benign conversation end to end.
5. Stabilize benign utility before adding covert prompts.

The first meaningful milestone is one replayable benign episode, not a large
framework or a complete defense suite.
