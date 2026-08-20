# Phase 2 Runtime and Environment Plan

## Current status

The local white-box runtime foundation is implemented and verified with a tiny randomly initialized causal model. CPU tests cover deterministic generation, token log probabilities, all-layer hidden states, selected-module capture, and downstream-logit changes under a zero activation patch. A separate unsandboxed test confirms generation and activation patching on the Apple M2 Metal GPU. No pretrained model weights have been downloaded.

The remaining local integration task is connecting model-backed policies to the Phase 1 agent interface. The next environment task is inventorying and configuring the two-node DGX Spark cluster before adding vLLM or a 7–9B checkpoint.

## Runtime decision

Phase 2 uses two model runtimes behind one capability-aware interface:

1. `TransformersWhiteBoxRuntime` is the primary runtime for causal experiments. It runs a Hugging Face causal language model directly through PyTorch and supports logits, hidden states, selected module outputs, and activation interventions.
2. A later `VLLMRuntime` is the high-throughput behavioral runtime. It will support scalable generation and log probabilities, but is not the primary activation-patching path.

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

Before cluster installation, capture:

- node hostnames and SSH aliases;
- OS and architecture;
- GPU model, count, memory, driver, and CUDA versions;
- inter-node topology and available networking;
- local and shared storage;
- Python, container, PyTorch, Transformers, and vLLM versions;
- scheduler or process-management constraints;
- model-cache location and Hugging Face credentials policy.

## Local Phase 2 acceptance gates

- optional ML imports do not affect Phase 0–1 installations;
- runtime capabilities are explicit and serializable;
- a tiny local causal model generates deterministically under a fixed seed;
- sampled-token log probabilities are returned;
- all-layer hidden states can be requested;
- selected module outputs can be captured by name;
- a zero or replacement patch changes downstream logits;
- hooks are removed after every request, including failed requests;
- existing Phase 0–1 tests continue to pass without model downloads.

## Dependency reproduction

`pyproject.toml` defines supported dependency ranges and optional groups. `requirements.txt` installs the complete local development environment. The exact environment used on the Apple Silicon development machine is recorded in `requirements/locks/macos-arm64-py312.txt` and should be supplied to pip as a constraints file.

The DGX environment requires a separate lock because Linux/CUDA PyTorch and vLLM artifacts are not interchangeable with macOS ARM64 packages.

## Cluster connection gates

- both nodes are reachable using non-interactive SSH after initial setup;
- host keys are pinned;
- a read-only inventory command succeeds on both nodes;
- no model or package installation begins before the inventory is reviewed;
- one shared model-cache strategy is selected;
- secrets remain outside repository configuration and event logs.
