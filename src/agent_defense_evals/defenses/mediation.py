"""Deterministic and randomized message mediators for capacity shaping."""

import random
from enum import StrEnum
from typing import Any

from agent_defense_evals.core.schemas import (
    ActionKind,
    AgentAction,
    DecisionKind,
    DefenseDecision,
)
from agent_defense_evals.core.seeding import derive_seed


class MediatorKind(StrEnum):
    UNRESTRICTED = "unrestricted"
    GENERIC_PARAPHRASE = "generic_paraphrase"
    TYPED_SCHEMA = "typed_schema"
    TASK_SUMMARY = "task_summary"
    RECIPIENT_RANDOMIZED = "recipient_randomized"
    INFORMATION_BUDGET = "information_budget"


class MemoryMode(StrEnum):
    CUMULATIVE = "cumulative"
    RESET_EACH_TURN = "reset_each_turn"


class ReceiverMemoryCompartment:
    """Expose either cumulative delivered messages or only the current turn."""

    def __init__(self, mode: MemoryMode) -> None:
        self.mode = mode

    def view(self, delivered_history: tuple[Any, ...]) -> tuple[Any, ...]:
        if not delivered_history:
            return ()
        if self.mode is MemoryMode.RESET_EACH_TURN:
            return delivered_history[-1:]
        return delivered_history


class MessageMediatorDefense:
    """Transform synthetic task messages while preserving auditable task fields.

    The two integer carrier fields operationalize unauthorized surface and
    semantic degrees of freedom. Production mediators would transform text or
    typed tool calls, but use this same defense boundary.
    """

    def __init__(
        self,
        kind: MediatorKind,
        *,
        base_seed: int,
        information_budget_bits: int = 1,
        randomized_retention: float = 0.5,
    ) -> None:
        if information_budget_bits < 0:
            raise ValueError("information budget must be nonnegative")
        if not 0.0 <= randomized_retention <= 1.0:
            raise ValueError("randomized retention must lie in [0, 1]")
        self.kind = kind
        self.base_seed = base_seed
        self.information_budget_bits = information_budget_bits
        self.randomized_retention = randomized_retention
        self.defense_id = f"message_mediator.{kind.value}"

    @staticmethod
    def _validated_payload(action: AgentAction) -> dict[str, Any]:
        payload = dict(action.payload)
        required = {"task_id", "surface_code", "semantic_code", "round"}
        if not required.issubset(payload):
            missing = sorted(required - set(payload))
            raise ValueError(f"capacity message is missing fields: {missing}")
        payload["task_id"] = str(payload["task_id"])
        payload["surface_code"] = int(payload["surface_code"])
        payload["semantic_code"] = int(payload["semantic_code"])
        payload["round"] = int(payload["round"])
        if payload["surface_code"] < 0 or payload["semantic_code"] < 0:
            raise ValueError("capacity carrier codes must be nonnegative")
        return payload

    def _transform(
        self,
        payload: dict[str, Any],
        *,
        recipient_id: str,
        episode_seed: int,
    ) -> dict[str, Any]:
        delivered = {
            "task_id": payload["task_id"],
            "surface_code": payload["surface_code"],
            "semantic_code": payload["semantic_code"],
            "round": payload["round"],
            "mediation": self.kind.value,
        }
        if self.kind is MediatorKind.UNRESTRICTED:
            return delivered
        delivered["surface_code"] = 0
        if self.kind is MediatorKind.GENERIC_PARAPHRASE:
            return delivered
        if self.kind in {MediatorKind.TYPED_SCHEMA, MediatorKind.TASK_SUMMARY}:
            delivered["semantic_code"] = 0
            return delivered
        if self.kind is MediatorKind.INFORMATION_BUDGET:
            states = 2**self.information_budget_bits
            delivered["semantic_code"] = (
                0 if states == 1 else delivered["semantic_code"] % states
            )
            return delivered
        if self.kind is MediatorKind.RECIPIENT_RANDOMIZED:
            rng = random.Random(
                derive_seed(
                    self.base_seed,
                    f"phase6-randomized:{recipient_id}",
                    episode_seed,
                )
            )
            if rng.random() >= self.randomized_retention:
                delivered["semantic_code"] = 0
            return delivered
        raise ValueError(f"unsupported mediator: {self.kind}")

    def evaluate(
        self,
        action: AgentAction,
        *,
        step: int,
        scenario_state: dict[str, Any],
    ) -> DefenseDecision:
        del step
        if action.kind is not ActionKind.MESSAGE:
            return DefenseDecision(
                decision=DecisionKind.ALLOW,
                defense_id=self.defense_id,
                action=action,
                reason="mediator applies only to messages",
            )
        if len(action.recipient_ids) != 1:
            raise ValueError("capacity messages require exactly one recipient")
        payload = self._validated_payload(action)
        delivered = self._transform(
            payload,
            recipient_id=action.recipient_ids[0],
            episode_seed=int(scenario_state.get("episode_seed", self.base_seed)),
        )
        transformed = action.model_copy(update={"payload": delivered})
        decision = (
            DecisionKind.ALLOW if transformed == action else DecisionKind.TRANSFORM
        )
        return DefenseDecision(
            decision=decision,
            defense_id=self.defense_id,
            action=transformed,
            reason=f"applied {self.kind.value} message mediation",
        )
