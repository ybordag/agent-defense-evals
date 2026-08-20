"""Validated immutable episode traces."""

from collections.abc import Iterable
from uuid import UUID

from agent_defense_evals.core.schemas import EventKind, EventRecord


class Trace:
    def __init__(self, events: Iterable[EventRecord] = ()) -> None:
        self._events: list[EventRecord] = []
        self._event_ids: set[UUID] = set()
        for event in events:
            self.append(event)

    @property
    def events(self) -> tuple[EventRecord, ...]:
        return tuple(self._events)

    def append(self, event: EventRecord) -> None:
        if event.event_id in self._event_ids:
            raise ValueError(f"duplicate event ID: {event.event_id}")
        if self._events:
            first = self._events[0]
            if event.episode_id != first.episode_id:
                raise ValueError("all events in a trace must share an episode ID")
            if event.logical_time <= self._events[-1].logical_time:
                raise ValueError("logical time must increase monotonically")
        missing = set(event.parent_ids) - self._event_ids
        if missing:
            unknown = sorted(map(str, missing))
            raise ValueError(f"event references unknown parents: {unknown}")
        self._events.append(event)
        self._event_ids.add(event.event_id)

    def by_kind(self, kind: EventKind) -> tuple[EventRecord, ...]:
        return tuple(event for event in self._events if event.kind is kind)

    def get(self, event_id: UUID) -> EventRecord:
        for event in self._events:
            if event.event_id == event_id:
                return event
        raise KeyError(event_id)
