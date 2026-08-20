from pathlib import Path

from agent_interaction_evals.config import ExperimentConfig, load_yaml_config


def test_load_experiment_config() -> None:
    config = load_yaml_config(Path("configs/experiment.yaml"), ExperimentConfig)

    assert config.name == "target-word-pilot"
    assert config.max_rounds == 4
    assert config.target_vocabulary_size == 64
