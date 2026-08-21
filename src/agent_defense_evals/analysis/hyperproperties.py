"""Typed provenance-backed policy DSL for Phase 4."""

from collections.abc import Mapping
from uuid import UUID

from pydantic import Field

from agent_defense_evals.core.schemas import ActionKind, EventKind, FrozenModel
from agent_defense_evals.core.trace import Trace
from agent_defense_evals.instrumentation.provenance import ProvenanceGraph


class LocalAuthorizationRule(FrozenModel):
    role: str = Field(min_length=1)
    allowed_actions: tuple[ActionKind, ...]


class ForbiddenFlowRule(FrozenModel):
    rule_id: str = Field(min_length=1)
    source_classification: str = Field(min_length=1)
    sink: str = Field(min_length=1)


class FlowViolation(FrozenModel):
    rule_id: str
    terminal_event_id: UUID
    source_event_ids: tuple[UUID, ...]
    subgraph_event_ids: tuple[UUID, ...]
    actor_ids: tuple[str, ...]


def evaluate_local_authorization(
    trace: Trace,
    *,
    roles: Mapping[str, str],
    rules: tuple[LocalAuthorizationRule, ...],
) -> tuple[UUID, ...]:
    allowed_by_role = {rule.role: set(rule.allowed_actions) for rule in rules}
    rejected = []
    for event in trace.by_kind(EventKind.ACTION_APPLIED):
        action = event.payload["action"]
        role = roles.get(str(event.actor_id))
        if role is None or ActionKind(action["kind"]) not in allowed_by_role[role]:
            rejected.append(event.event_id)
    return tuple(rejected)


def evaluate_forbidden_flow(
    trace: Trace,
    rule: ForbiddenFlowRule,
) -> tuple[FlowViolation, ...]:
    graph = ProvenanceGraph(trace)
    events = {event.event_id: event for event in trace.events}
    artifact_events = {}
    artifact_sources: dict[str, tuple[str, ...]] = {}
    artifact_classifications: dict[str, str] = {}
    for event in trace.by_kind(EventKind.ACTION_APPLIED):
        candidate = event.payload["action"]
        if candidate["kind"] != ActionKind.CREATE_ARTIFACT.value:
            continue
        payload = candidate["payload"]
        artifact_id = str(payload["artifact_id"])
        artifact_events[artifact_id] = event.event_id
        artifact_sources[artifact_id] = tuple(
            map(str, payload.get("source_artifact_ids", ()))
        )
        artifact_classifications[artifact_id] = str(payload["classification"])
    violations = []
    for terminal in trace.by_kind(EventKind.ACTION_APPLIED):
        action = terminal.payload["action"]
        if (
            action["kind"] != ActionKind.EXECUTE_ARTIFACT.value
            or action["payload"].get("sink") != rule.sink
        ):
            continue
        pending = [str(action["payload"]["artifact_id"])]
        visited: set[str] = set()
        source_artifact_ids = []
        while pending:
            artifact_id = pending.pop()
            if artifact_id in visited or artifact_id not in artifact_sources:
                continue
            visited.add(artifact_id)
            if artifact_classifications[artifact_id] == rule.source_classification:
                source_artifact_ids.append(artifact_id)
            pending.extend(artifact_sources[artifact_id])
        sources = [artifact_events[artifact_id] for artifact_id in source_artifact_ids]
        if not sources:
            continue
        subgraph: set[UUID] = {terminal.event_id}
        for source in sources:
            subgraph.update(graph.shortest_path(source, terminal.event_id))
        actors = tuple(
            sorted(
                {
                    str(events[event_id].actor_id)
                    for event_id in subgraph
                    if events[event_id].actor_id is not None
                }
            )
        )
        violations.append(
            FlowViolation(
                rule_id=rule.rule_id,
                terminal_event_id=terminal.event_id,
                source_event_ids=tuple(sorted(sources, key=str)),
                subgraph_event_ids=tuple(sorted(subgraph, key=str)),
                actor_ids=actors,
            )
        )
    return tuple(violations)
