from pathlib import Path
from uuid import uuid4

import pytest

from agent_defense_evals.core.events import JsonlEventStore
from agent_defense_evals.core.schemas import EventKind, EventRecord
from agent_defense_evals.core.trace import Trace


def make_event(logical_time: int, *, parent_ids: tuple = ()) -> EventRecord:
    episode_id = make_event.episode_id
    return EventRecord(
        event_id=uuid4(),
        experiment_id="test",
        episode_id=episode_id,
        step=0,
        logical_time=logical_time,
        kind=EventKind.EPISODE_STARTED,
        parent_ids=parent_ids,
    )


make_event.episode_id = uuid4()


def test_jsonl_round_trip(tmp_path: Path) -> None:
    first = make_event(0)
    second = make_event(1, parent_ids=(first.event_id,))
    store = JsonlEventStore(tmp_path / "events.jsonl")

    store.replace((first, second))

    assert tuple(store.read()) == (first, second)


def test_trace_rejects_unknown_parent() -> None:
    trace = Trace()
    event = make_event(0, parent_ids=(uuid4(),))

    with pytest.raises(ValueError, match="unknown parents"):
        trace.append(event)
