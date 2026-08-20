"""Deterministic event-sourced multi-agent runner."""

from collections.abc import Iterable
from typing import Any
from uuid import UUID

from agent_defense_evals.agents.base import AgentPolicy
from agent_defense_evals.attacks.base import AttackStrategy
from agent_defense_evals.core.schemas import (
    AgentAction,
    DecisionKind,
    EpisodeResult,
    EventKind,
    EventRecord,
    ExperimentSpec,
)
from agent_defense_evals.core.seeding import (
    derive_episode_id,
    derive_event_id,
    derive_run_id,
    derive_seed,
)
from agent_defense_evals.core.trace import Trace
from agent_defense_evals.defenses.gateway import DefenseGateway
from agent_defense_evals.models.types import generation_event_payload
from agent_defense_evals.scenarios.base import Scenario


class EventRecorder:
    def __init__(
        self,
        *,
        experiment_id: str,
        episode_id: UUID,
        trace: Trace,
    ) -> None:
        self.experiment_id = experiment_id
        self.episode_id = episode_id
        self.trace = trace
        self.logical_time = 0

    def record(
        self,
        kind: EventKind,
        *,
        step: int,
        actor_id: str | None = None,
        recipient_ids: tuple[str, ...] = (),
        parent_ids: tuple[UUID, ...] = (),
        payload: dict[str, Any] | None = None,
        risk_level: float = 0.0,
        reversible: bool = True,
    ) -> EventRecord:
        event = EventRecord(
            event_id=derive_event_id(
                self.episode_id, self.logical_time, kind.value, actor_id
            ),
            experiment_id=self.experiment_id,
            episode_id=self.episode_id,
            step=step,
            logical_time=self.logical_time,
            actor_id=actor_id,
            recipient_ids=recipient_ids,
            kind=kind,
            parent_ids=parent_ids,
            payload=payload or {},
            risk_level=risk_level,
            reversible=reversible,
        )
        self.trace.append(event)
        self.logical_time += 1
        return event


