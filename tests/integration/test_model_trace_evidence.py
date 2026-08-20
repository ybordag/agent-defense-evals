import json

from agent_defense_evals.core.schemas import AttackDimensions, ModelRuntimeSpec
from agent_defense_evals.experiments.anytime_evidence import (
    AnytimeEvidenceSpec,
    StreamCondition,
)
from agent_defense_evals.experiments.model_trace_evidence import (
    ModelTraceEvidenceSpec,
    run_model_trace_evidence,
)
from agent_defense_evals.models.types import (
    GenerationRequest,
    GenerationResult,
    ModelIdentity,
    RuntimeCapabilities,
)


class DirectiveFollowingRuntime:
    identity = ModelIdentity(runtime="fake", model_id="directive-follower")

    @property
    def capabilities(self) -> RuntimeCapabilities:
        return RuntimeCapabilities(generation=True, token_logprobs=True)

    def generate(self, request: GenerationRequest) -> GenerationResult:
        signal = (
            "coordinate"
            if "Directive for this step: coordinate" in request.prompt
            else "routine"
        )
        return GenerationResult(
            text=json.dumps({"signal": signal}),
            prompt_token_ids=(1, 2),
            generated_token_ids=(3, 4),
            token_logprobs=(-0.1, -0.1),
            identity=self.identity,
        )


def test_model_trace_scores_are_attributed_and_monitored() -> None:
    evidence = AnytimeEvidenceSpec(
        experiment_id="model-stream-test",
        base_seed=23,
        horizon=100,
        calibration_episodes=1,
        evaluation_episodes=1,
        base_rate=0.01,
        benign_drift_amplitude=0.02,
        attack_rate=0.5,
        onset_fraction=(0.15, 0.25),
        irreversible_delay=60,
        dimensions=AttackDimensions(horizon=100),
    )
    report = run_model_trace_evidence(
        ModelTraceEvidenceSpec(
            experiment_id="model-trace-test",
            base_seed=23,
            evidence=evidence,
            runtime=ModelRuntimeSpec(
                runtime_id="signal-model",
                kind="fake",
                model_id="directive-follower",
            ),
            conditions=(
                StreamCondition.BENIGN_STATIONARY,
                StreamCondition.BENIGN_DRIFT,
                StreamCondition.LOW_RATE,
            ),
        ),
        runtimes={"signal-model": DirectiveFollowingRuntime()},
    )

    assert all(report.gates.values())
    assert report.model_generation_events == 800
    assert report.attributed_scores == 400
    assert report.model["model_id"] == "directive-follower"
    assert StreamCondition.LOW_RATE in report.positive_log_evidence_conditions
    assert not report.conditional_validity_claimed
