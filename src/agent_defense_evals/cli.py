"""Command-line interface for validation, execution, and replay."""

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from agent_defense_evals.core.config import load_experiment, load_yaml
from agent_defense_evals.core.events import JsonlEventStore
from agent_defense_evals.core.factory import (
    build_agents,
    build_attack,
    build_defenses,
    build_scenario,
)
from agent_defense_evals.core.runner import ExperimentRunner
from agent_defense_evals.core.schemas import EventKind
from agent_defense_evals.core.trace import Trace
from agent_defense_evals.defenses.gateway import DefenseGateway
from agent_defense_evals.experiments.anytime_evidence import (
    AnytimeEvidenceSpec,
    run_anytime_evidence,
)
from agent_defense_evals.experiments.causal_information import (
    CausalInformationSpec,
    run_causal_information,
)
from agent_defense_evals.experiments.coalitional_hyperproperties import (
    CoalitionalHyperpropertySpec,
    run_coalitional_hyperproperties,
)
from agent_defense_evals.experiments.heterogeneous_policy_audit import (
    HeterogeneousPolicyAuditSpec,
    run_heterogeneous_policy_audit,
)
from agent_defense_evals.experiments.white_box_information import (
    WhiteBoxInformationSpec,
    run_white_box_information,
)
from agent_defense_evals.instrumentation.provenance import ProvenanceGraph


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-defense-evals")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-config")
    validate.add_argument("--config", type=Path, required=True)

    run = subparsers.add_parser("run")
    run.add_argument("--config", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)

    replay = subparsers.add_parser("replay")
    replay.add_argument("--events", type=Path, required=True)

    phase3 = subparsers.add_parser("phase3-run")
    phase3.add_argument("--config", type=Path, required=True)
    phase3.add_argument("--output", type=Path, required=True)

    phase3_white_box = subparsers.add_parser("phase3-white-box")
    phase3_white_box.add_argument("--config", type=Path, required=True)
    phase3_white_box.add_argument("--output", type=Path, required=True)

    phase4 = subparsers.add_parser("phase4-run")
    phase4.add_argument("--config", type=Path, required=True)
    phase4.add_argument("--output", type=Path, required=True)

    phase4_model = subparsers.add_parser("phase4-model-audit")
    phase4_model.add_argument("--config", type=Path, required=True)
    phase4_model.add_argument("--output", type=Path, required=True)

    phase5 = subparsers.add_parser("phase5-run")
    phase5.add_argument("--config", type=Path, required=True)
    phase5.add_argument("--output", type=Path, required=True)
    return parser


def build_runner(config_path: Path) -> ExperimentRunner:
    spec = load_experiment(config_path)
    return ExperimentRunner(
        spec=spec,
        scenario=build_scenario(spec),
        agents=build_agents(spec),
        attack=build_attack(spec),
        gateway=DefenseGateway(build_defenses(spec)),
    )


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command == "validate-config":
        spec = load_experiment(args.config)
        print(spec.model_dump_json(indent=2))
        return
    if args.command == "run":
        result, trace = build_runner(args.config).run()
        JsonlEventStore(args.output).replace(trace.events)
        print(result.model_dump_json(indent=2))
        return
    if args.command == "replay":
        trace = Trace(JsonlEventStore(args.events).read())
        graph = ProvenanceGraph(trace)
        completed = trace.by_kind(EventKind.EPISODE_COMPLETED)
        if len(completed) != 1:
            raise RuntimeError(
                "a replayable trace requires exactly one completion event"
            )
        terminal = completed[0]
        summary = {
            "episode_id": str(terminal.episode_id),
            "event_count": len(trace.events),
            "provenance_nodes": graph.node_count,
            "completion_ancestor_count": len(graph.ancestors(terminal.event_id)),
            "outcome": terminal.payload,
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return
    if args.command == "phase3-run":
        spec = load_yaml(args.config, CausalInformationSpec)
        report = run_causal_information(spec)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            report.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        print(report.model_dump_json(indent=2))
        return
    if args.command == "phase3-white-box":
        spec = load_yaml(args.config, WhiteBoxInformationSpec)
        report = run_white_box_information(spec)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            report.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        print(report.model_dump_json(indent=2))
        return
    if args.command == "phase4-run":
        spec = load_yaml(args.config, CoalitionalHyperpropertySpec)
        report = run_coalitional_hyperproperties(spec)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            report.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        print(report.model_dump_json(indent=2))
        return
    if args.command == "phase4-model-audit":
        spec = load_yaml(args.config, HeterogeneousPolicyAuditSpec)
        report = run_heterogeneous_policy_audit(spec)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            report.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        print(report.model_dump_json(indent=2))
        return
    if args.command == "phase5-run":
        spec = load_yaml(args.config, AnytimeEvidenceSpec)
        report = run_anytime_evidence(spec)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            report.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        print(report.model_dump_json(indent=2))
