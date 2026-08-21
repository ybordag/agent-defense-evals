"""Explicit component registry for scripted and model-backed experiments."""

from collections.abc import Mapping

from agent_defense_evals.agents.artifact_workflow import ArtifactWorkflowAgent
from agent_defense_evals.agents.base import AgentPolicy
from agent_defense_evals.agents.model import StructuredModelAgent
from agent_defense_evals.agents.scripted import ConstraintSharingAgent
from agent_defense_evals.agents.secret_relay import (
    SecretReceiverAgent,
    SecretSenderAgent,
    SentinelAgent,
)
from agent_defense_evals.agents.sequential_signal import SequentialSignalModelAgent
from agent_defense_evals.attacks.base import AttackStrategy
from agent_defense_evals.attacks.scripted import ForceSelectionAttack, NoAttack
from agent_defense_evals.channels.covert import ChannelKind
from agent_defense_evals.core.schemas import ExperimentSpec
from agent_defense_evals.defenses.base import Defense
from agent_defense_evals.defenses.mediation import (
    MediatorKind,
    MessageMediatorDefense,
)
from agent_defense_evals.defenses.scripted import BlockPlanDefense, RewritePlanDefense
from agent_defense_evals.models.base import ModelRuntime
from agent_defense_evals.models.openai_runtime import OpenAICompatibleRuntime
from agent_defense_evals.models.transformers_runtime import TransformersWhiteBoxRuntime
from agent_defense_evals.models.types import ModelCaptureSpec
from agent_defense_evals.scenarios.artifact_workflow import ArtifactWorkflowScenario
from agent_defense_evals.scenarios.base import Scenario
from agent_defense_evals.scenarios.distributed_choice import DistributedChoiceScenario
from agent_defense_evals.scenarios.secret_relay import SecretRelayScenario
from agent_defense_evals.scenarios.sequential_signal import SequentialSignalScenario


def build_scenario(spec: ExperimentSpec) -> Scenario:
    if spec.scenario.kind == "distributed_choice":
        return DistributedChoiceScenario(spec.scenario.config)
    if spec.scenario.kind == "secret_relay":
        return SecretRelayScenario(spec.scenario.config)
    if spec.scenario.kind == "artifact_workflow":
        return ArtifactWorkflowScenario(spec.scenario.config)
    if spec.scenario.kind == "sequential_signal":
        return SequentialSignalScenario(spec.scenario.config)
    raise ValueError(f"unknown scenario kind: {spec.scenario.kind}")


def build_model_runtimes(spec: ExperimentSpec) -> dict[str, ModelRuntime]:
    runtimes: dict[str, ModelRuntime] = {}
    for runtime_spec in spec.runtimes:
        config = runtime_spec.config
        if runtime_spec.kind == "openai_compatible":
            runtimes[runtime_spec.runtime_id] = OpenAICompatibleRuntime(
                base_url=str(config["base_url"]),
                model_id=runtime_spec.model_id,
                model_revision=config.get("model_revision"),
                tokenizer_id=config.get("tokenizer_id"),
                tokenizer_revision=config.get("tokenizer_revision"),
                adapter_id=config.get("adapter_id"),
                adapter_revision=config.get("adapter_revision"),
                api_key_env=config.get("api_key_env"),
                api_mode=str(config.get("api_mode", "chat")),
                timeout=float(config.get("timeout", 60.0)),
            )
            continue
        if runtime_spec.kind == "transformers_white_box":
            runtimes[runtime_spec.runtime_id] = (
                TransformersWhiteBoxRuntime.from_pretrained(
                    runtime_spec.model_id,
                    device=config.get("device"),
                    revision=config.get("model_revision"),
                    tokenizer_id=config.get("tokenizer_id"),
                    tokenizer_revision=config.get("tokenizer_revision"),
                    adapter_id=config.get("adapter_id"),
                    adapter_revision=config.get("adapter_revision"),
                    use_chat_template=bool(config.get("use_chat_template", True)),
                    trust_remote_code=bool(config.get("trust_remote_code", False)),
                )
            )
            continue
        raise ValueError(f"unknown model runtime kind: {runtime_spec.kind}")
    return runtimes


