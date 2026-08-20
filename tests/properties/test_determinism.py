from pathlib import Path

import pytest

from agent_defense_evals.cli import build_runner


@pytest.mark.parametrize(
    "config",
    [
        Path("configs/experiments/scripted_baseline.yaml"),
        Path("configs/experiments/scripted_blocked_attack.yaml"),
    ],
)
def test_identical_specs_produce_identical_traces(config: Path) -> None:
    first_result, first_trace = build_runner(config).run()
    second_result, second_trace = build_runner(config).run()

    assert first_result == second_result
    assert first_trace.events == second_trace.events
