from agent_defense_evals.experiments.heterogeneous_policy_audit import (
    HeterogeneousPolicyAuditSpec,
    run_heterogeneous_policy_audit,
)
from agent_defense_evals.models.types import (
    GenerationRequest,
    GenerationResult,
    ModelIdentity,
    RuntimeCapabilities,
)


class AuthorizingRuntime:
    def __init__(self, model_id: str) -> None:
        self.identity = ModelIdentity(runtime="fake", model_id=model_id)

    @property
    def capabilities(self) -> RuntimeCapabilities:
        return RuntimeCapabilities(generation=True)

    def generate(self, request: GenerationRequest) -> GenerationResult:
        assert request.response_schema is not None
        return GenerationResult(
            text='{"authorized": true}',
            prompt_token_ids=(1,),
            generated_token_ids=(2,),
            token_logprobs=(-0.1,),
            identity=self.identity,
        )


def test_heterogeneous_model_audit_uses_both_runtimes() -> None:
    report = run_heterogeneous_policy_audit(
        HeterogeneousPolicyAuditSpec(
            experiment_id="model-audit-test",
            base_seed=3,
            remote_base_url="http://model.test/v1",
            remote_model_id="small",
            white_box_model_id="large",
            device="cpu",
        ),
        runtimes={
            "remote": AuthorizingRuntime("small"),
            "white_box": AuthorizingRuntime("large"),
        },
    )

    assert report.all_local_components_authorized
    assert {result.runtime_id for result in report.results} == {
        "remote",
        "white_box",
    }
