"""Command-line interface for validation, execution, and replay."""

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from agent_defense_evals.core.config import load_experiment
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
