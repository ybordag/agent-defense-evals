"""Stable seed and identifier derivation."""

import hashlib
import json
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from agent_defense_evals.core.schemas import ExperimentSpec


def derive_seed(base_seed: int, namespace: str, index: int) -> int:
    payload = f"{base_seed}:{namespace}:{index}".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def derive_run_id(spec: ExperimentSpec) -> UUID:
    payload = stable_json(spec.model_dump(mode="json"))
    return uuid5(NAMESPACE_URL, payload)


def derive_episode_id(run_id: UUID, episode_seed: int) -> UUID:
    return uuid5(run_id, str(episode_seed))


def derive_event_id(
    episode_id: UUID,
    logical_time: int,
    kind: str,
    actor_id: str | None,
) -> UUID:
    return uuid5(episode_id, f"{logical_time}:{kind}:{actor_id or '-'}")
