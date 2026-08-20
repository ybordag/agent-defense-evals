from pathlib import Path

from agent_interaction_evals.events import read_events
from agent_interaction_evals.schemas import EventType
from agent_interaction_evals.smoke import run_phase0_smoke


def test_phase0_smoke_gate(tmp_path: Path) -> None:
    output = tmp_path / "phase0.jsonl"

    event = run_phase0_smoke(Path("configs/experiment.yaml"), output)

    assert event.event_type is EventType.EPISODE_STARTED
    assert list(read_events(output)) == [event]
