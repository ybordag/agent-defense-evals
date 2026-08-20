"""Append-only JSONL event persistence."""

from collections.abc import Iterable, Iterator
from pathlib import Path

from agent_defense_evals.core.schemas import EventRecord


class JsonlEventStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def replace(self, events: Iterable[EventRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as stream:
            for event in events:
                stream.write(event.model_dump_json())
                stream.write("\n")

    def append(self, event: EventRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(event.model_dump_json())
            stream.write("\n")

    def read(self) -> Iterator[EventRecord]:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    yield EventRecord.model_validate_json(line)
