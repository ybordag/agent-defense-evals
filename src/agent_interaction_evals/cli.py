"""Command-line interface for experiment utilities."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from agent_interaction_evals.smoke import run_phase0_smoke


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-interaction-evals")
    subparsers = parser.add_subparsers(dest="command", required=True)

    smoke = subparsers.add_parser(
        "phase0-smoke", help="run the Phase 0 configuration/event round trip"
    )
    smoke.add_argument(
        "--config", type=Path, default=Path("configs/experiment.yaml")
    )
    smoke.add_argument(
        "--output", type=Path, default=Path("artifacts/phase0-smoke.jsonl")
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command == "phase0-smoke":
        event = run_phase0_smoke(args.config, args.output)
        print(
            f"phase0 gate passed: episode={event.episode_id} "
            f"artifact={args.output}"
        )
