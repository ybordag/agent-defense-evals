from typing import Any

import pytest

from agent_defense_evals.models.openai_runtime import OpenAICompatibleRuntime
from agent_defense_evals.models.types import (
    GenerationRequest,
    ModelCaptureSpec,
)


def test_openai_runtime_maps_completion_and_provenance() -> None:
    captured: dict[str, Any] = {}

    def transport(
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str],
        timeout: float,
    ) -> dict[str, Any]:
        captured.update(
            url=url,
            payload=payload,
            headers=headers,
            timeout=timeout,
        )
        return {
            "id": "completion-1",
            "prompt_token_ids": [10, 11],
            "usage": {"prompt_tokens": 2, "completion_tokens": 2},
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"kind":"noop","recipient_ids":[],"payload":{}}'
                        )
                    },
                    "token_ids": [12, 13],
                    "finish_reason": "stop",
                    "logprobs": {
                        "content": [
                            {"token": "a", "logprob": -0.1},
                            {"token": "b", "logprob": -0.2},
                        ]
                    },
                }
            ],
        }

    runtime = OpenAICompatibleRuntime(
        base_url="http://model.test/v1/",
        model_id="test-model",
        model_revision="revision-1",
        timeout=12.0,
        transport=transport,
    )
    result = runtime.generate(
        GenerationRequest(
            prompt="act",
            max_new_tokens=8,
            seed=7,
            capture=ModelCaptureSpec(logits=False),
            response_schema={"type": "object"},
        )
    )

    assert captured["url"] == "http://model.test/v1/chat/completions"
    assert captured["payload"]["temperature"] == 0.0
    assert captured["payload"]["logprobs"] is True
    assert captured["payload"]["return_token_ids"] is True
    assert captured["payload"]["response_format"]["type"] == "json_schema"
    assert result.generated_token_ids == (12, 13)
    assert result.token_logprobs == (-0.1, -0.2)
    assert result.identity is not None
    assert result.identity.model_id == "test-model"
    assert runtime.capabilities.remote_serving


def test_openai_runtime_rejects_white_box_requests() -> None:
    runtime = OpenAICompatibleRuntime(
        base_url="http://model.test/v1",
        model_id="test-model",
        transport=lambda *_: {},
    )

    with pytest.raises(ValueError, match="full logits"):
        runtime.generate(GenerationRequest(prompt="act"))