class ExperimentRunner:
    def __init__(
        self,
        *,
        spec: ExperimentSpec,
        scenario: Scenario,
        agents: Iterable[AgentPolicy],
        attack: AttackStrategy,
        gateway: DefenseGateway,
    ) -> None:
        self.spec = spec
        self.scenario = scenario
        self.agents = tuple(agents)
        self.attack = attack
        self.gateway = gateway
        configured_ids = tuple(agent.agent_id for agent in self.agents)
        if set(configured_ids) != set(self.scenario.agent_ids):
            raise ValueError("agent IDs must match scenario private views")

    def run(self) -> tuple[EpisodeResult, Trace]:
        run_id = derive_run_id(self.spec)
        episode_seed = derive_seed(self.spec.base_seed, "episode", 0)
        episode_id = derive_episode_id(run_id, episode_seed)
        self.scenario.reset(episode_id, episode_seed)
        trace = Trace()
        recorder = EventRecorder(
            experiment_id=self.spec.experiment_id,
            episode_id=episode_id,
            trace=trace,
        )
        started = recorder.record(
            EventKind.EPISODE_STARTED,
            step=0,
            payload={
                "run_id": str(run_id),
                "episode_seed": episode_seed,
                "spec": self.spec.model_dump(mode="json"),
            },
        )
        frontier: tuple[UUID, ...] = (started.event_id,)
        steps_executed = 0

        for step in range(self.spec.max_steps):
            steps_executed = step + 1
            proposals: list[tuple[AgentAction, EventRecord]] = []
            for agent in self.agents:
                observation = self.scenario.observe(agent.agent_id, step)
                observed = recorder.record(
                    EventKind.OBSERVATION_EMITTED,
                    step=step,
                    actor_id="scenario",
                    recipient_ids=(agent.agent_id,),
                    parent_ids=frontier,
                    payload={"observation": observation.model_dump(mode="json")},
                )
                policy_decision = agent.act(observation)
                action_parent = observed.event_id
                if policy_decision.generation is not None:
                    if policy_decision.request is None:
                        raise RuntimeError("model generation is missing its request")
                    generated = recorder.record(
                        EventKind.MODEL_GENERATED,
                        step=step,
                        actor_id=agent.agent_id,
                        recipient_ids=(agent.agent_id,),
                        parent_ids=(observed.event_id,),
                        payload=generation_event_payload(
                            policy_decision.request,
                            policy_decision.generation,
                        ),
                    )
                    action_parent = generated.event_id
                action = policy_decision.action
                proposed = recorder.record(
                    EventKind.ACTION_PROPOSED,
                    step=step,
                    actor_id=agent.agent_id,
                    recipient_ids=action.recipient_ids,
                    parent_ids=(action_parent,),
                    payload={"action": action.model_dump(mode="json")},
                )
                proposals.append((action, proposed))

            next_frontier: list[UUID] = []
            for raw_action, proposed in proposals:
                action = self.attack.transform_action(
                    raw_action,
                    step=step,
                    scenario_state=self.scenario.snapshot(),
                )
                action_parent = proposed.event_id
                if action != raw_action:
                    mutated = recorder.record(
                        EventKind.ATTACK_MUTATED,
                        step=step,
                        actor_id=self.attack.attack_id,
                        recipient_ids=action.recipient_ids,
                        parent_ids=(proposed.event_id,),
                        payload={
                            "before": raw_action.model_dump(mode="json"),
                            "after": action.model_dump(mode="json"),
                        },
                        risk_level=0.8,
                    )
                    action_parent = mutated.event_id

                decisions = self.gateway.evaluate(
                    action,
                    step=step,
                    scenario_state=self.scenario.snapshot(),
                )
                decision_parent = action_parent
                for decision in decisions:
                    decided = recorder.record(
                        EventKind.DEFENSE_DECIDED,
                        step=step,
                        actor_id=decision.defense_id,
                        recipient_ids=(action.actor_id,),
                        parent_ids=(decision_parent,),
                        payload={"decision": decision.model_dump(mode="json")},
                    )
                    decision_parent = decided.event_id

                final_decision = decisions[-1]
                if final_decision.decision is DecisionKind.BLOCK:
                    next_frontier.append(decision_parent)
                    continue
                self.scenario.apply(final_decision.action)
                applied = recorder.record(
                    EventKind.ACTION_APPLIED,
                    step=step,
                    actor_id=final_decision.action.actor_id,
                    recipient_ids=final_decision.action.recipient_ids,
                    parent_ids=(decision_parent,),
                    payload={
                        "action": final_decision.action.model_dump(mode="json"),
                        "scenario": self.scenario.snapshot(),
                    },
                )
                next_frontier.append(applied.event_id)

            frontier = tuple(next_frontier)
            if self.scenario.is_terminal():
                break

        utility = self.scenario.utility_outcome()
        security = self.scenario.security_outcome()
        completed = recorder.record(
            EventKind.EPISODE_COMPLETED,
            step=steps_executed,
            actor_id="runner",
            parent_ids=frontier,
            payload={
                "scenario": self.scenario.snapshot(),
                "utility": utility.model_dump(mode="json"),
                "security": security.model_dump(mode="json"),
                "dimensions": self.spec.dimensions.model_dump(mode="json"),
            },
            risk_level=min(1.0, security.loss),
        )
        selected_plan = self.scenario.snapshot().get("selected_plan")
        result = EpisodeResult(
            experiment_id=self.spec.experiment_id,
            episode_id=episode_id,
            run_id=run_id,
            steps=steps_executed,
            selected_plan=selected_plan,
            utility=utility,
            security=security,
            event_count=len(trace.events),
        )
        if trace.events[-1] != completed:
            raise RuntimeError("completed event must terminate the trace")
        return result, trace
