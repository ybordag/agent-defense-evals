from agent_defense_evals.channels.covert import ChannelKind
from agent_defense_evals.experiments.causal_information import (
    CausalInformationSpec,
    run_causal_information,
)


def test_paired_secret_experiment_separates_message_and_action_information() -> None:
    report = run_causal_information(
        CausalInformationSpec(
            experiment_id="phase3-test",
            base_seed=7,
            pairs=16,
            tasks=("amber", "cobalt"),
        )
    )
    by_channel = {result.channel: result for result in report.channels}

    assert all(report.gates.values())
    assert by_channel[ChannelKind.BENIGN].paired_action_change_rate == 0.0
    covert = by_channel[ChannelKind.DISTRIBUTION_MATCHING]
    assert covert.message_mutual_information_bits == 0.0
    assert covert.action_mutual_information_bits == 1.0
    assert covert.utility_success_rate == 1.0
