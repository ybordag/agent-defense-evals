"""OpenAI-compatible chat/completion runtime for vLLM behavioral scaling."""

import json
import os
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from agent_defense_evals.models.types import (
    GenerationRequest,
    GenerationResult,
    ModelIdentity,
    RuntimeCapabilities,
)

Transport = Callable[[str, dict[str, Any], dict[str, str], float], dict[str, Any]]


def _http_transport(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    timeout: float,
) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode(),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310
            raw = response.read().decode()
    except HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(
            f"model server returned HTTP {exc.code}: {detail[:500]}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"model server request failed: {exc.reason}") from exc
    decoded = json.loads(raw)
    if not isinstance(decoded, dict):
        raise RuntimeError("model server response must be a JSON object")
    return decoded


class OpenAICompatibleRuntime:
    """Single-request `/v1/completions` adapter tested against vLLM."""

    def __init__(
        self,
        *,
        base_url: str,
        model_id: str,
        model_revision: str | None = None,
        tokenizer_id: str | None = None,
        tokenizer_revision: str | None = None,
        adapter_id: str | None = None,
        adapter_revision: str | None = None,
        api_key_env: str | None = None,
        api_mode: str = "chat",
        timeout: float = 60.0,
        transport: Transport | None = None,
    ) -> None:
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must use HTTP or HTTPS")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if api_mode not in {"chat", "completion"}:
            raise ValueError("api_mode must be 'chat' or 'completion'")
        self.base_url = base_url.rstrip("/")
        self.model_id = model_id
        self.api_key_env = api_key_env
        self.api_mode = api_mode
        self.timeout = timeout
        self.transport = transport or _http_transport
        self.identity = ModelIdentity(
            runtime=type(self).__name__,
            model_id=model_id,
            model_revision=model_revision,
            tokenizer_id=tokenizer_id,
            tokenizer_revision=tokenizer_revision,
            adapter_id=adapter_id,
            adapter_revision=adapter_revision,
            endpoint=self.base_url,
        )

    @property
    def capabilities(self) -> RuntimeCapabilities:
        return RuntimeCapabilities(
            generation=True,
            token_logprobs=True,
            hidden_states=False,
            activation_capture=False,
            activation_patch=False,
            batching=True,
            remote_serving=True,
        )

    def _validate_request(self, request: GenerationRequest) -> None:
        if request.capture.hidden_states or request.capture.module_names:
            raise ValueError("remote runtime does not expose hidden activations")
        if request.capture.logits:
            raise ValueError("remote runtime does not expose full logits")
        if request.patches:
            raise ValueError("remote runtime does not support activation patches")

    def generate(self, request: GenerationRequest) -> GenerationResult:
        self._validate_request(request)
        payload: dict[str, Any] = {
            "model": self.model_id,
            "max_tokens": request.max_new_tokens,
            "temperature": request.temperature if request.do_sample else 0.0,
            "top_p": request.top_p,
            "seed": request.seed,
            "logprobs": 1,
            "return_token_ids": True,
        }
        if self.api_mode == "chat":
            payload["messages"] = [{"role": "user", "content": request.prompt}]
            payload["logprobs"] = True
            payload["top_logprobs"] = 1
        else:
            payload["prompt"] = request.prompt
            payload["echo"] = False
        if request.stop:
            payload["stop"] = list(request.stop)
        if request.response_schema is not None:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "agent_action",
                    "schema": request.response_schema,
                    "strict": True,
                },
            }
        headers = {"Content-Type": "application/json"}
        if self.api_key_env:
            api_key = os.environ.get(self.api_key_env)
            if not api_key:
                raise RuntimeError(
                    f"API key environment variable is unset: {self.api_key_env}"
                )
            headers["Authorization"] = f"Bearer {api_key}"
        response = self.transport(
            (
                f"{self.base_url}/chat/completions"
                if self.api_mode == "chat"
                else f"{self.base_url}/completions"
            ),
            payload,
            headers,
            self.timeout,
        )
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError("model server response contains no completion choices")
        choice = choices[0]
        if not isinstance(choice, dict):
            raise RuntimeError("model server completion choice must be an object")
        logprob_data = choice.get("logprobs") or {}
        if self.api_mode == "chat":
            content_logprobs = logprob_data.get("content") or ()
            token_logprobs = tuple(
                float(item["logprob"])
                for item in content_logprobs
                if isinstance(item, dict) and item.get("logprob") is not None
            )
            message = choice.get("message") or {}
            text = str(message.get("content", ""))
        else:
            token_logprobs = tuple(
                float(value)
                for value in (logprob_data.get("token_logprobs") or ())
                if value is not None
            )
            text = str(choice.get("text", ""))
        generated_ids = choice.get("token_ids") or logprob_data.get("token_ids") or ()
        prompt_ids = response.get("prompt_token_ids") or choice.get(
            "prompt_token_ids"
        ) or ()
        usage = response.get("usage") or {}
        return GenerationResult(
            text=text,
            prompt_token_ids=tuple(map(int, prompt_ids)),
            generated_token_ids=tuple(map(int, generated_ids)),
            token_logprobs=token_logprobs,
            prompt_token_count=usage.get("prompt_tokens"),
            generated_token_count=usage.get("completion_tokens"),
            identity=self.identity,
            metadata={
                "runtime": type(self).__name__,
                "request_id": response.get("id"),
                "finish_reason": choice.get("finish_reason"),
                "usage": usage,
            },
        )
