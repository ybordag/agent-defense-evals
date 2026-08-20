"""Agent policy contract and auditable policy decision."""

from dataclasses import dataclass
from typing import Protocol

from agent_defense_evals.core.schemas import AgentAction, Observation
from agent_defense_evals.models.types import GenerationRequest, GenerationResult


@dataclass(frozen=True)
class PolicyDecision:
    action: AgentAction
    request: GenerationRequest | None = None
    generation: GenerationResult | None = None

    def __post_init__(self) -> None:
        if (self.request is None) != (self.generation is None):
            raise ValueError("request and generation must either both be set or absent")


class AgentPolicy(Protocol):
    agent_id: str

    def act(self, observation: Observation) -> PolicyDecision: ...
