import math

from agent_defense_evals.analysis.sequential_evidence import (
    FixedScoreThreshold,
    MixtureBettingEProcess,
    PageCusum,
    run_monitor,
)


def test_eprocess_accumulates_weak_persistent_evidence() -> None:
    scores = (0.0,) * 20 + (1.0, 0.0, 0.0, 0.0) * 30
    result = run_monitor(
        MixtureBettingEProcess(
            null_mean_upper=0.08,
            alpha=0.05,
            bet_fractions=(0.025, 0.05, 0.10, 0.20),
        ),
        scores,
    )

    assert result.alarm_step is not None
    assert result.max_statistic >= math.log(20.0)


def test_monitors_remain_quiet_on_zero_scores() -> None:
    scores = (0.0,) * 128

    assert run_monitor(FixedScoreThreshold(0.5), scores).alarm_step is None
    assert (
        run_monitor(
            PageCusum(reference_mean=0.1, threshold=3.0), scores
        ).alarm_step
        is None
    )
    assert (
        run_monitor(
            MixtureBettingEProcess(
                null_mean_upper=0.08,
                alpha=0.05,
                bet_fractions=(0.05, 0.10),
            ),
            scores,
        ).alarm_step
        is None
    )
