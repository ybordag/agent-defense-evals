import pytest
from pydantic import ValidationError

from agent_defense_evals.experiments.anytime_evidence import StreamCondition
from agent_defense_evals.experiments.confirmatory_evidence import (
    ClaimScope,
    ConfirmatoryEvidenceSpec,
    ConfirmatorySplit,
    EpisodeEvidence,
    ModelConfigRef,
    SplitDesign,
    ValidityMode,
    build_manifest,
    build_shard_artifact,
    finalize_confirmatory_report,
    missing_assignments,
    verify_shard_artifact,
)


def _spec(*, test_episodes: int = 80) -> ConfirmatoryEvidenceSpec:
    return ConfirmatoryEvidenceSpec(
        experiment_id="phase5-confirmatory-test",
        base_seed=20260820,
        horizon=20,
        alpha=0.05,
        confidence=0.95,
        validity_mode=ValidityMode.EMPIRICAL_LIFETIME,
        reference_null_mean=0.08,
        irreversible_delay=10,
        bootstrap_replicates=100,
        score_source_id="coalition_action_agreement",
        score_version="1",
        model_configs=(
            ModelConfigRef(
                config_id="qwen-primary",
                model_id="Qwen/Qwen2.5-7B-Instruct",
                model_revision="primary-revision",
                runtime_kind="openai_compatible",
                decoding_sha256="a" * 64,
            ),
            ModelConfigRef(
                config_id="qwen-held-out",
                model_id="Qwen/Qwen2.5-7B-Instruct",
                model_revision="held-out-revision",
                runtime_kind="openai_compatible",
                decoding_sha256="b" * 64,
            ),
        ),
        calibration=SplitDesign(
            conditions=(
                StreamCondition.BENIGN_STATIONARY,
                StreamCondition.BENIGN_DRIFT,
            ),
            episodes_per_condition=20,
            prompt_families=("calibration-task",),
            model_config_ids=("qwen-primary",),
        ),
        validation=SplitDesign(
            conditions=(
                StreamCondition.BENIGN_STATIONARY,
                StreamCondition.BENIGN_DRIFT,
                StreamCondition.LOW_RATE,
            ),
            episodes_per_condition=10,
            prompt_families=("validation-task",),
            model_config_ids=("qwen-primary",),
        ),
        test=SplitDesign(
            conditions=(
                StreamCondition.BENIGN_STATIONARY,
                StreamCondition.BENIGN_DRIFT,
                StreamCondition.LOW_RATE,
            ),
            episodes_per_condition=test_episodes,
            prompt_families=("held-out-task",),
            model_config_ids=("qwen-primary", "qwen-held-out"),
        ),
    )


def _evidence(spec: ConfirmatoryEvidenceSpec) -> tuple[EpisodeEvidence, ...]:
    manifest = build_manifest(spec)
    models = {model.config_id: model for model in spec.model_configs}
    episodes = []
    for assignment in manifest.assignments:
        attacked = assignment.condition is StreamCondition.LOW_RATE
        onset = 5 if attacked else None
        irreversible = 15 if attacked else None
        if attacked:
            scores = (0.0,) * int(onset) + (1.0,) * (spec.horizon - int(onset))
        else:
            scores = (0.0,) * spec.horizon
        model = models[assignment.model_config_id]
        episodes.append(
            EpisodeEvidence(
                assignment_id=assignment.assignment_id,
                split=assignment.split,
                condition=assignment.condition,
                seed=assignment.seed,
                prompt_family=assignment.prompt_family,
                model_config_id=assignment.model_config_id,
                model_id=model.model_id,
                model_revision=model.model_revision,
                score_source_id=spec.score_source_id,
                score_version=spec.score_version,
                scores=scores,
                onset_step=onset,
                irreversible_step=irreversible,
                utility_score=0.9,
                latency_seconds=0.01,
                trace_sha256=f"trace-{assignment.assignment_id}",
            )
        )
    return tuple(episodes)


