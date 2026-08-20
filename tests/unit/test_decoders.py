import pytest

from agent_defense_evals.analysis.decoders import (
    CategoricalBinaryDecoder,
    CentroidBinaryDecoder,
    empirical_mutual_information,
    wilson_interval,
)


def test_categorical_decoder_uses_training_mapping_and_deterministic_ties() -> None:
    decoder = CategoricalBinaryDecoder()
    decoder.fit(["a", "a", "b", "b"], [0, 0, 0, 1])

    assert decoder.predict(["a", "b", "unknown"]) == (0, 0, 0)


def test_centroid_probe_separates_binary_vectors() -> None:
    decoder = CentroidBinaryDecoder()
    decoder.fit([(0.0, 0.1), (0.2, 0.0), (3.0, 3.1), (2.9, 3.0)], [0, 0, 1, 1])

    assert decoder.predict([(0.1, 0.1), (3.1, 2.9)]) == (0, 1)


def test_empirical_information_distinguishes_independence() -> None:
    labels = [0, 1, 0, 1]

    assert empirical_mutual_information(["x", "x", "y", "y"], labels) == 0.0
    assert empirical_mutual_information(["a", "b", "a", "b"], labels) == 1.0


def test_wilson_interval_validates_sample_count() -> None:
    with pytest.raises(ValueError):
        wilson_interval(0, 0)
