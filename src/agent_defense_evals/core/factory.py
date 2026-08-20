"""Small explicit component registry for the initial vertical slice."""

from agent_defense_evals.agents.base import AgentPolicy
from agent_defense_evals.agents.scripted import ConstraintSharingAgent
from agent_defense_evals.attacks.base import AttackStrategy
from agent_defense_evals.attacks.scripted import ForceSelectionAttack, NoAttack
from agent_defense_evals.core.schemas import ExperimentSpec
from agent_defense_evals.defenses.base import Defense
from agent_defense_evals.defenses.scripted import BlockPlanDefense, RewritePlanDefense
from agent_defense_evals.scenarios.base import Scenario
from agent_defense_evals.scenarios.distributed_choice import DistributedChoiceScenario


def build_scenario(spec: ExperimentSpec) -> Scenario:
    if spec.scenario.kind == "distributed_choice":
        return DistributedChoiceScenario(spec.scenario.config)
    raise ValueError(f"unknown scenario kind: {spec.scenario.kind}")


def build_agents(spec: ExperimentSpec) -> tuple[AgentPolicy, ...]:
    agents: list[AgentPolicy] = []
    for agent in spec.agents:
        if agent.policy.kind != "constraint_sharer":
            raise ValueError(f"unknown policy kind: {agent.policy.kind}")
        agents.append(
            ConstraintSharingAgent(
                agent.agent_id,
                coordinator=bool(agent.policy.config.get("coordinator", False)),
            )
        )
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
        raise ValueError(f"unknown defense kind: {defense.kind}")
    return tuple(defenses)
