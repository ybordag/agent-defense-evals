# Phase 2 Runtime and Environment Plan

## Current status

The white-box runtime is implemented and verified with both tiny random models and Qwen2.5-7B-Instruct. CPU tests cover deterministic generation, token log probabilities, all-layer hidden states, selected-module capture, and downstream-logit changes under a zero activation patch. A separate unsandboxed test confirms generation and activation patching on the Apple M2 Metal GPU.

The runtime is installed in an isolated environment on `spark-thor`. The common model policy, OpenAI-compatible adapter, vLLM structured generation, 7B direct execution, generation provenance, and CUDA activation patching are verified. Phase 2 is complete.

## Runtime decision

Phase 2 uses two model runtimes behind one capability-aware interface:

1. `TransformersWhiteBoxRuntime` is the primary runtime for causal experiments. It runs a Hugging Face causal language model directly through PyTorch and supports logits, hidden states, selected module outputs, and activation interventions.
2. `OpenAICompatibleRuntime` is the high-throughput behavioral runtime tested against vLLM 0.23. It supports chat or text completions, token log probabilities, returned token identifiers, usage-derived token counts, structured JSON output, and remote model provenance. It is not the activation-patching path.

Runtime identity is an experimental variable. Results from different kernels or serving engines must not be treated as bitwise-equivalent even when they use the same checkpoint and sampling configuration.

## Local environment

The current development machine is an Apple M2 MacBook Air with 24 GB unified memory and a Metal GPU. It is appropriate for:

- developing the runtime contracts;
- CPU/MPS generation with small models;
- hidden-state and selected-module capture;
- activation-hook and patching tests;
- scripted/model agent integration;
- tiny randomly initialized models requiring no weight download;
- limited quantized behavioral inference.

It is not the intended environment for vLLM, high-throughput 7–9B sweeps, full-layer activation retention, or multi-agent GPU parallelism.

## Cluster environment

The two-node NVIDIA DGX Spark cluster is the intended environment for:

- 7–9B BF16/FP16 execution;
- vLLM serving and batched behavioral rollouts;
- activation capture and patch sweeps;
- probe training;
- homogeneous and heterogeneous multi-agent batches;
- long-horizon and attack/defense parameter sweeps.

The following inventory is verified for `spark-thor`:

- SSH alias: `spark-thor` over Tailscale;
- OS: Ubuntu 24.04 on ARM64;
- accelerator: one NVIDIA GB10, compute capability 12.1;
- memory: approximately 119 GiB unified memory;
- driver: 580.95.05;
- CUDA toolkit: 13.0;
- Python: 3.12.3;
- repository clone: `/home/yashi/Code/agent-defense-evals`;
- project environment: `/home/yashi/Code/agent-defense-evals/.venv`;
- project PyTorch: 2.11.0+cu130 with CUDA available;
- project Transformers: 5.15.1;
- existing serving environment: `/home/yashi/venvs/fairlead-vllm-managed`;
- existing server: vLLM 0.23.0 serving `Qwen/Qwen2.5-0.5B-Instruct` on port 8000.
- cached acceptance checkpoint: `Qwen/Qwen2.5-7B-Instruct`, revision `a09a35458c702b33eeacc393d103063234e8bc28`.

The second node still requires the same read-only inventory. Before multi-node execution, capture:

- node hostnames and SSH aliases;
- OS and architecture;
- GPU model, count, memory, driver, and CUDA versions;
- inter-node topology and available networking;
- local and shared storage;
- Python, container, PyTorch, Transformers, and vLLM versions;
- scheduler or process-management constraints;
- model-cache location and Hugging Face credentials policy.

## Phase 2 acceptance gates

- optional ML imports do not affect Phase 0–1 installations;
- runtime capabilities are explicit and serializable;
- a tiny local causal model generates deterministically under a fixed seed;
- sampled-token log probabilities are returned;
- all-layer hidden states can be requested;
- selected module outputs can be captured by name;
- a zero or replacement patch changes downstream logits;
- hooks are removed after every request, including failed requests;
- existing Phase 0–1 tests continue to pass without model downloads.
- model-derived actions traverse the existing attack, defense, and scenario boundaries;
- model and sampling provenance is recorded in `model_generated` events;
- capture descriptors carry exact prompt/completion or forward-pass token spans;
- the 7B acceptance episode selects the jointly feasible optimal plan;
- a 7B layer intervention changes downstream logits and the selected token.

## Dependency reproduction

`pyproject.toml` defines supported dependency ranges and optional groups. `requirements.txt` installs the complete local development environment. The exact environment used on the Apple Silicon development machine is recorded in `requirements/locks/macos-arm64-py312.txt` and should be supplied to pip as a constraints file.

The verified Thor environment is recorded in `requirements/locks/linux-arm64-cu130-py312.txt`. PyTorch must first be installed from the official CUDA 13 wheel index because the `+cu130` build is not available from the default Python package index:

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

Both the project environment and the known-good vLLM environment report `nvidia-cusparselt-cu13 0.8.0 is not supported on this platform` from `pip check`. Despite that metadata warning, CUDA tensor execution, the Transformers activation-patch smoke test, and vLLM generation all succeed. Preserve the warning in environment reports and re-evaluate it when the NVIDIA/PyTorch wheel set changes.

## Deployment workflow

GitHub is the source of truth. The Thor clone uses the public HTTPS remote and therefore needs no GitHub credential for read-only deployment.

1. Verify, commit, and push changes from the development machine.
2. On Thor, run `git -C /home/yashi/Code/agent-defense-evals pull --ff-only`.
3. If dependency declarations changed, reinstall using the Linux/CUDA lock above.
4. Run `.venv/bin/python -m pytest -q` and `.venv/bin/ruff check .`.
5. Verify `torch.cuda.is_available()` and the recorded GPU identity.
6. Verify the vLLM models endpoint before behavioral sweeps.

Do not install the project into the managed vLLM environment. The project runtime and server remain separate so that white-box dependency changes cannot destabilize the serving process.

## Verified Thor acceptance checks

- clean deployment from GitHub `main`;
- 24 tests pass with the MPS-only test skipped;
- Ruff passes;
- CLI entry point runs;
- CUDA reports an NVIDIA GB10 and completes a tensor operation;
- a tiny direct Transformers model generates on CUDA;
- a forward-hook zero patch is applied on CUDA;
- the vLLM chat-completions endpoint returns a valid generation.
- the vLLM-backed 0.5B episode completes and records a security violation after a reasoning error;
- the direct 7B episode completes in three steps with utility 1.0 and security loss 0.0;
- zeroing `model.layers.0` changes the 7B next token from 1249 to 11 and produces a maximum absolute logit delta of approximately 27.77.

## Cluster connection gates

- both nodes are reachable using non-interactive SSH after initial setup;
- host keys are pinned;
- a read-only inventory command succeeds on both nodes;
- no model or package installation begins before the inventory is reviewed;
- one shared model-cache strategy is selected;
- secrets remain outside repository configuration and event logs.
