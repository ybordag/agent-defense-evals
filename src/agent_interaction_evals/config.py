"""Typed configuration loading."""

from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel, ConfigDict, Field

ConfigT = TypeVar("ConfigT", bound=BaseModel)


class ExperimentConfig(BaseModel):
    """Configuration shared by every episode in an experiment run."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    base_seed: int = Field(ge=0)
    artifact_dir: Path = Path("artifacts")
    max_rounds: int = Field(default=4, ge=1, le=20)
    max_regenerations: int = Field(default=2, ge=0, le=10)
    target_vocabulary_size: int = Field(default=64, ge=2)


class ModelConfig(BaseModel):
    """OpenAI-compatible model routing configuration."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    fairlead_base_url: str = Field(min_length=1)
    sender_model: str = Field(min_length=1)
    receiver_model: str = Field(min_length=1)
    request_timeout_seconds: float = Field(default=120.0, gt=0)
    priority: str = Field(default="batch", min_length=1)


def load_yaml_config(path: Path, model: type[ConfigT]) -> ConfigT:
    """Load a YAML mapping and validate it with ``model``."""

    with path.open("r", encoding="utf-8") as stream:
        raw: Any = yaml.safe_load(stream)
    if not isinstance(raw, dict):
        raise ValueError(f"configuration must be a mapping: {path}")
    return model.model_validate(raw)
