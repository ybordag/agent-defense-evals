from pathlib import Path

from agent_defense_evals.core.config import load_experiment
from agent_defense_evals.core.schemas import Directness


def test_load_baseline_configuration() -> None:
    spec = load_experiment(Path("configs/experiments/scripted_baseline.yaml"))

    assert spec.experiment_id == "scripted-baseline"
    assert len(spec.agents) == 2
    assert spec.dimensions.directness is Directness.NONE


def test_load_blocked_attack_configuration() -> None:
    spec = load_experiment(
        Path("configs/experiments/scripted_blocked_attack.yaml")
    )

    assert spec.attack.kind == "force_selection"
    assert spec.defenses[0].kind == "block_plan"
    assert spec.dimensions.directness is Directness.EXPLICIT
