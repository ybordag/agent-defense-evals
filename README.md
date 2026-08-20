# Agent Defense Evals

An event-sourced evaluation harness for multi-agent AI security defenses across collusion, steganography, heterogeneous attacks, and the attack dimensions defined in Section 3.3 of the motivating research.

The current implementation covers Phases 0 and 1 plus the Phase 2 runtime foundation: immutable specifications, deterministic traces, scripted agents, defense mediation, provenance, and direct Transformers-based white-box generation and activation intervention. The runtime is verified on Apple Metal and an NVIDIA GB10/CUDA 13 host.

## Documentation

- [Documentation index](docs/README.md)
- [Defense conjectures](docs/03_defense_conjectures.md)
- [Experimental program](docs/04_experimental_program_and_transfer.md)
- [System architecture](docs/05_system_architecture.md)
- [Implementation roadmap](docs/implementation/roadmap.md)

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

## Phase 0–1 commands

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
