"""Serializable runtime requests and in-memory generation results."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from pydantic import Field

from agent_defense_evals.core.schemas import FrozenModel


class PatchMode(StrEnum):
    ZERO = "zero"
    REPLACE = "replace"


class RuntimeCapabilities(FrozenModel):
    generation: bool = True
    token_logprobs: bool = False
    hidden_states: bool = False
    activation_capture: bool = False
    activation_patch: bool = False
    batching: bool = False
    remote_serving: bool = False


class ModelCaptureSpec(FrozenModel):
    logits: bool = True
    hidden_states: bool = False
    module_names: tuple[str, ...] = ()


class ActivationPatchSpec(FrozenModel):
    module_name: str = Field(min_length=1)
    token_index: int = -1
    mode: PatchMode = PatchMode.ZERO
    replacement: tuple[float, ...] | None = None

    def replacement_required(self) -> None:
        if self.mode is PatchMode.REPLACE and self.replacement is None:
            raise ValueError("replacement values are required for replace patches")


class GenerationRequest(FrozenModel):
    prompt: str
    max_new_tokens: int = Field(default=16, ge=1, le=4096)
    do_sample: bool = False
    temperature: float = Field(default=1.0, gt=0.0)
    seed: int = Field(default=0, ge=0)
    capture: ModelCaptureSpec = ModelCaptureSpec()
    patches: tuple[ActivationPatchSpec, ...] = ()


@dataclass(frozen=True)
class GenerationResult:
    text: str
    prompt_token_ids: tuple[int, ...]
    generated_token_ids: tuple[int, ...]
    token_logprobs: tuple[float, ...]
    step_logits: tuple[Any, ...] = ()
    hidden_states: tuple[tuple[Any, ...], ...] = ()
    module_outputs: dict[str, tuple[Any, ...]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
