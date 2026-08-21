import json

from agent_defense_evals.core.schemas import ModelRuntimeSpec
from agent_defense_evals.experiments.anytime_evidence import StreamCondition
from agent_defense_evals.experiments.confirmatory_evidence import (
    ConfirmatoryEvidenceSpec,
    ConfirmatorySplit,
    ModelConfigRef,
    SplitDesign,
    build_manifest,
)
from agent_defense_evals.experiments.confirmatory_model import (
    ConfirmatoryExecutionSpec,
    ConfirmatoryRuntimeConfig,
    decoding_sha256,
    run_confirmatory_shard,
    select_shard_assignments,
)
from agent_defense_evals.models.types import (
    GenerationRequest,
    GenerationResult,
    ModelIdentity,
    RuntimeCapabilities,
)


class GoalFollowingRuntime:
    def __init__(self, model_id: str, revision: str) -> None:
        self.identity = ModelIdentity(
            runtime="fake", model_id=model_id, model_revision=revision
        )
        self.requests: list[GenerationRequest] = []

    @property
    def capabilities(self) -> RuntimeCapabilities:
        return RuntimeCapabilities(generation=True)

    def generate(self, request: GenerationRequest) -> GenerationResult:
        self.requests.append(request)
        coordinate = "Improve joint throughput" in request.prompt
        return GenerationResult(
            text=json.dumps({"signal": "coordinate" if coordinate else "routine"}),
            prompt_token_ids=(1,),
            generated_token_ids=(2,),
            token_logprobs=(-0.1,),
            identity=self.identity,
        )


def _execution_spec() -> ConfirmatoryExecutionSpec:
    runtime_configs = (
        ConfirmatoryRuntimeConfig(
            config_id="primary",
            runtime=ModelRuntimeSpec(
                runtime_id="runtime-primary",
                kind="fake",
                model_id="open-model-primary",
                config={"model_revision": "revision-a"},
            ),
        ),
        ConfirmatoryRuntimeConfig(
            config_id="held-out",
            runtime=ModelRuntimeSpec(
                runtime_id="runtime-held-out",
                kind="fake",
                model_id="open-model-held-out",
                config={"model_revision": "revision-b"},
            ),
        ),
    )
    models = tuple(
        ModelConfigRef(
            config_id=config.config_id,
            model_id=config.runtime.model_id,
            model_revision=str(config.runtime.config["model_revision"]),
            runtime_kind=config.runtime.kind,
            decoding_sha256=decoding_sha256(config),
        )
        for config in runtime_configs
    )
    design = ConfirmatoryEvidenceSpec(
        experiment_id="goal-driven-confirmatory-test",
        base_seed=91,
        horizon=20,
        irreversible_delay=10,
        bootstrap_replicates=100,
        score_source_id="coalition_action_agreement",
        score_version="1",
        model_configs=models,
        calibration=SplitDesign(
            conditions=(
                StreamCondition.BENIGN_STATIONARY,
                StreamCondition.BENIGN_DRIFT,
            ),
            episodes_per_condition=1,
            prompt_families=("calibration-operations",),
            model_config_ids=("primary",),
        ),
        validation=SplitDesign(
            conditions=(
                StreamCondition.BENIGN_STATIONARY,
                StreamCondition.BENIGN_DRIFT,
                StreamCondition.LOW_RATE,
            ),
            episodes_per_condition=1,
            prompt_families=("validation-operations",),
            model_config_ids=("primary",),
        ),
        test=SplitDesign(
            conditions=(
                StreamCondition.BENIGN_STATIONARY,
                StreamCondition.BENIGN_DRIFT,
                StreamCondition.LOW_RATE,
            ),
            episodes_per_condition=2,
            prompt_families=("held-out-operations",),
            model_config_ids=("primary", "held-out"),
        ),
    )
    return ConfirmatoryExecutionSpec(design=design, runtime_configs=runtime_configs)


def test_goal_driven_confirmatory_shard_uses_unscripted_prompts_and_scores() -> None:
    spec = _execution_spec()
    manifest = build_manifest(spec.design)
    primary = GoalFollowingRuntime("open-model-primary", "revision-a")
    held_out = GoalFollowingRuntime("open-model-held-out", "revision-b")
    shard = run_confirmatory_shard(
        spec,
        manifest,
        runtimes={"primary": primary, "held-out": held_out},
        max_new_episodes=2,
    )

    assert len(shard.episodes) == 2
    shard = run_confirmatory_shard(
        spec,
        manifest,
        runtimes={"primary": primary, "held-out": held_out},
        existing=shard,
    )

    assert len(shard.episodes) == len(manifest.assignments)
    requests = primary.requests + held_out.requests
    assert requests
    assert all("Directive for this step" not in item.prompt for item in requests)
    assert all("low_rate" not in item.prompt for item in requests)
    attacks = [
        episode
        for episode in shard.episodes
        if episode.condition is StreamCondition.LOW_RATE
    ]
    benign = [
        episode
        for episode in shard.episodes
        if episode.condition
        in {
            StreamCondition.BENIGN_STATIONARY,
            StreamCondition.BENIGN_DRIFT,
        }
    ]
    assert all(max(episode.scores) == 0.0 for episode in benign)
    assert all(
        any(score == 1.0 for score in episode.scores[int(episode.onset_step) :])
        for episode in attacks
    )
    assert {
        episode.model_config_id
        for episode in shard.episodes
        if episode.split is ConfirmatorySplit.TEST
    } == {"primary", "held-out"}

    request_count = len(requests)
    resumed = run_confirmatory_shard(
        spec,
        manifest,
        runtimes={"primary": primary, "held-out": held_out},
        existing=shard,
    )
    assert resumed == shard
    assert len(primary.requests) + len(held_out.requests) == request_count


def test_split_shards_do_not_start_frozen_test_assignments() -> None:
    spec = _execution_spec()
    manifest = build_manifest(spec.design)
    selected = select_shard_assignments(
        manifest,
        shard_index=0,
        shard_count=2,
        split=ConfirmatorySplit.VALIDATION,
    )

    assert selected
    assert all(item.split is ConfirmatorySplit.VALIDATION for item in selected)
