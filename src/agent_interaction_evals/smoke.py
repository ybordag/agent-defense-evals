"""Phase 0 acceptance-gate implementation."""

from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from agent_interaction_evals.config import ExperimentConfig, load_yaml_config
from agent_interaction_evals.events import JsonlEventSink, read_events
from agent_interaction_evals.schemas import (
    Condition,
    EpisodeSpec,
    EventRecord,
    EventType,
)
from agent_interaction_evals.seeding import derive_seed


def run_phase0_smoke(config_path: Path, output_path: Path) -> EventRecord:
    """Generate, persist, reload, and verify one deterministic episode event."""

    config = load_yaml_config(config_path, ExperimentConfig)
    run_id = uuid5(NAMESPACE_URL, f"{config.name}:{config.base_seed}")
    episode_seed = derive_seed(config.base_seed, "phase0-smoke", 0)
    episode_id = uuid5(run_id, str(episode_seed))
    episode = EpisodeSpec(
        run_id=run_id,
        episode_id=episode_id,
        condition=Condition.BENIGN,
        seed=episode_seed,
        task_id="phase0-smoke-task",
    )
    event = EventRecord(
        event_id=uuid5(episode_id, EventType.EPISODE_STARTED.value),
        run_id=episode.run_id,
        episode_id=episode.episode_id,
        condition=episode.condition,
        seed=episode.seed,
        event_type=EventType.EPISODE_STARTED,
        payload={"episode": episode.model_dump(mode="json")},
    )

    if output_path.exists():
        output_path.unlink()
    JsonlEventSink(output_path).append(event)
    restored = list(read_events(output_path))
    if restored != [event]:
        raise RuntimeError("Phase 0 event round trip did not preserve the record")
    return restored[0]
