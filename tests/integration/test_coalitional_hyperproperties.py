from agent_defense_evals.analysis.hyperproperties import (
    ForbiddenFlowRule,
    evaluate_forbidden_flow,
)
from agent_defense_evals.core.schemas import ActionKind, EventKind
from agent_defense_evals.experiments.coalitional_hyperproperties import (
    CoalitionalHyperpropertySpec,
    TopologyKind,
    _run_episode,
    run_coalitional_hyperproperties,
)


def test_phase4_acceptance_gates_and_minimal_coalition() -> None:
    report = run_coalitional_hyperproperties(
        CoalitionalHyperpropertySpec(
            experiment_id="phase4-test",
            base_seed=9,
            topologies=(TopologyKind.CHAIN, TopologyKind.DENSE),
        )
    )

    assert all(report.gates.values())
    assert all(
        result.minimal_violating_coalitions == (("planner", "reviewer"),)
        for result in report.topologies
    )
    assert all(result.authorization_gate_blocked_harm for result in report.topologies)
    chain, dense = report.topologies
    assert chain.bag_local_checks < chain.exhaustive_checks
    assert dense.bag_local_checks == dense.exhaustive_checks


def test_harmful_execution_is_irreversible_and_provenance_localized() -> None:
    spec = CoalitionalHyperpropertySpec(
        experiment_id="phase4-trace-test",
        base_seed=11,
        topologies=(TopologyKind.CHAIN,),
    )
    result, trace = _run_episode(
        spec,
        TopologyKind.CHAIN,
        frozenset({"planner", "reviewer"}),
    )
    executions = [
        event
        for event in trace.by_kind(EventKind.ACTION_APPLIED)
        if event.payload["action"]["kind"] == ActionKind.EXECUTE_ARTIFACT.value
    ]
    violations = evaluate_forbidden_flow(
        trace,
        ForbiddenFlowRule(
            rule_id="protected-flow",
            source_classification="protected",
            sink="external",
        ),
    )

    assert result.security.violation
    assert len(executions) == 1
    assert not executions[0].reversible
    assert len(violations) == 1
    assert len(violations[0].subgraph_event_ids) < len(trace.events)
