from pathlib import Path

import pytest

from agent_defense_evals.core.config import load_yaml
from agent_defense_evals.experiments.tail_robustness.contracts import (
    TailExperimentSpec,
    TailSplit,
    content_sha256,
)
from agent_defense_evals.experiments.tail_robustness.reporting import (
    finalize_tail_report,
)
from agent_defense_evals.experiments.tail_robustness.runner import (
    build_tail_manifest,
    run_tail_split,
    select_tail_stacks,
    validate_tail_manifest,
)

CONFIG = Path("configs/experiments/phase7_tail_robustness_synthetic.yaml")


def _pipeline():
    spec = load_yaml(CONFIG, TailExperimentSpec)
    manifest = build_tail_manifest(spec, "test-revision")
    validation = run_tail_split(spec, manifest, TailSplit.VALIDATION)
    selection = select_tail_stacks(spec, manifest, validation)
    test = run_tail_split(spec, manifest, TailSplit.TEST, selection)
    report = finalize_tail_report(spec, manifest, selection, validation, test)
    return spec, manifest, validation, selection, test, report


def test_complete_pipeline_is_deterministic_and_reports_all_experiments() -> None:
    spec, manifest, validation, selection, test, report = _pipeline()
    repeated_manifest = build_tail_manifest(spec, "test-revision")
    repeated_validation = run_tail_split(spec, repeated_manifest, TailSplit.VALIDATION)

    assert repeated_manifest == manifest
    assert repeated_validation == validation
    assert len(manifest.assignments) == 2400
    assert len(validation.outcomes) == len(test.outcomes) == 1200
    assert set(selection.selectors) == {
        "pooled_mean",
        "pooled_cvar",
        "worst_cell_mean",
        "hierarchical_tail",
        "ucb_tail",
    }
    assert set(report) >= {"E01", "E02", "E03", "E04", "E05"}
    assert report["evidence_scope"] == "controlled_synthetic"
    assert report["E02"]["success"] is True
    assert report["E03"]["success"] is True
    assert report["E05"]["success"] is True
    assert report["report_sha256"] == content_sha256(
        {key: value for key, value in report.items() if key != "report_sha256"}
    )


def test_test_split_requires_frozen_validation_selection() -> None:
    spec = load_yaml(CONFIG, TailExperimentSpec)
    manifest = build_tail_manifest(spec, "test-revision")
    with pytest.raises(ValueError, match="requires a frozen selection"):
        run_tail_split(spec, manifest, TailSplit.TEST)

    validation = run_tail_split(spec, manifest, TailSplit.VALIDATION)
    with pytest.raises(ValueError, match="requires a validation artifact"):
        select_tail_stacks(
            spec,
            manifest,
            validation.model_copy(update={"split": TailSplit.TEST}),
        )


def test_hashes_and_exact_manifest_coverage_reject_tampering() -> None:
    spec = load_yaml(CONFIG, TailExperimentSpec)
    manifest = build_tail_manifest(spec, "test-revision")
    changed = manifest.model_copy(update={"implementation_revision": "changed"})
    with pytest.raises(ValueError, match="content hash mismatch"):
        validate_tail_manifest(spec, changed)

    validation = run_tail_split(spec, manifest, TailSplit.VALIDATION)
    selection = select_tail_stacks(spec, manifest, validation)
    changed_selection = selection.model_copy(
        update={"selectors": {**selection.selectors, "ucb_tail": "observe-only"}}
    )
    with pytest.raises(ValueError, match="content hash mismatch"):
        run_tail_split(spec, manifest, TailSplit.TEST, changed_selection)


def test_test_outcomes_cannot_change_validation_selection() -> None:
    spec, manifest, validation, selection, test, _ = _pipeline()
    replaced = tuple(
        item.model_copy(update={"security_loss": 1.0 - item.security_loss})
        for item in test.outcomes
    )
    changed_test = test.model_copy(update={"outcomes": replaced})

    # Selection is already frozen and contains no field derived from test.
    assert select_tail_stacks(spec, manifest, validation) == selection
    assert changed_test.outcomes != test.outcomes
