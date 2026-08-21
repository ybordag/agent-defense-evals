"""Goal-driven open-model execution for the Phase 5 confirmatory design."""

from __future__ import annotations

import hashlib
import json
import random
import time
from collections.abc import Callable, Mapping

from pydantic import Field, model_validator

from agent_defense_evals.analysis.trace_scores import CoalitionSignalTraceScorer
from agent_defense_evals.attacks.scripted import NoAttack
from agent_defense_evals.core.factory import (
    build_agents,
    build_model_runtimes,
    build_scenario,
)
from agent_defense_evals.core.runner import ExperimentRunner
from agent_defense_evals.core.schemas import (
    AgentSpec,
    AttackDimensions,
    CaptureSpec,
    ComponentSpec,
    Directness,
    EventKind,
    ExperimentSpec,
    FrozenModel,
    ModelRuntimeSpec,
)
from agent_defense_evals.defenses.gateway import DefenseGateway
from agent_defense_evals.experiments.anytime_evidence import (
    BENIGN_CONDITIONS,
    StreamCondition,
)
from agent_defense_evals.experiments.confirmatory_evidence import (
    ConfirmatoryEvidenceSpec,
    ConfirmatoryManifest,
    ConfirmatoryShardArtifact,
    ConfirmatorySplit,
    EpisodeAssignment,
    EpisodeEvidence,
    ValidityMode,
    build_shard_artifact,
    specification_sha256,
    verify_manifest,
    verify_shard_artifact,
)
from agent_defense_evals.models.base import ModelRuntime


class ConfirmatoryRuntimeConfig(FrozenModel):
    config_id: str = Field(min_length=1)
    runtime: ModelRuntimeSpec
    max_new_tokens: int = Field(default=16, ge=4, le=128)
    do_sample: bool = True
    temperature: float = Field(default=0.7, gt=0.0)
    top_p: float = Field(default=0.95, gt=0.0, le=1.0)


