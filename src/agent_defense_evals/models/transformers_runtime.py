"""Direct PyTorch/Transformers runtime for white-box experiments."""

from collections import defaultdict
from collections.abc import Callable
from contextlib import ExitStack
from typing import Any

from agent_defense_evals.models.types import (
    ActivationPatchSpec,
    GenerationRequest,
    GenerationResult,
    PatchMode,
    RuntimeCapabilities,
)

try:
    import torch
except ImportError:  # pragma: no cover - exercised by minimal installations
    torch = None  # type: ignore[assignment]


def _require_torch() -> Any:
    if torch is None:
        raise RuntimeError(
            "TransformersWhiteBoxRuntime requires the 'local-model' extra"
        )
    return torch


class TransformersWhiteBoxRuntime:
    """Single-request runtime with capture and causal intervention hooks."""

    def __init__(
        self,
        model: Any,
        tokenizer: Any,
        *,
        device: str | None = None,
    ) -> None:
        torch_module = _require_torch()
        self.model = model
        self.tokenizer = tokenizer
        self.device = device or (
            "mps" if torch_module.backends.mps.is_available() else "cpu"
        )
        self.model.to(self.device)
        self.model.eval()

    @classmethod
    def from_pretrained(
        cls,
        model_id: str,
        *,
        device: str | None = None,
        revision: str | None = None,
        trust_remote_code: bool = False,
    ) -> "TransformersWhiteBoxRuntime":
        _require_torch()
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:  # pragma: no cover - dependency error path
            raise RuntimeError(
                "TransformersWhiteBoxRuntime requires the 'local-model' extra"
            ) from exc
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            revision=revision,
            trust_remote_code=trust_remote_code,
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            revision=revision,
            trust_remote_code=trust_remote_code,
            torch_dtype="auto",
        )
        return cls(model, tokenizer, device=device)

    @property
    def capabilities(self) -> RuntimeCapabilities:
        return RuntimeCapabilities(
            generation=True,
            token_logprobs=True,
            hidden_states=True,
            activation_capture=True,
            activation_patch=True,
            batching=False,
            remote_serving=False,
        )

    def _named_modules(self) -> dict[str, Any]:
        return dict(self.model.named_modules())

    def _validate_request(self, request: GenerationRequest) -> None:
        modules = self._named_modules()
        requested = set(request.capture.module_names)
        requested.update(patch.module_name for patch in request.patches)
        missing = requested - set(modules)
        if missing:
            raise ValueError(f"unknown model modules: {sorted(missing)}")
        for patch in request.patches:
            patch.replacement_required()

    def _patch_tensor(self, value: Any, patch: ActivationPatchSpec) -> Any:
        torch_module = _require_torch()
        if not torch_module.is_tensor(value):
            raise TypeError(f"module {patch.module_name} did not return a tensor")
        patched = value.clone()
        token_index = patch.token_index
        if not -patched.shape[-2] <= token_index < patched.shape[-2]:
            raise IndexError(
                f"token index {token_index} is invalid for shape {tuple(patched.shape)}"
            )
        if patch.mode is PatchMode.ZERO:
            patched[..., token_index, :] = 0
            return patched
        replacement = torch_module.tensor(
            patch.replacement,
            dtype=patched.dtype,
            device=patched.device,
        )
        if replacement.shape != patched.shape[-1:]:
            raise ValueError(
                "replacement width must match the module hidden dimension"
            )
        patched[..., token_index, :] = replacement
        return patched

    def _hook_for(
        self,
        module_name: str,
        *,
        capture: bool,
        patches: tuple[ActivationPatchSpec, ...],
        captured: dict[str, list[Any]],
        patch_counts: dict[str, int],
    ) -> Callable[..., Any]:
        def hook(module: Any, inputs: tuple[Any, ...], output: Any) -> Any:
            del module, inputs
            is_tuple = isinstance(output, tuple)
            primary = output[0] if is_tuple else output
            if capture:
                captured[module_name].append(primary.detach().cpu())
            patched = primary
            for patch in patches:
                patched = self._patch_tensor(patched, patch)
                patch_counts[module_name] += 1
            if patched is primary:
                return output
            if is_tuple:
                return (patched, *output[1:])
            return patched

        return hook

    def generate(self, request: GenerationRequest) -> GenerationResult:
        torch_module = _require_torch()
        self._validate_request(request)
        encoded = self.tokenizer(request.prompt, return_tensors="pt")
        model_inputs = {
            key: value.to(self.device)
            for key, value in encoded.items()
            if torch_module.is_tensor(value)
        }
        input_ids = model_inputs["input_ids"]
        input_length = input_ids.shape[-1]
        modules = self._named_modules()
        captured: dict[str, list[Any]] = defaultdict(list)
        patch_counts: dict[str, int] = defaultdict(int)
        patches_by_module: dict[str, list[ActivationPatchSpec]] = defaultdict(list)
        for patch in request.patches:
            patches_by_module[patch.module_name].append(patch)
        hooked_modules = set(request.capture.module_names) | set(patches_by_module)

        torch_module.manual_seed(request.seed)
        if self.device == "mps":
            torch_module.mps.manual_seed(request.seed)

        with ExitStack() as stack:
            for module_name in sorted(hooked_modules):
                handle = modules[module_name].register_forward_hook(
                    self._hook_for(
                        module_name,
                        capture=module_name in request.capture.module_names,
                        patches=tuple(patches_by_module[module_name]),
                        captured=captured,
                        patch_counts=patch_counts,
                    )
                )
                stack.callback(handle.remove)

            generation_kwargs: dict[str, Any] = {
                "max_new_tokens": request.max_new_tokens,
                "do_sample": request.do_sample,
                "return_dict_in_generate": True,
                "output_scores": True,
                "output_hidden_states": request.capture.hidden_states,
                "pad_token_id": self._pad_token_id(),
            }
            eos_token_id = getattr(self.tokenizer, "eos_token_id", None)
            if eos_token_id is not None:
                generation_kwargs["eos_token_id"] = eos_token_id
            if request.do_sample:
                generation_kwargs["temperature"] = request.temperature

            with torch_module.inference_mode():
                output = self.model.generate(**model_inputs, **generation_kwargs)

        sequence = output.sequences[0]
        generated = sequence[input_length:]
        scores = tuple(output.scores or ())
        logprobs = tuple(
            float(torch_module.log_softmax(score[0], dim=-1)[token_id].item())
            for score, token_id in zip(scores, generated, strict=True)
        )
        hidden_states = tuple(
            tuple(layer.detach().cpu() for layer in step)
            for step in (output.hidden_states or ())
        )
        return GenerationResult(
            text=self.tokenizer.decode(generated, skip_special_tokens=True),
            prompt_token_ids=tuple(map(int, input_ids[0].detach().cpu().tolist())),
            generated_token_ids=tuple(map(int, generated.detach().cpu().tolist())),
            token_logprobs=logprobs,
            step_logits=(
                tuple(score.detach().cpu() for score in scores)
                if request.capture.logits
                else ()
            ),
            hidden_states=hidden_states,
            module_outputs={
                name: tuple(values) for name, values in captured.items()
            },
            metadata={
                "runtime": type(self).__name__,
                "model_class": type(self.model).__name__,
                "device": self.device,
                "seed": request.seed,
                "patch_applied_counts": dict(patch_counts),
            },
        )

    def _pad_token_id(self) -> int:
        for source in (self.tokenizer, self.model.config):
            value = getattr(source, "pad_token_id", None)
            if value is not None:
                return int(value)
        eos_token_id = getattr(self.tokenizer, "eos_token_id", None)
        return int(eos_token_id) if eos_token_id is not None else 0
