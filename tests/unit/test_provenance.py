from pathlib import Path

from agent_defense_evals.cli import build_runner
from agent_defense_evals.core.schemas import EventKind
from agent_defense_evals.instrumentation.provenance import ProvenanceGraph


def test_completion_has_action_ancestors() -> None:
    _, trace = build_runner(
        Path("configs/experiments/scripted_baseline.yaml")
    ).run()
    graph = ProvenanceGraph(trace)
    completed = trace.by_kind(EventKind.EPISODE_COMPLETED)[0]
    ancestors = graph.ancestors(completed.event_id)
    selection_events = [
        event
        for event in trace.by_kind(EventKind.ACTION_APPLIED)
        if event.payload["action"]["kind"] == "select_plan"
    ]

    assert graph.node_count == len(trace.events)
    assert len(selection_events) == 1
    assert selection_events[0].event_id in ancestors
