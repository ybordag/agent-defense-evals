"""Agent policy contract."""

from typing import Protocol

from agent_defense_evals.core.schemas import AgentAction, Observation


class AgentPolicy(Protocol):
    agent_id: str

    def act(self, observation: Observation) -> AgentAction: ...
