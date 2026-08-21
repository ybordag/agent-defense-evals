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
from agent_defense_evals.experiments.capacity_shaping import (
    CapacityShapingSpec,
    run_capacity_shaping,
)
from agent_defense_evals.experiments.causal_information import (
    CausalInformationSpec,
    run_causal_information,
)
from agent_defense_evals.experiments.coalitional_hyperproperties import (
    CoalitionalHyperpropertySpec,
    run_coalitional_hyperproperties,
)
from agent_defense_evals.experiments.confirmatory_evidence import (
    ConfirmatoryManifest,
    ConfirmatoryShardArtifact,
    ConfirmatorySplit,
    build_manifest,
    finalize_confirmatory_report,
)
from agent_defense_evals.experiments.confirmatory_model import (
    ConfirmatoryExecutionSpec,
    run_confirmatory_shard,
)
from agent_defense_evals.experiments.defense_optimization import (
    DefenseOptimizationSpec,
    run_defense_optimization,
)
from agent_defense_evals.experiments.heterogeneous_policy_audit import (
    HeterogeneousPolicyAuditSpec,
    run_heterogeneous_policy_audit,
)
from agent_defense_evals.experiments.model_capacity_transfer import (
    ModelCapacityTransferSpec,
    run_model_capacity_transfer,
)
from agent_defense_evals.experiments.model_trace_evidence import (
    ModelTraceEvidenceSpec,
    run_model_trace_evidence,
)
from agent_defense_evals.experiments.model_workflow_remediation import (
    ModelWorkflowRemediationSpec,
    run_model_workflow_remediation,
)
from agent_defense_evals.experiments.white_box_information import (
    WhiteBoxInformationSpec,
    run_white_box_information,
)
from agent_defense_evals.instrumentation.provenance import ProvenanceGraph


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


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

    phase5_model = subparsers.add_parser("phase5-model-run")
    phase5_model.add_argument("--config", type=Path, required=True)
    phase5_model.add_argument("--output", type=Path, required=True)

    phase5_plan = subparsers.add_parser("phase5-confirmatory-plan")
    phase5_plan.add_argument("--config", type=Path, required=True)
    phase5_plan.add_argument("--output", type=Path, required=True)
    phase5_plan.add_argument("--implementation-revision", required=True)

    phase5_confirmatory = subparsers.add_parser("phase5-confirmatory-run")
    phase5_confirmatory.add_argument("--config", type=Path, required=True)
    phase5_confirmatory.add_argument("--manifest", type=Path, required=True)
    phase5_confirmatory.add_argument("--output", type=Path, required=True)
    phase5_confirmatory.add_argument("--shard-index", type=int, default=0)
    phase5_confirmatory.add_argument("--shard-count", type=int, default=1)
    phase5_confirmatory.add_argument("--max-new-episodes", type=int)
    phase5_confirmatory.add_argument(
        "--split",
        choices=tuple(item.value for item in ConfirmatorySplit),
        required=True,
    )
    phase5_confirmatory.add_argument("--implementation-revision", required=True)

    phase5_report = subparsers.add_parser("phase5-confirmatory-report")
    phase5_report.add_argument("--config", type=Path, required=True)
    phase5_report.add_argument("--manifest", type=Path, required=True)
    phase5_report.add_argument("--shards", type=Path, nargs="+", required=True)
    phase5_report.add_argument("--output", type=Path, required=True)
    phase5_report.add_argument("--implementation-revision", required=True)

    phase6 = subparsers.add_parser("phase6-run")
    phase6.add_argument("--config", type=Path, required=True)
    phase6.add_argument("--output", type=Path, required=True)

    phase7 = subparsers.add_parser("phase7-run")
    phase7.add_argument("--config", type=Path, required=True)
    phase7.add_argument("--output", type=Path, required=True)

    phase7_model = subparsers.add_parser("phase7-model-capacity")
    phase7_model.add_argument("--config", type=Path, required=True)
    phase7_model.add_argument("--output", type=Path, required=True)

    phase7_workflow = subparsers.add_parser("phase7-model-workflow")
    phase7_workflow.add_argument("--config", type=Path, required=True)
    phase7_workflow.add_argument("--output", type=Path, required=True)
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
        return
    if args.command == "phase5-model-run":
        spec = load_yaml(args.config, ModelTraceEvidenceSpec)
        report = run_model_trace_evidence(spec)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            report.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        print(report.model_dump_json(indent=2))
        return
    if args.command == "phase5-confirmatory-plan":
        spec = load_yaml(args.config, ConfirmatoryExecutionSpec)
        manifest = build_manifest(
            spec.design,
            implementation_revision=args.implementation_revision,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            manifest.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        print(
            json.dumps(
                {
                    "assignments": len(manifest.assignments),
                    "implementation_revision": manifest.implementation_revision,
                    "specification_sha256": manifest.specification_sha256,
                    "manifest_sha256": manifest.manifest_sha256,
                    "output": str(args.output),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.command == "phase5-confirmatory-run":
        spec = load_yaml(args.config, ConfirmatoryExecutionSpec)
        manifest = ConfirmatoryManifest.model_validate_json(
            args.manifest.read_text(encoding="utf-8")
        )
        existing = (
            ConfirmatoryShardArtifact.model_validate_json(
                args.output.read_text(encoding="utf-8")
            )
            if args.output.exists()
            else None
        )

        def checkpoint(artifact: ConfirmatoryShardArtifact) -> None:
            _atomic_write(args.output, artifact.model_dump_json(indent=2) + "\n")

        shard = run_confirmatory_shard(
            spec,
            manifest,
            shard_index=args.shard_index,
            shard_count=args.shard_count,
            split=ConfirmatorySplit(args.split),
            implementation_revision=args.implementation_revision,
            existing=existing,
            checkpoint=checkpoint,
            max_new_episodes=args.max_new_episodes,
        )
        checkpoint(shard)
        print(
            json.dumps(
                {
                    "artifact_sha256": shard.artifact_sha256,
                    "episodes": len(shard.episodes),
                    "implementation_revision": shard.implementation_revision,
                    "output": str(args.output),
                    "shard_id": shard.shard_id,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.command == "phase5-confirmatory-report":
        spec = load_yaml(args.config, ConfirmatoryExecutionSpec)
        manifest = ConfirmatoryManifest.model_validate_json(
            args.manifest.read_text(encoding="utf-8")
        )
        if manifest.implementation_revision != args.implementation_revision:
            raise ValueError(
                "manifest implementation revision differs from report command"
            )
        shards = tuple(
            ConfirmatoryShardArtifact.model_validate_json(
                path.read_text(encoding="utf-8")
            )
            for path in args.shards
        )
        report = finalize_confirmatory_report(spec.design, manifest, shards)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            report.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        print(report.model_dump_json(indent=2))
        return
    if args.command == "phase6-run":
        spec = load_yaml(args.config, CapacityShapingSpec)
        report = run_capacity_shaping(spec)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            report.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        print(report.model_dump_json(indent=2))
        return
    if args.command == "phase7-run":
        spec = load_yaml(args.config, DefenseOptimizationSpec)
        report = run_defense_optimization(spec)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            report.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        print(report.model_dump_json(indent=2))
        return
    if args.command == "phase7-model-capacity":
        spec = load_yaml(args.config, ModelCapacityTransferSpec)
        report = run_model_capacity_transfer(spec)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            report.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        print(report.model_dump_json(indent=2))
        return
    if args.command == "phase7-model-workflow":
        spec = load_yaml(args.config, ModelWorkflowRemediationSpec)
        report = run_model_workflow_remediation(spec)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            report.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        print(report.model_dump_json(indent=2))
