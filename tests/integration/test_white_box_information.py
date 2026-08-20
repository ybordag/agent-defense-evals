import re

import pytest

torch = pytest.importorskip("torch")

from agent_defense_evals.experiments.white_box_information import (  # noqa: E402
    WhiteBoxInformationSpec,
    run_white_box_information,
)
from agent_defense_evals.models.types import (  # noqa: E402
    GenerationRequest,
    GenerationResult,
    ModelIdentity,
    RuntimeCapabilities,
)


class FakeWhiteBoxRuntime:
    identity = ModelIdentity(runtime="fake-white-box", model_id="fake-model")

    @property
    def capabilities(self) -> RuntimeCapabilities:
        return RuntimeCapabilities(
            generation=True,
            token_logprobs=True,
            activation_capture=True,
            activation_patch=True,
        )

    def generate(self, request: GenerationRequest) -> GenerationResult:
        key = int(re.search(r"private key is ([01])", request.prompt).group(1))
        ciphertext = int(
            re.search(r"reference token is ([01])", request.prompt).group(1)
        )
        secret = key ^ ciphertext
        patched = bool(request.patches)
        token = 0 if patched else secret
        logits = torch.tensor([[3.0, 0.0] if token == 0 else [0.0, 3.0]])
        vector = torch.tensor(
            [[[0.0, 0.1] if secret == 0 else [3.0, 3.1]]]
        )
        return GenerationResult(
            text=str(token),
            prompt_token_ids=(1, 2),
            generated_token_ids=(token,),
            token_logprobs=(-0.01,),
            step_logits=(logits,),
            module_outputs={
                module_name: (vector,)
                for module_name in request.capture.module_names
            },
            identity=self.identity,
            metadata={
                "patch_applied_counts": {
                    patch.module_name: 1 for patch in request.patches
                }
            },
        )


def test_white_box_probe_and_patch_gates() -> None:
    report = run_white_box_information(
        WhiteBoxInformationSpec(
            experiment_id="white-box-test",
            base_seed=11,
            model_id="fake-model",
            device="cpu",
            pairs=8,
            probe_module="layer.1",
            patch_modules=("layer.0", "layer.1"),
        ),
        runtime=FakeWhiteBoxRuntime(),
    )

    assert all(report.gates.values())
    assert report.message_decoder.value == 0.5
    assert report.behavior_accuracy.value == 1.0
    assert report.activation_probe.value == 1.0
    assert all(patch.flipped_to_reference for patch in report.patches)
