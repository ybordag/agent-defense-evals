# Reviewer evidence rerun - 2026-08-21

## Provenance

- Code revision used for the model reruns: `3141882` (`Retain model canary episode traces`)
- Code revision recorded in the synthetic manifest: `3e77926`
- Model host: `spark-thor`
- Model runtime: vLLM OpenAI-compatible endpoint at `http://127.0.0.1:8000/v1`
- Model: `Qwen/Qwen2.5-7B-Instruct`
- Model revision: `a09a35458c702b33eeacc393d103063234e8bc28`
- Sampling: deterministic generation in the registered capacity and workflow configs

## Files

| File | Records | SHA-256 |
|---|---:|---|
| `phase7-model-capacity-7b-vllm-trace-complete.json` | 64 episodes | `41b94832eba158545e9f59756db63536e0c297345d859d6463647ab4ec5ad0fd` |
| `phase7-model-workflow-7b-vllm-trace-complete.json` | 24 episodes | `f6993ee0954107e2fb24a5706c1749cc753b5cbf2812938dadedb80b14ee82ea` |
| `tail-manifest.json` | 2,400 assignments | `ab1223edc27ce6eb4b3951bdc75f32eb6fa5cd9446b08da0ead9a8a01b65fe7b` |
| `tail-validation.json` | 1,200 outcomes | `c6b67fdaaf451d1bb4141193b5bb88a838714623ed8c4607349616a2fe0252db` |
| `tail-selection.json` | 5 selector decisions | `1f3ac9132aebff1333b44926a7c3b10ced039a7755f3215478f336643d7ac80f` |
| `tail-test.json` | 1,200 outcomes | `17be6be35d737b681ca1d8af9207e2b8d9def2e534c92f9e38b2ded18cc95bb2` |
| `tail-report.json` | E01-E05 report | `5c5d62c2e4b16905917ae53d82b79e1d46a715a5bc7fb6663da6534eb74da196` |

The SHA-256 values above hash the complete files as stored in this directory. The report files also contain internal hashes defined by the harness; those cover canonical experiment payloads and may differ from whole-file hashes.

## Verification summary

- Capacity: 64 of 64 episode records contain full trace events and trace hashes; all eight registered gates pass.
- Workflow: 24 of 24 episode records contain full trace events and trace hashes; all eight registered gates pass.
- Synthetic tail suite: all five registered selectors chose `diverse-stack`; E01 remains false, E02/E03/E05 pass as controlled fixtures, and E04 remains false.

## Claim boundary

The model-backed attacks execute supplied or registered policies. These artifacts do not demonstrate autonomous collusion discovery, stack-specific best-response search, or transfer to a genuinely different held-out model family.
