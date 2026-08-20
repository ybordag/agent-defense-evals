"""Human-authored YAML configuration loading."""

from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel

from agent_defense_evals.core.schemas import ExperimentSpec

ConfigT = TypeVar("ConfigT", bound=BaseModel)


def load_yaml(path: Path, model: type[ConfigT]) -> ConfigT:
    with path.open("r", encoding="utf-8") as stream:
        raw: Any = yaml.safe_load(stream)
    if not isinstance(raw, dict):
        raise ValueError(f"configuration must be a mapping: {path}")
    return model.model_validate(raw)


def load_experiment(path: Path) -> ExperimentSpec:
    return load_yaml(path, ExperimentSpec)
