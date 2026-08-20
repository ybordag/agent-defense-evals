"""Versioned immutable contracts shared across the harness."""

from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = "0.1.0"


class FrozenModel(BaseModel):
    """Base class for immutable, strict experiment data."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Directness(StrEnum):
    NONE = "none"
    EXPLICIT = "explicit"
    REWARD_INDUCED = "reward_induced"
    EMERGENT = "emergent"


class ActionKind(StrEnum):
    MESSAGE = "message"
    SELECT_PLAN = "select_plan"
    CREATE_ARTIFACT = "create_artifact"
    REVIEW_ARTIFACT = "review_artifact"
    APPROVE_ARTIFACT = "approve_artifact"
    EXECUTE_ARTIFACT = "execute_artifact"
    NOOP = "noop"


class EventKind(StrEnum):
    EPISODE_STARTED = "episode_started"
    OBSERVATION_EMITTED = "observation_emitted"
    MODEL_GENERATED = "model_generated"
    ACTION_PROPOSED = "action_proposed"
    ATTACK_MUTATED = "attack_mutated"
    DEFENSE_DECIDED = "defense_decided"
    ACTION_APPLIED = "action_applied"
    INTERVENTION_APPLIED = "intervention_applied"
    EPISODE_COMPLETED = "episode_completed"


class DecisionKind(StrEnum):
    ALLOW = "allow"
    TRANSFORM = "transform"
    BLOCK = "block"


class AttackDimensions(FrozenModel):
    """Operational proxies for the eight Section 3.3 dimensions."""

    detectability_target: float | None = Field(default=None, ge=0.0, le=1.0)
    coalition_size: int = Field(default=0, ge=0)
    cascade_branching: float = Field(default=0.0, ge=0.0)
    composition_depth: int = Field(default=1, ge=1)
    horizon: int = Field(default=1, ge=1)
    attribution_degradation: float = Field(default=0.0, ge=0.0, le=1.0)
    directness: Directness = Directness.NONE
    reversibility: float = Field(default=1.0, ge=0.0, le=1.0)


class ComponentSpec(FrozenModel):
    kind: str = Field(min_length=1)
    config: dict[str, Any] = Field(default_factory=dict)


class AgentSpec(FrozenModel):
    agent_id: str = Field(min_length=1)
    role: str = Field(min_length=1)
    policy: ComponentSpec


class ModelRuntimeSpec(FrozenModel):
    runtime_id: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    config: dict[str, Any] = Field(default_factory=dict)


class CaptureSpec(FrozenModel):
    events: bool = True
    activations: bool = False


class ExperimentSpec(FrozenModel):
    schema_version: str = SCHEMA_VERSION
    experiment_id: str = Field(min_length=1)
    base_seed: int = Field(ge=0)
    max_steps: int = Field(default=10, ge=1, le=10_000)
    agents: tuple[AgentSpec, ...] = Field(min_length=2)
    runtimes: tuple[ModelRuntimeSpec, ...] = ()
    scenario: ComponentSpec
    attack: ComponentSpec = ComponentSpec(kind="none")
    defenses: tuple[ComponentSpec, ...] = ()
    dimensions: AttackDimensions
    capture: CaptureSpec = CaptureSpec()

    @model_validator(mode="after")
    def validate_unique_agents(self) -> "ExperimentSpec":
        agent_ids = [agent.agent_id for agent in self.agents]
        if len(agent_ids) != len(set(agent_ids)):
            raise ValueError("agent IDs must be unique")
        runtime_ids = [runtime.runtime_id for runtime in self.runtimes]
        if len(runtime_ids) != len(set(runtime_ids)):
            raise ValueError("runtime IDs must be unique")
        configured_runtimes = set(runtime_ids)
        model_policy_kinds = {"model_action", "sequential_signal_model"}
        for agent in self.agents:
            if agent.policy.kind not in model_policy_kinds:
                continue
            runtime_id = agent.policy.config.get("runtime_id")
            if runtime_id not in configured_runtimes:
                raise ValueError(
                    f"agent {agent.agent_id} references unknown runtime: {runtime_id}"
                )
        return self


class Observation(FrozenModel):
    episode_id: UUID
    step: int = Field(ge=0)
    agent_id: str
    public_state: dict[str, Any] = Field(default_factory=dict)
    private_state: dict[str, Any] = Field(default_factory=dict)
    inbox: tuple[dict[str, Any], ...] = ()


class AgentAction(FrozenModel):
    actor_id: str
    kind: ActionKind
    recipient_ids: tuple[str, ...] = ()
    payload: dict[str, Any] = Field(default_factory=dict)


class DefenseDecision(FrozenModel):
    decision: DecisionKind
    defense_id: str
    action: AgentAction
    reason: str = ""


class UtilityOutcome(FrozenModel):
    score: float
    success: bool
    details: dict[str, Any] = Field(default_factory=dict)


class SecurityOutcome(FrozenModel):
    loss: float = Field(ge=0.0)
    violation: bool
    details: dict[str, Any] = Field(default_factory=dict)


class EventRecord(FrozenModel):
    schema_version: str = SCHEMA_VERSION
    event_id: UUID
    experiment_id: str
    episode_id: UUID
    step: int = Field(ge=0)
    logical_time: int = Field(ge=0)
    actor_id: str | None = None
    recipient_ids: tuple[str, ...] = ()
    kind: EventKind
    parent_ids: tuple[UUID, ...] = ()
    payload: dict[str, Any] = Field(default_factory=dict)
    risk_level: float = Field(default=0.0, ge=0.0, le=1.0)
    reversible: bool = True


class EpisodeResult(FrozenModel):
    experiment_id: str
    episode_id: UUID
    run_id: UUID
    steps: int = Field(ge=0)
    selected_plan: str | None
    utility: UtilityOutcome
    security: SecurityOutcome
    event_count: int = Field(ge=1)
