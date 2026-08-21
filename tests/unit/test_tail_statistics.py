import pytest

from agent_defense_evals.experiments.tail_robustness.statistics import (
    dkw_cvar_ucb,
    hoeffding_difference_lower,
    spearman_correlation,
    upper_tail_cvar,
    wilson_upper,
)


def test_upper_tail_cvar_uses_fractional_boundary_mass() -> None:
    assert upper_tail_cvar([0.0, 0.2, 0.6, 1.0], 0.50) == pytest.approx(0.8)
    assert upper_tail_cvar([0.0, 0.2, 0.6, 1.0], 0.375) == pytest.approx(
        (1.0 + 0.5 * 0.6) / 1.5
    )


def test_cvar_ucb_is_conservative_and_shrinks_with_sample_size() -> None:
    small = dkw_cvar_ucb([0.2] * 20, 0.5, 0.05)
    large = dkw_cvar_ucb([0.2] * 2000, 0.5, 0.05)
    assert 0.2 <= large < small <= 1.0


def test_probability_and_difference_bounds() -> None:
    assert wilson_upper(0, 100, 0.05) < 0.05
    assert wilson_upper(10, 100, 0.05) > 0.10
    assert hoeffding_difference_lower([1.0] * 100, 0.05) > 0.7


def test_spearman_handles_ties_and_direction() -> None:
    assert spearman_correlation([1, 2, 3], [10, 20, 30]) == pytest.approx(1.0)
    assert spearman_correlation([1, 2, 3], [30, 20, 10]) == pytest.approx(-1.0)
    assert spearman_correlation([1, 1, 2], [3, 3, 5]) == pytest.approx(1.0)


@pytest.mark.parametrize("tail_fraction", [0.0, -0.1, 1.1])
def test_cvar_rejects_invalid_tail_mass(tail_fraction: float) -> None:
    with pytest.raises(ValueError, match="tail_fraction"):
        upper_tail_cvar([0.1], tail_fraction)
