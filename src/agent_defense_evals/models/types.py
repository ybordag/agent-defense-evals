"""Serializable runtime requests and auditable in-memory generation results."""

import hashlib
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from pydantic import Field, model_validator

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


class ModelIdentity(FrozenModel):
    """Stable model/runtime identity recorded with every generation."""

    runtime: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    model_revision: str | None = None
    tokenizer_id: str | None = None
    tokenizer_revision: str | None = None
    adapter_id: str | None = None
    adapter_revision: str | None = None
    endpoint: str | None = None


class TokenSpan(FrozenModel):
    """Half-open token span in the combined prompt/completion sequence."""

    start: int = Field(ge=0)
    end: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_order(self) -> "TokenSpan":
        if self.end < self.start:
            raise ValueError("token span end must not precede start")
        return self


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
    top_p: float = Field(default=1.0, gt=0.0, le=1.0)
    seed: int = Field(default=0, ge=0, le=2**63 - 1)
    stop: tuple[str, ...] = ()
    response_schema: dict[str, Any] | None = None
    capture: ModelCaptureSpec = ModelCaptureSpec()
    patches: tuple[ActivationPatchSpec, ...] = ()


@dataclass(frozen=True)
class GenerationResult:
    text: str
    prompt_token_ids: tuple[int, ...]
    generated_token_ids: tuple[int, ...]
    token_logprobs: tuple[float, ...]
    prompt_token_count: int | None = None
    generated_token_count: int | None = None
    step_logits: tuple[Any, ...] = ()
    hidden_states: tuple[tuple[Any, ...], ...] = ()
    module_outputs: dict[str, tuple[Any, ...]] = field(default_factory=dict)
    identity: ModelIdentity | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def _tensor_descriptor(value: Any, token_span: TokenSpan) -> dict[str, Any]:
    shape = tuple(int(dimension) for dimension in getattr(value, "shape", ()))
    return {
        "shape": shape,
        "dtype": str(getattr(value, "dtype", type(value).__name__)),
        "token_span": token_span.model_dump(mode="json"),
    }


def _input_span(
    value: Any,
    *,
    call_index: int,
    prompt_tokens: int,
) -> TokenSpan:
    shape = tuple(int(dimension) for dimension in getattr(value, "shape", ()))
    sequence_length = shape[-2] if len(shape) >= 2 else 0
    if call_index == 0 or sequence_length != 1:
        return TokenSpan(start=0, end=sequence_length)
    position = prompt_tokens + call_index - 1
    return TokenSpan(start=position, end=position + 1)


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return str(value)


def generation_event_payload(
    request: GenerationRequest,
    result: GenerationResult,
) -> dict[str, Any]:
    """Build a JSON-safe provenance payload without storing raw activations."""

    prompt_tokens = (
        result.prompt_token_count
        if result.prompt_token_count is not None
        else len(result.prompt_token_ids)
    )
    completion_tokens = (
        result.generated_token_count
        if result.generated_token_count is not None
        else len(result.generated_token_ids)
    )
    completion_start = prompt_tokens
    patch_manifest = []
    for patch in request.patches:
        replacement_hash = None
        if patch.replacement is not None:
            replacement_hash = hashlib.sha256(
                json.dumps(patch.replacement, separators=(",", ":")).encode()
            ).hexdigest()
        patch_manifest.append(
            {
                "module_name": patch.module_name,
                "token_index": patch.token_index,
                "mode": patch.mode.value,
                "replacement_sha256": replacement_hash,
            }
        )

    logits = [
        {
            "step": step,
            **_tensor_descriptor(
                value,
                TokenSpan(
                    start=completion_start + step,
                    end=completion_start + step + 1,
                ),
            ),
        }
        for step, value in enumerate(result.step_logits)
    ]
    hidden_states = []
    for step, layers in enumerate(result.hidden_states):
        for layer, value in enumerate(layers):
            hidden_states.append(
                {
                    "step": step,
                    "layer": layer,
                    **_tensor_descriptor(
                        value,
                        _input_span(
                            value,
                            call_index=step,
                            prompt_tokens=prompt_tokens,
                        ),
                    ),
                }
            )
    module_outputs = []
    for module_name, values in sorted(result.module_outputs.items()):
        for call_index, value in enumerate(values):
            module_outputs.append(
                {
                    "module_name": module_name,
                    "call_index": call_index,
                    **_tensor_descriptor(
                        value,
                        _input_span(
                            value,
                            call_index=call_index,
                            prompt_tokens=prompt_tokens,
                        ),
                    ),
                }
            )

    return {
        "model": (
            result.identity.model_dump(mode="json") if result.identity else None
        ),
        "prompt": {
            "sha256": hashlib.sha256(request.prompt.encode()).hexdigest(),
            "characters": len(request.prompt),
            "token_span": TokenSpan(start=0, end=prompt_tokens).model_dump(
                mode="json"
            ),
        },
        "completion": {
            "text": result.text,
            "token_span": TokenSpan(
                start=completion_start,
                end=completion_start + completion_tokens,
            ).model_dump(mode="json"),
            "token_ids": list(result.generated_token_ids),
            "token_logprobs": list(result.token_logprobs),
        },
        "sampling": {
            "max_new_tokens": request.max_new_tokens,
            "do_sample": request.do_sample,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "seed": request.seed,
            "stop": list(request.stop),
            "response_schema": request.response_schema,
        },
        "capture": {
            "requested": request.capture.model_dump(mode="json"),
            "logits": logits,
            "hidden_states": hidden_states,
            "module_outputs": module_outputs,
            "patches": patch_manifest,
        },
        "runtime_metadata": _json_safe(result.metadata),
    }
