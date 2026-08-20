from agent_defense_evals.experiments.anytime_evidence import (
    AnytimeEvidenceSpec,
    StreamCondition,
    run_anytime_evidence,
)


def test_phase5_first_increment_acceptance_gates() -> None:
    report = run_anytime_evidence(
        AnytimeEvidenceSpec(
            experiment_id="phase5-test",
            base_seed=17,
            horizon=128,
            calibration_episodes=80,
            evaluation_episodes=80,
            irreversible_delay=64,
        )
    )

    assert all(report.gates.values())
    diagnostics = {
        diagnostic.condition: diagnostic
        for diagnostic in report.calibration_diagnostics
    }
    assert diagnostics[StreamCondition.BENIGN_DRIFT].conditional_calibration_valid
    assert not diagnostics[
        StreamCondition.BENIGN_UNMODELED_SHIFT
    ].conditional_calibration_valid
    assert all(
        result.median_detection_delay is None
        or result.median_detection_delay >= 0.0
        for result in report.results
    )