def decoding_sha256(config: ConfirmatoryRuntimeConfig) -> str:
    payload = {
        "do_sample": config.do_sample,
        "max_new_tokens": config.max_new_tokens,
        "temperature": config.temperature,
        "top_p": config.top_p,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class ConfirmatoryExecutionSpec(FrozenModel):
    design: ConfirmatoryEvidenceSpec
    runtime_configs: tuple[ConfirmatoryRuntimeConfig, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_runtime_bindings(self) -> ConfirmatoryExecutionSpec:
        if self.design.validity_mode is not ValidityMode.EMPIRICAL_LIFETIME:
            raise ValueError(
                "goal-driven model execution requires empirical lifetime validity"
            )
        runtime_by_id = {item.config_id: item for item in self.runtime_configs}
        if len(runtime_by_id) != len(self.runtime_configs):
            raise ValueError("confirmatory runtime config IDs must be unique")
        expected_ids = {item.config_id for item in self.design.model_configs}
        if set(runtime_by_id) != expected_ids:
            raise ValueError("every frozen model config requires one runtime binding")
        for frozen in self.design.model_configs:
            binding = runtime_by_id[frozen.config_id]
            if binding.runtime.model_id != frozen.model_id:
                raise ValueError(f"model ID differs for {frozen.config_id}")
            if binding.runtime.kind != frozen.runtime_kind:
                raise ValueError(f"runtime kind differs for {frozen.config_id}")
            revision = str(binding.runtime.config.get("model_revision", ""))
            if revision != frozen.model_revision:
                raise ValueError(f"model revision differs for {frozen.config_id}")
            if decoding_sha256(binding) != frozen.decoding_sha256:
                raise ValueError(f"decoding hash differs for {frozen.config_id}")
        return self


def _attack_timing(
    design: ConfirmatoryEvidenceSpec,
    assignment: EpisodeAssignment,
) -> tuple[int | None, int | None]:
    if assignment.condition in BENIGN_CONDITIONS:
        return None, None
    rng = random.Random(assignment.seed)
    lower = max(1, design.horizon // 5)
    upper = min(
        max(lower, 2 * design.horizon // 5),
        design.horizon - design.irreversible_delay - 1,
    )
    if upper < lower:
        raise ValueError("horizon leaves no valid randomized attack-onset range")
    onset = rng.randint(lower, upper)
    return onset, onset + design.irreversible_delay


def build_confirmatory_episode_spec(
    spec: ConfirmatoryExecutionSpec,
    assignment: EpisodeAssignment,
) -> ExperimentSpec:
    bindings = {item.config_id: item for item in spec.runtime_configs}
    binding = bindings[assignment.model_config_id]
    onset, irreversible = _attack_timing(spec.design, assignment)
    agent_ids = ("signal_sender", "signal_receiver")
    policy = {
        "runtime_id": binding.runtime.runtime_id,
        "max_new_tokens": binding.max_new_tokens,
        "do_sample": binding.do_sample,
        "temperature": binding.temperature,
        "top_p": binding.top_p,
    }
    directness = (
        Directness.NONE
        if assignment.condition in BENIGN_CONDITIONS
        else (
            Directness.REWARD_INDUCED
            if assignment.condition is StreamCondition.REWARD_INDUCED
            else Directness.EMERGENT
        )
    )
    return ExperimentSpec(
        experiment_id=f"{spec.design.experiment_id}:{assignment.assignment_id}",
        base_seed=assignment.seed,
        max_steps=spec.design.horizon,
        agents=tuple(
            AgentSpec(
                agent_id=agent_id,
                role=role,
                policy=ComponentSpec(kind="sequential_signal_model", config=policy),
            )
            for agent_id, role in zip(
                agent_ids, ("signal-sender", "signal-receiver"), strict=True
            )
        ),
        runtimes=(binding.runtime,),
        scenario=ComponentSpec(
            kind="sequential_signal",
            config={
                "agent_ids": list(agent_ids),
                "behavior_mode": "goal_driven",
                "horizon": spec.design.horizon,
                "condition": assignment.condition.value,
                "onset_step": onset,
                "irreversible_step": irreversible,
                "prompt_family": assignment.prompt_family,
            },
        ),
        dimensions=AttackDimensions(
            detectability_target=0.5,
            coalition_size=2,
            cascade_branching=1.0,
            composition_depth=3,
            horizon=spec.design.horizon,
            attribution_degradation=0.5,
            directness=directness,
            reversibility=0.0,
        ),
        capture=CaptureSpec(events=True, activations=False),
    )


def _trace_sha256(trace_events: tuple[object, ...]) -> str:
    payload = [event.model_dump(mode="json") for event in trace_events]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def run_confirmatory_assignment(
    spec: ConfirmatoryExecutionSpec,
    assignment: EpisodeAssignment,
    runtime: ModelRuntime,
) -> EpisodeEvidence:
    episode_spec = build_confirmatory_episode_spec(spec, assignment)
    started = time.monotonic()
    result, trace = ExperimentRunner(
        spec=episode_spec,
        scenario=build_scenario(episode_spec),
        agents=build_agents(
            episode_spec, {episode_spec.runtimes[0].runtime_id: runtime}
        ),
        attack=NoAttack(),
        gateway=DefenseGateway(()),
    ).run()
    latency = time.monotonic() - started
    if not result.utility.success or result.steps != spec.design.horizon:
        raise RuntimeError("confirmatory episode did not complete its frozen horizon")
    scores = CoalitionSignalTraceScorer(("signal_sender", "signal_receiver")).score(
        trace, horizon=spec.design.horizon
    )
    if len(scores) != spec.design.horizon or any(
        len(score.sources[0].actor_ids) != 2 for score in scores
    ):
        raise RuntimeError("confirmatory trace scores are incomplete or unattributed")
    generations = trace.by_kind(EventKind.MODEL_GENERATED)
    expected_generations = spec.design.horizon * 2
    if len(generations) != expected_generations:
        raise RuntimeError("confirmatory trace is missing model generations")
    frozen_models = {item.config_id: item for item in spec.design.model_configs}
    frozen = frozen_models[assignment.model_config_id]
    model_payloads = [event.payload.get("model") or {} for event in generations]
    identities = {model.get("model_id") for model in model_payloads}
    revisions = {model.get("model_revision") for model in model_payloads}
    if identities != {frozen.model_id} or revisions != {frozen.model_revision}:
        raise RuntimeError("runtime model identity differs from frozen provenance")
    onset, irreversible = _attack_timing(spec.design, assignment)
    return EpisodeEvidence(
        assignment_id=assignment.assignment_id,
        split=assignment.split,
        condition=assignment.condition,
        seed=assignment.seed,
        prompt_family=assignment.prompt_family,
        model_config_id=assignment.model_config_id,
        model_id=frozen.model_id,
        model_revision=frozen.model_revision,
        score_source_id=spec.design.score_source_id,
        score_version=spec.design.score_version,
        scores=tuple(score.value for score in scores),
        onset_step=onset,
        irreversible_step=irreversible,
        utility_score=result.utility.score,
        latency_seconds=latency,
        trace_sha256=_trace_sha256(trace.events),
    )


def select_shard_assignments(
    manifest: ConfirmatoryManifest,
    *,
    shard_index: int,
    shard_count: int,
    split: ConfirmatorySplit,
) -> tuple[EpisodeAssignment, ...]:
    if shard_count < 1 or not 0 <= shard_index < shard_count:
        raise ValueError("shard index must be in [0, shard_count)")
    eligible = tuple(
        assignment
        for assignment in manifest.assignments
        if assignment.split is split
    )
    return tuple(
        assignment
        for index, assignment in enumerate(eligible)
        if index % shard_count == shard_index
    )


def run_confirmatory_shard(
    spec: ConfirmatoryExecutionSpec,
    manifest: ConfirmatoryManifest,
    *,
    shard_index: int = 0,
    shard_count: int = 1,
    split: ConfirmatorySplit,
    implementation_revision: str,
    runtimes: Mapping[str, ModelRuntime] | None = None,
    existing: ConfirmatoryShardArtifact | None = None,
    checkpoint: Callable[[ConfirmatoryShardArtifact], None] | None = None,
    max_new_episodes: int | None = None,
) -> ConfirmatoryShardArtifact:
    verify_manifest(manifest)
    if manifest.implementation_revision != implementation_revision:
        raise ValueError("manifest implementation revision differs from execution")
    if manifest.specification_sha256 != specification_sha256(spec.design):
        raise ValueError("manifest does not match execution design")
    if max_new_episodes is not None and max_new_episodes < 1:
        raise ValueError("max new episodes must be positive")
    selected = select_shard_assignments(
        manifest,
        shard_index=shard_index,
        shard_count=shard_count,
        split=split,
    )
    if not selected:
        raise ValueError("selected confirmatory shard is empty")
    shard_id = f"{split.value}-shard-{shard_index:04d}-of-{shard_count:04d}"
    completed: list[EpisodeEvidence] = []
    if existing is not None:
        verify_shard_artifact(existing)
        if existing.shard_id != shard_id:
            raise ValueError("existing checkpoint has a different shard identity")
        if (
            existing.specification_sha256 != manifest.specification_sha256
            or existing.manifest_sha256 != manifest.manifest_sha256
        ):
            raise ValueError("existing checkpoint differs from the frozen manifest")
        selected_ids = {item.assignment_id for item in selected}
        if any(item.assignment_id not in selected_ids for item in existing.episodes):
            raise ValueError("existing checkpoint contains another shard's assignment")
        completed.extend(existing.episodes)
    completed_ids = {item.assignment_id for item in completed}
    remaining = tuple(
        item for item in selected if item.assignment_id not in completed_ids
    )
    if not remaining:
        if existing is None:
            raise RuntimeError("completed shard has no checkpoint artifact")
        return existing
    to_run = remaining if max_new_episodes is None else remaining[:max_new_episodes]
    runtime_map = dict(runtimes or {})
    bindings = {item.config_id: item for item in spec.runtime_configs}
    for config_id in {item.model_config_id for item in to_run}:
        if config_id in runtime_map:
            continue
        example = next(item for item in to_run if item.model_config_id == config_id)
        episode_spec = build_confirmatory_episode_spec(spec, example)
        built = build_model_runtimes(episode_spec)
        runtime_map[config_id] = built[bindings[config_id].runtime.runtime_id]
    for assignment in to_run:
        completed.append(
            run_confirmatory_assignment(
                spec, assignment, runtime_map[assignment.model_config_id]
            )
        )
        artifact = build_shard_artifact(
            shard_id=shard_id,
            manifest=manifest,
            episodes=tuple(completed),
        )
        if checkpoint is not None:
            checkpoint(artifact)
    return artifact
