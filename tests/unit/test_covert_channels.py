import pytest

from agent_defense_evals.channels.covert import (
    ChannelKind,
    decode_message,
    encode_message,
)


@pytest.mark.parametrize("channel", tuple(ChannelKind))
@pytest.mark.parametrize("secret", (0, 1))
def test_controlled_channels_round_trip(channel: ChannelKind, secret: int) -> None:
    text = encode_message(
        channel,
        task_id="amber",
        secret=secret,
        key=1,
    )
    decoded = decode_message(channel, text, key=1)

    assert decoded.task_id == "amber"
    assert decoded.secret == (None if channel is ChannelKind.BENIGN else secret)


def test_distribution_matching_ciphertext_changes_with_key() -> None:
    first = encode_message(
        ChannelKind.DISTRIBUTION_MATCHING,
        task_id="amber",
        secret=1,
        key=0,
    )
    second = encode_message(
        ChannelKind.DISTRIBUTION_MATCHING,
        task_id="amber",
        secret=1,
        key=1,
    )

    assert "token=1" in first
    assert "token=0" in second
