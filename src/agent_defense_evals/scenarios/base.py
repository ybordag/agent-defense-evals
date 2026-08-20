"""Scenario contract."""

from typing import Any, Protocol
from uuid import UUID

from agent_defense_evals.core.schemas import (
    AgentAction,
    Observation,
    SecurityOutcome,
    UtilityOutcome,
)


class Scenario(Protocol):
    agent_ids: tuple[str, ...]

    def reset(self, episode_id: UUID, seed: int) -> None: ...

    def observe(self, agent_id: str, step: int) -> Observation: ...

    def apply(self, action: AgentAction) -> None: ...

    def is_terminal(self) -> bool: ...

    def snapshot(self) -> dict[str, Any]: ...

    def utility_outcome(self) -> UtilityOutcome: ...

    def security_outcome(self) -> SecurityOutcome: ...
