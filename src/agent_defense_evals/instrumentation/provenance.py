"""Minimal provenance DAG derived from immutable event parent links."""

from collections import defaultdict
from uuid import UUID

from agent_defense_evals.core.trace import Trace


class ProvenanceGraph:
    def __init__(self, trace: Trace) -> None:
        self._parents: dict[UUID, set[UUID]] = {}
        self._children: dict[UUID, set[UUID]] = defaultdict(set)
        for event in trace.events:
            parents = set(event.parent_ids)
            self._parents[event.event_id] = parents
            for parent in parents:
                self._children[parent].add(event.event_id)

    @property
    def node_count(self) -> int:
        return len(self._parents)

    def parents(self, event_id: UUID) -> frozenset[UUID]:
        return frozenset(self._parents[event_id])

    def ancestors(self, event_id: UUID) -> frozenset[UUID]:
        visited: set[UUID] = set()
        pending = list(self._parents[event_id])
        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            pending.extend(self._parents[current] - visited)
        return frozenset(visited)

    def descendants(self, event_id: UUID) -> frozenset[UUID]:
        visited: set[UUID] = set()
        pending = list(self._children[event_id])
        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            pending.extend(self._children[current] - visited)
        return frozenset(visited)

    def shortest_path(self, source: UUID, target: UUID) -> tuple[UUID, ...]:
        if source == target:
            return (source,)
        pending: list[tuple[UUID, tuple[UUID, ...]]] = [(source, (source,))]
        visited = {source}
        while pending:
            current, path = pending.pop(0)
            for child in sorted(self._children[current], key=str):
                if child == target:
                    return (*path, child)
                if child not in visited:
                    visited.add(child)
                    pending.append((child, (*path, child)))
        raise ValueError(f"no provenance path from {source} to {target}")
