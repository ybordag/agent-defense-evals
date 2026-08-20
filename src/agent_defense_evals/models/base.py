"""Capability-aware model runtime boundary."""

from typing import Protocol

from agent_defense_evals.models.types import (
    GenerationRequest,
    GenerationResult,
    RuntimeCapabilities,
)


class ModelRuntime(Protocol):
    @property
    def capabilities(self) -> RuntimeCapabilities: ...

    def generate(self, request: GenerationRequest) -> GenerationResult: ...
