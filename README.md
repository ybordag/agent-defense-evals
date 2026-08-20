# Agent Interaction Evals

Evaluation harnesses for security, information flow, and coordination in
multi-agent AI systems.

The first experiment studies whether two agents can complete a verifiable
collaborative task while one indirectly signals an unrelated target word for
the other to emit. It measures overt utility, exact covert success, near-target
leakage, and the observability of the signal.

## Documentation

- [Experimental design](docs/design.md)
- [Implementation plan](docs/implementation-plan.md)

## Phase 0 quick start

Python 3.11 or newer is recommended.

```bash
conda create --name agent-interaction-evals python=3.11 -y
conda activate agent-interaction-evals
python -m pip install -r requirements.txt
```

Run the Phase 0 smoke test:

```bash
agent-interaction-evals phase0-smoke \
  --config configs/experiment.yaml \
  --output artifacts/phase0-smoke.jsonl
```

Run the test and lint suites:

```bash
pytest
ruff check .
```

The smoke test loads typed configuration, deterministically generates an
episode specification, writes an append-only JSONL event, reads it back, and
verifies the round trip.

## Deployment

The first implementation runs as a local Python client against an
OpenAI-compatible endpoint. Container and Kubernetes deployment for the DGX
Spark environment is intentionally deferred until the behavioral experiment
works end to end.
