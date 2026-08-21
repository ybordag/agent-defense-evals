"""Mechanism-diverse tail-robustness experiment harness."""

from agent_defense_evals.experiments.tail_robustness.contracts import (
    TailExperimentSpec,
    TailManifest,
    TailOutcomeArtifact,
    TailSelectionArtifact,
)
from agent_defense_evals.experiments.tail_robustness.runner import (
    build_tail_manifest,
    run_tail_split,
    select_tail_stacks,
)

__all__ = [
    "TailExperimentSpec",
    "TailManifest",
    "TailOutcomeArtifact",
    "TailSelectionArtifact",
    "build_tail_manifest",
    "run_tail_split",
    "select_tail_stacks",
]
