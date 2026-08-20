from typing import Any

import pytest

torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")

from agent_defense_evals.models.transformers_runtime import (  # noqa: E402
    TransformersWhiteBoxRuntime,
)
from agent_defense_evals.models.types import (  # noqa: E402
    ActivationPatchSpec,
    GenerationRequest,
    ModelCaptureSpec,
)


class TinyTokenizer:
    pad_token_id = 0
    eos_token_id = None

    def __call__(self, text: str, *, return_tensors: str) -> dict[str, Any]:
        assert return_tensors == "pt"
        token_ids = [3 + (ord(character) % 29) for character in text] or [1]
        input_ids = torch.tensor([token_ids], dtype=torch.long)
        return {
            "input_ids": input_ids,
            "attention_mask": torch.ones_like(input_ids),
        }

    def decode(self, token_ids: Any, *, skip_special_tokens: bool) -> str:
        del skip_special_tokens
        return " ".join(f"token-{int(token_id)}" for token_id in token_ids)


def build_tiny_runtime(device: str) -> TransformersWhiteBoxRuntime:
    config = transformers.GPT2Config(
        vocab_size=32,
        n_positions=16,
        n_ctx=16,
        n_embd=16,
        n_layer=2,
        n_head=2,
        bos_token_id=1,
        eos_token_id=None,
        pad_token_id=0,
    )
    model = transformers.GPT2LMHeadModel(config)
    return TransformersWhiteBoxRuntime(model, TinyTokenizer(), device=device)


@pytest.fixture
def tiny_runtime() -> TransformersWhiteBoxRuntime:
    return build_tiny_runtime("cpu")


def test_tiny_model_generation_is_deterministic_and_capturable(
    tiny_runtime: TransformersWhiteBoxRuntime,
) -> None:
    request = GenerationRequest(
        prompt="abc",
        max_new_tokens=2,
        seed=17,
        capture=ModelCaptureSpec(
            logits=True,
            hidden_states=True,
            module_names=("transformer.h.0",),
        ),
    )

    first = tiny_runtime.generate(request)
    second = tiny_runtime.generate(request)

    assert first.generated_token_ids == second.generated_token_ids
    assert first.token_logprobs == second.token_logprobs
    assert len(first.generated_token_ids) == 2
    assert len(first.token_logprobs) == 2
    assert len(first.step_logits) == 2
    assert len(first.hidden_states) == 2
    assert first.module_outputs["transformer.h.0"]
    assert tiny_runtime.capabilities.activation_patch


def test_zero_patch_changes_downstream_logits_and_removes_hooks(
    tiny_runtime: TransformersWhiteBoxRuntime,
) -> None:
    baseline = tiny_runtime.generate(
        GenerationRequest(prompt="abc", max_new_tokens=1, seed=23)
    )
    patched = tiny_runtime.generate(
        GenerationRequest(
            prompt="abc",
            max_new_tokens=1,
            seed=23,
            patches=(ActivationPatchSpec(module_name="transformer.h.0"),),
        )
    )

    assert patched.metadata["patch_applied_counts"]["transformer.h.0"] > 0
    assert not torch.allclose(baseline.step_logits[0], patched.step_logits[0])
    assert not tiny_runtime.model.transformer.h[0]._forward_hooks


@pytest.mark.skipif(
    not torch.backends.mps.is_available(),
    reason="MPS is unavailable in this execution environment",
)
def test_tiny_model_generation_and_patch_on_mps() -> None:
    runtime = build_tiny_runtime("mps")

    result = runtime.generate(
        GenerationRequest(
            prompt="abc",
            max_new_tokens=1,
            seed=29,
            patches=(ActivationPatchSpec(module_name="transformer.h.0"),),
        )
    )

    assert len(result.generated_token_ids) == 1
    assert result.metadata["device"] == "mps"
    assert result.metadata["patch_applied_counts"]["transformer.h.0"] > 0
