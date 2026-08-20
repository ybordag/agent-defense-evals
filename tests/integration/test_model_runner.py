import json
from pathlib import Path

from agent_defense_evals.agents.model import StructuredModelAgent
from agent_defense_evals.attacks.scripted import NoAttack
from agent_defense_evals.core.config import load_experiment
from agent_defense_evals.core.factory import build_scenario
from agent_defense_evals.core.runner import ExperimentRunner
from agent_defense_evals.core.schemas import EventKind
from agent_defense_evals.defenses.gateway import DefenseGateway
from agent_defense_evals.models.types import (
    GenerationRequest,
    GenerationResult,
    ModelIdentity,
    RuntimeCapabilities,
)

BASELINE = Path("configs/experiments/scripted_baseline.yaml")


class RuleRuntime:
    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id

    @property
    def capabilities(self) -> RuntimeCapabilities:
        return RuntimeCapabilities(generation=True, token_logprobs=True)

    def generate(self, request: GenerationRequest) -> GenerationResult:
        prompt = request.prompt
        if '\"step\":0' in prompt:
            other = "coordinator" if self.agent_id == "analyst" else "analyst"
            allowed = (
                ["alpha", "beta"]
                if self.agent_id == "analyst"
                else ["beta", "gamma"]
            )
            action = {
                "kind": "message",
                "recipient_ids": [other],
                "payload": {"allowed_plans": allowed},
            }
        elif self.agent_id == "coordinator":
            action = {
                "kind": "select_plan",
                "recipient_ids": [],
                "payload": {"plan_id": "beta"},
            }
        else:
            action = {"kind": "noop", "recipient_ids": [], "payload": {}}
        return GenerationResult(
            text=json.dumps(action),
            prompt_token_ids=(1, 2, 3),
            generated_token_ids=(4, 5),
            token_logprobs=(-0.1, -0.2),
            module_outputs={"layer.0": (TensorDescriptor((1, 3, 4)),)},
            identity=ModelIdentity(runtime="rule", model_id="rule-model"),
        )


class TensorDescriptor:
    def __init__(self, shape: tuple[int, ...]) -> None:
        self.shape = shape
        self.dtype = "float32"


def test_model_generation_is_a_parent_of_proposed_action() -> None:
    spec = load_experiment(BASELINE)
    agents = tuple(
        StructuredModelAgent(
            agent.agent_id,
            role=agent.role,
            runtime=RuleRuntime(agent.agent_id),
            base_seed=spec.base_seed,
        )
        for agent in spec.agents
    )
    runner = ExperimentRunner(
        spec=spec,
        scenario=build_scenario(spec),
        agents=agents,
        attack=NoAttack(),
        gateway=DefenseGateway(()),
    )

    result, trace = runner.run()

    generated = trace.by_kind(EventKind.MODEL_GENERATED)
    proposed = trace.by_kind(EventKind.ACTION_PROPOSED)
    generated_ids = {event.event_id for event in generated}
    assert result.selected_plan == "beta"
    assert len(generated) == 4
    assert all(event.parent_ids[0] in generated_ids for event in proposed)
    assert generated[0].payload["model"]["model_id"] == "rule-model"
    assert generated[0].payload["prompt"]["token_span"] == {
        "start": 0,
        "end": 3,
    }
    assert generated[0].payload["completion"]["token_span"] == {
        "start": 3,
        "end": 5,
    }
    assert generated[0].payload["capture"]["module_outputs"] == [
        {
            "module_name": "layer.0",
            "call_index": 0,
            "shape": (1, 3, 4),
            "dtype": "float32",
            "token_span": {"start": 0, "end": 3},
        }
    ]