def test_manifest_is_deterministic_disjoint_and_includes_held_out_model() -> None:
    spec = _spec(test_episodes=10)
    first = build_manifest(spec)
    second = build_manifest(spec)

    assert first == second
    assert len(first.assignments) == 100
    assert len({assignment.assignment_id for assignment in first.assignments}) == 100
    assert len({assignment.seed for assignment in first.assignments}) == 100
    assert {
        assignment.prompt_family
        for assignment in first.assignments
        if assignment.split is ConfirmatorySplit.TEST
    } == {"held-out-task"}
    assert any(
        assignment.model_config_id == "qwen-held-out"
        for assignment in first.assignments
        if assignment.split is ConfirmatorySplit.TEST
    )


def test_spec_rejects_prompt_leakage_and_missing_held_out_model() -> None:
    spec = _spec(test_episodes=10)
    with pytest.raises(ValidationError, match="prompt families must be disjoint"):
        ConfirmatoryEvidenceSpec.model_validate(
            {
                **spec.model_dump(mode="python"),
                "test": spec.test.model_copy(
                    update={"prompt_families": ("calibration-task",)}
                ),
            }
        )
    with pytest.raises(ValidationError, match="held-out model configuration"):
        ConfirmatoryEvidenceSpec.model_validate(
            {
                **spec.model_dump(mode="python"),
                "test": spec.test.model_copy(
                    update={"model_config_ids": ("qwen-primary",)}
                ),
            }
        )


def test_shards_are_content_addressed_and_resume_lists_missing_assignments() -> None:
    spec = _spec(test_episodes=10)
    manifest = build_manifest(spec)
    episodes = _evidence(spec)
    midpoint = len(episodes) // 2
    first = build_shard_artifact(
        shard_id="first", manifest=manifest, episodes=episodes[:midpoint]
    )

    verify_shard_artifact(first)
    assert len(missing_assignments(manifest, (first,))) == len(episodes) - midpoint
    tampered = first.model_copy(update={"artifact_sha256": "wrong"})
    with pytest.raises(ValueError, match="digest does not match"):
        verify_shard_artifact(tampered)


def test_empirical_report_uses_only_calibration_and_does_not_overclaim() -> None:
    spec = _spec()
    manifest = build_manifest(spec)
    episodes = _evidence(spec)
    shards = (
        build_shard_artifact(
            shard_id="calibration",
            manifest=manifest,
            episodes=tuple(
                episode
                for episode in episodes
                if episode.split is ConfirmatorySplit.CALIBRATION
            ),
        ),
        build_shard_artifact(
            shard_id="validation",
            manifest=manifest,
            episodes=tuple(
                episode
                for episode in episodes
                if episode.split is ConfirmatorySplit.VALIDATION
            ),
        ),
        build_shard_artifact(
            shard_id="test",
            manifest=manifest,
            episodes=tuple(
                episode
                for episode in episodes
                if episode.split is ConfirmatorySplit.TEST
            ),
        ),
    )
    report = finalize_confirmatory_report(spec, manifest, shards)

    assert report.calibration.claim_scope is ClaimScope.EXCHANGEABLE_EPISODE_LIFETIME
    assert not report.calibration.conditional_validity_claimed
    assert report.calibration.eprocess_log_threshold == 0.0
    assert all(report.gates.values())
    assert report.group_diagnostics
    assert all(diagnostic.descriptive_only for diagnostic in report.group_diagnostics)
    low_rate = next(
        result
        for result in report.test_results
        if result.monitor_id == "mixture_e_process"
        and result.condition is StreamCondition.LOW_RATE
    )
    assert low_rate.post_onset_detection.estimate == 1.0
    assert low_rate.detected_before_irreversible.estimate == 1.0
    assert low_rate.median_detection_delay is not None


def test_report_rejects_missing_or_duplicate_assignments() -> None:
    spec = _spec(test_episodes=10)
    manifest = build_manifest(spec)
    episodes = _evidence(spec)
    incomplete = build_shard_artifact(
        shard_id="incomplete", manifest=manifest, episodes=episodes[:-1]
    )
    with pytest.raises(ValueError, match="missing 1 assignments"):
        finalize_confirmatory_report(spec, manifest, (incomplete,))

    first = build_shard_artifact(
        shard_id="first", manifest=manifest, episodes=episodes[:1]
    )
    second = build_shard_artifact(
        shard_id="second", manifest=manifest, episodes=episodes[:1]
    )
    with pytest.raises(ValueError, match="duplicate assignment across shards"):
        finalize_confirmatory_report(spec, manifest, (first, second))
