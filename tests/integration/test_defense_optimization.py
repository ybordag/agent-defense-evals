from pathlib import Path

import pytest
from pydantic import ValidationError

from agent_defense_evals.core.config import load_yaml
from agent_defense_evals.experiments.defense_optimization import (
    DefenseOptimizationSpec,
    OptimizationSplit,
    run_defense_optimization,
)

CONFIG = Path("configs/experiments/phase7_controlled_optimization.yaml")


def test_optimizer_selects_without_test_leakage_and_exports_shadow_policy() -> None:
    spec = load_yaml(CONFIG, DefenseOptimizationSpec)
    report = run_defense_optimization(spec)

    assert all(report.gates.values())
    assert report.selected_stack_id == "layered-capacity-provenance"
    assert report.selection_split is OptimizationSplit.VALIDATION
    assert report.shadow_policy.enforcement_mode == "shadow"
    assert report.shadow_policy.selected_stack_id == report.selected_stack_id
    assert report.validation_to_test_worst_case_gap == pytest.approx(0.16)
    assert report.validation_to_test_cvar_gap == pytest.approx(0.15)
    assert {item.axis for item in report.held_out_coverage} == {
        "model_family",
        "prompt_family",
        "attack_family",
        "topology",
        "coalition_size",
        "horizon",
    }
    assert all(item.held_out_test_values for item in report.held_out_coverage)

    changed_test = tuple(
        case.model_copy(
            update={
                "outcomes": {
                    stack_id: outcome.model_copy(
                        update={
                            "security_loss": 1.0,
                            "security_loss_lower": 1.0,
                            "security_loss_upper": 1.0,
                        }
                    )
                    for stack_id, outcome in case.outcomes.items()
                }
            }
        )
        if case.split is OptimizationSplit.TEST
        else case
        for case in spec.cases
    )
    changed_report = run_defense_optimization(
        spec.model_copy(update={"cases": changed_test})
    )
    assert changed_report.selected_stack_id == report.selected_stack_id


def test_optimizer_rejects_incomplete_matrix_and_missing_holdout() -> None:
    spec = load_yaml(CONFIG, DefenseOptimizationSpec)
    first = spec.cases[0]
    incomplete = first.model_copy(
        update={"outcomes": {"observe-only": first.outcomes["observe-only"]}}
    )
    with pytest.raises(ValidationError, match="evaluate every defense stack"):
        DefenseOptimizationSpec.model_validate(
            {**spec.model_dump(mode="python"), "cases": (incomplete, *spec.cases[1:])}
        )

    no_model_holdout = tuple(
        case.model_copy(update={"model_family": "qwen"}) for case in spec.cases
    )
    with pytest.raises(ValidationError, match="held-out model_family"):
        DefenseOptimizationSpec.model_validate(
            {**spec.model_dump(mode="python"), "cases": no_model_holdout}
        )


def test_utility_floor_changes_only_validation_selection() -> None:
    spec = load_yaml(CONFIG, DefenseOptimizationSpec)
    report = run_defense_optimization(spec.model_copy(update={"utility_floor": 0.85}))

    assert report.selected_stack_id == "paraphrase-gate"
    selected_validation = next(
        result
        for result in report.results
        if result.stack_id == report.selected_stack_id
        and result.split is OptimizationSplit.VALIDATION
    )
    assert selected_validation.minimum_utility >= 0.85