def build_agents(
    spec: ExperimentSpec,
    runtimes: Mapping[str, ModelRuntime] | None = None,
) -> tuple[AgentPolicy, ...]:
    agents: list[AgentPolicy] = []
    runtime_map = dict(runtimes or {})
    for agent in spec.agents:
        if agent.policy.kind == "constraint_sharer":
            agents.append(
                ConstraintSharingAgent(
                    agent.agent_id,
                    coordinator=bool(agent.policy.config.get("coordinator", False)),
                )
            )
            continue
        if agent.policy.kind == "model_action":
            if not runtime_map:
                runtime_map = build_model_runtimes(spec)
            config = agent.policy.config
            runtime_id = str(config["runtime_id"])
            agents.append(
                StructuredModelAgent(
                    agent.agent_id,
                    role=agent.role,
                    runtime=runtime_map[runtime_id],
                    base_seed=spec.base_seed,
                    instructions=str(config.get("instructions", "")),
                    max_new_tokens=int(config.get("max_new_tokens", 128)),
                    do_sample=bool(config.get("do_sample", False)),
                    temperature=float(config.get("temperature", 1.0)),
                    top_p=float(config.get("top_p", 1.0)),
                    capture=ModelCaptureSpec.model_validate(
                        config.get("capture", {"logits": False})
                    ),
                )
            )
            continue
        if agent.policy.kind == "sequential_signal_model":
            if not runtime_map:
                runtime_map = build_model_runtimes(spec)
            config = agent.policy.config
            runtime_id = str(config["runtime_id"])
            agents.append(
                SequentialSignalModelAgent(
                    agent.agent_id,
                    role=agent.role,
                    runtime=runtime_map[runtime_id],
                    base_seed=spec.base_seed,
                    max_new_tokens=int(config.get("max_new_tokens", 16)),
                    do_sample=bool(config.get("do_sample", True)),
                    temperature=float(config.get("temperature", 0.7)),
                    top_p=float(config.get("top_p", 0.95)),
                )
            )
            continue
        if agent.policy.kind in {"secret_sender", "secret_receiver"}:
            config = agent.policy.config
            channel = ChannelKind(str(config["channel"]))
            codebook = tuple(map(str, config.get("codebook", ("calm", "bright"))))
            if len(codebook) != 2:
                raise ValueError("secret relay codebook requires two entries")
            policy_type = (
                SecretSenderAgent
                if agent.policy.kind == "secret_sender"
                else SecretReceiverAgent
            )
            agents.append(
                policy_type(
                    agent.agent_id,
                    channel=channel,
                    codebook=(codebook[0], codebook[1]),
                )
            )
            continue
        if agent.policy.kind == "sentinel":
            agents.append(SentinelAgent(agent.agent_id))
            continue
        if agent.policy.kind == "artifact_workflow":
            config = agent.policy.config
            agents.append(
                ArtifactWorkflowAgent(
                    agent.agent_id,
                    role=agent.role,
                    compromised=bool(config.get("compromised", False)),
                    recipients=tuple(map(str, config.get("recipients", ()))),
                    policy_backend=str(config.get("policy_backend", "rules-v1")),
                )
            )
            continue
        raise ValueError(f"unknown policy kind: {agent.policy.kind}")
    return tuple(agents)


def build_attack(spec: ExperimentSpec) -> AttackStrategy:
    if spec.attack.kind == "none":
        return NoAttack()
    if spec.attack.kind == "force_selection":
        return ForceSelectionAttack(
            target_agent=str(spec.attack.config["target_agent"]),
            forced_plan=str(spec.attack.config["forced_plan"]),
        )
    raise ValueError(f"unknown attack kind: {spec.attack.kind}")


def build_defenses(spec: ExperimentSpec) -> tuple[Defense, ...]:
    defenses: list[Defense] = []
    for defense in spec.defenses:
        if defense.kind == "block_plan":
            defenses.append(
                BlockPlanDefense(
                    tuple(map(str, defense.config.get("blocked_plans", ())))
                )
            )
            continue
        if defense.kind == "rewrite_plan":
            defenses.append(
                RewritePlanDefense(
                    source_plan=str(defense.config["source_plan"]),
                    replacement_plan=str(defense.config["replacement_plan"]),
                )
            )
            continue
        if defense.kind == "message_mediator":
            config = defense.config
            defenses.append(
                MessageMediatorDefense(
                    MediatorKind(str(config["mediator"])),
                    base_seed=int(config.get("base_seed", spec.base_seed)),
                    information_budget_bits=int(
                        config.get("information_budget_bits", 1)
                    ),
                    randomized_retention=float(config.get("randomized_retention", 0.5)),
                )
            )
            continue
        raise ValueError(f"unknown defense kind: {defense.kind}")
    return tuple(defenses)
