from uuid import UUID

import pytest

from agent_defense_evals.agents.model import ModelOutputError, StructuredModelAgent
from agent_defense_evals.core.schemas import ActionKind, Observation
from agent_defense_evals.models.types import (
    GenerationRequest,
    GenerationResult,
    ModelIdentity,
    RuntimeCapabilities,
)


class FixedRuntime:
    def __init__(self, text: str) -> None:
        self.text = text
        self.requests: list[GenerationRequest] = []

    @property
    def capabilities(self) -> RuntimeCapabilities:
        return RuntimeCapabilities(generation=True)

    def generate(self, request: GenerationRequest) -> GenerationResult:
        self.requests.append(request)
        return GenerationResult(
            text=self.text,
            prompt_token_ids=(1, 2),
            generated_token_ids=(3,),
            token_logprobs=(-0.1,),
            identity=ModelIdentity(runtime="fixed", model_id="fixed-model"),
        )


def observation() -> Observation:
    return Observation(
        episode_id=UUID("00000000-0000-0000-0000-000000000001"),
        step=0,
        agent_id="analyst",
        public_state={
            "other_agents": ["coordinator"],
            "scores": {"alpha": 10.0, "beta": 8.0},
        },
        private_state={"allowed_plans": ["alpha", "beta"]},
    )


def test_model_agent_parses_action_and_enforces_actor_identity() -> None:
    runtime = FixedRuntime(
        'prefix {"kind":"message","recipient_ids":["coordinator"],'
        '"payload":{"allowed_plans":["alpha","beta"]}} trailing'
    )
    agent = StructuredModelAgent(
        "analyst",
        role="constraint-holder",
        runtime=runtime,
        base_seed=5,
    )

    decision = agent.act(observation())

    assert decision.action.actor_id == "analyst"
    assert decision.action.kind is ActionKind.MESSAGE
    assert decision.generation is not None
    assert runtime.requests[0].capture.logits is False


def test_model_agent_rejects_non_json_output() -> None:
    agent = StructuredModelAgent(
        "analyst",
        role="constraint-holder",
        runtime=FixedRuntime("I cannot decide"),
        base_seed=5,
    )

    with pytest.raises(ModelOutputError, match="no JSON"):
        agent.act(observation())


def test_model_agent_rejects_kind_specific_payload_error() -> None:
    agent = StructuredModelAgent(
        "analyst",
        role="constraint-holder",
        runtime=FixedRuntime(
            '{"kind":"select_plan","recipient_ids":[],"payload":{}}'
        ),
        base_seed=5,
    )

    with pytest.raises(ModelOutputError, match="known plan_id"):
        agent.act(observation())
