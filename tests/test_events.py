from pathlib import Path
from uuid import uuid4

from agent_interaction_evals.events import JsonlEventSink, read_events
from agent_interaction_evals.schemas import Condition, EventRecord, EventType


def test_jsonl_event_round_trip(tmp_path: Path) -> None:
    event = EventRecord(
        run_id=uuid4(),
        episode_id=uuid4(),
        condition=Condition.BENIGN,
        seed=42,
        event_type=EventType.EPISODE_STARTED,
        payload={"task_id": "example"},
    )
    path = tmp_path / "events.jsonl"

    JsonlEventSink(path).append(event)

    assert list(read_events(path)) == [event]
