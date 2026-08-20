"""Versioned data contracts for runs, episodes, and events."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "0.1.0"


class Condition(StrEnum):
    BENIGN = "benign"
    BENIGN_DEFENDED = "benign-defended"
    LEAKAGE_CONTROL = "leakage-control"
    COLLUSIVE = "collusive"
    COLLUSIVE_DEFENDED = "collusive-defended"
    SHUFFLED_TARGET = "shuffled-target"


class EventType(StrEnum):
    EPISODE_STARTED = "episode_started"
    MODEL_REQUEST_STARTED = "model_request_started"
    MESSAGE_GENERATED = "message_generated"
    LEXICAL_POLICY_VIOLATION = "lexical_policy_violation"
    MESSAGE_TRANSFORMED = "message_transformed"
    MESSAGE_DELIVERED = "message_delivered"
    AGENT_FINALIZED = "agent_finalized"
    EPISODE_SCORED = "episode_scored"
    MONITOR_DECODED = "monitor_decoded"
    COUNTERFACTUAL_SCORED = "counterfactual_scored"
    EPISODE_FAILED = "episode_failed"


class EpisodeSpec(BaseModel):
    """Immutable inputs needed to execute and replay one episode."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = SCHEMA_VERSION
    run_id: UUID
    episode_id: UUID = Field(default_factory=uuid4)
    condition: Condition
    seed: int = Field(ge=0)
    task_id: str = Field(min_length=1)
    target_word: str | None = None


class EventRecord(BaseModel):
    """Append-only event envelope used throughout the experiment."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = SCHEMA_VERSION
    event_id: UUID = Field(default_factory=uuid4)
    run_id: UUID
    episode_id: UUID
    condition: Condition
    seed: int = Field(ge=0)
    event_type: EventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: dict[str, Any] = Field(default_factory=dict)
