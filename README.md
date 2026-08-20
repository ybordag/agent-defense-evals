# Agent Defense Evals

An event-sourced evaluation harness for multi-agent AI security defenses across collusion, steganography, heterogeneous attacks, and the attack dimensions defined in Section 3.3 of the motivating research.

Phases 0–4 are implemented: deterministic traces, scripted and model-backed agents, defense mediation, provenance, remote serving, white-box intervention, causal usable-information evaluation, and coalitional hyperproperty verification. Phase 4 includes exhaustive and graph-local coalition checks, provenance-backed flow policies, an irreversible authorization gate, and a heterogeneous Qwen model audit.

## Documentation

- [Documentation index](docs/README.md)
- [Defense conjectures](docs/03_defense_conjectures.md)
- [Experimental program](docs/04_experimental_program_and_transfer.md)
- [System architecture](docs/05_system_architecture.md)
- [Implementation roadmap](docs/implementation/roadmap.md)
- [Phase 2 completion report](docs/implementation/phase-2-completion.md)
- [Phase 3 completion report](docs/implementation/phase-3-completion.md)
- [Phase 4 completion report](docs/implementation/phase-4-completion.md)

## Development setup

Python 3.11 or newer is required.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,local-model]'
```

For an exact reproduction of the current Apple Silicon/Python 3.12 environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install \
  -c requirements/locks/macos-arm64-py312.txt \
  -e '.[dev,local-model]'
```

For the verified DGX Spark Linux ARM64/CUDA 13 environment, install the CUDA-enabled PyTorch wheel first and then apply the platform lock:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install \
  --index-url https://download.pytorch.org/whl/cu130 \
  'torch==2.11.0+cu130'
python -m pip install \
  -c requirements/locks/linux-arm64-cu130-py312.txt \
  -e '.[dev,local-model]'
```

See the [Phase 2 environment plan](docs/implementation/phase-2-environments.md) for the Thor deployment workflow and vLLM boundary.

## Core commands

Validate the benign scripted configuration:

```bash
agent-defense-evals validate-config \
  --config configs/experiments/scripted_baseline.yaml
```

Run an episode and write its immutable trace:

```bash
agent-defense-evals run \
  --config configs/experiments/scripted_baseline.yaml \
  --output artifacts/scripted-baseline.jsonl
```

Replay and validate a trace:

```bash
agent-defense-evals replay \
  --events artifacts/scripted-baseline.jsonl
```

Run verification:

```bash
pytest
ruff check .
```

The blocked-attack configuration is `configs/experiments/scripted_blocked_attack.yaml`.

Thor model-backed configurations are:

- `configs/experiments/model_vllm_smoke.yaml` for the running vLLM endpoint;
- `configs/experiments/model_transformers_7b.yaml` for direct 7B white-box execution.

Run the Phase 3 behavioral experiment locally:

```bash
agent-defense-evals phase3-run \
  --config configs/experiments/phase3_causal_information.yaml \
  --output artifacts/phase3-scripted-report.json
```

Run the white-box confirmation on Thor:

```bash
agent-defense-evals phase3-white-box \
  --config configs/experiments/phase3_white_box_7b.yaml \
  --output artifacts/phase3-white-box-7b-report.json
```

Run the Phase 4 coalition and topology experiment:

```bash
agent-defense-evals phase4-run \
  --config configs/experiments/phase4_coalitional_hyperproperties.yaml \
  --output artifacts/phase4-report.json
```

Run the heterogeneous Phase 4 model audit on Thor:

```bash
agent-defense-evals phase4-model-audit \
  --config configs/experiments/phase4_heterogeneous_model_audit.yaml \
  --output artifacts/phase4-model-audit.json
```
