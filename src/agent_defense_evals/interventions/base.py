"""First-class intervention boundary for later causal experiments."""

from typing import Any, Protocol


class Intervention(Protocol):
    intervention_id: str

    def apply(self, state: dict[str, Any]) -> dict[str, Any]: ...


class NoOpIntervention:
    intervention_id = "none"

    def apply(self, state: dict[str, Any]) -> dict[str, Any]:
        return dict(state)
