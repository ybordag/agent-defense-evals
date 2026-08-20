"""Append-only JSONL event persistence."""

from collections.abc import Iterator
from pathlib import Path

from agent_interaction_evals.schemas import EventRecord


class JsonlEventSink:
    """Write one validated event per line and flush it immediately."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: EventRecord) -> None:
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(event.model_dump_json())
            stream.write("\n")
            stream.flush()


def read_events(path: Path) -> Iterator[EventRecord]:
    """Yield validated events from a JSONL artifact."""

    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                yield EventRecord.model_validate_json(line)
            except ValueError as error:
                raise ValueError(f"invalid event at {path}:{line_number}") from error
