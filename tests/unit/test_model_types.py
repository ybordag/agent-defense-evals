import pytest
from pydantic import ValidationError

from agent_defense_evals.models.types import (
    ActivationPatchSpec,
    GenerationRequest,
    PatchMode,
    RuntimeCapabilities,
)


def test_runtime_capabilities_are_explicit_and_serializable() -> None:
    capabilities = RuntimeCapabilities(
        token_logprobs=True,
        hidden_states=True,
        activation_capture=True,
        activation_patch=True,
    )

    assert capabilities.model_dump()["activation_patch"] is True
    assert capabilities.remote_serving is False


def test_generation_request_rejects_invalid_token_budget() -> None:
    with pytest.raises(ValidationError):
        GenerationRequest(prompt="test", max_new_tokens=0)


def test_replace_patch_requires_values() -> None:
    patch = ActivationPatchSpec(
        module_name="layer.0",
        mode=PatchMode.REPLACE,
    )

    with pytest.raises(ValueError, match="replacement values"):
        patch.replacement_required()
