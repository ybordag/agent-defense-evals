"""Planning, execution, and sealed selection for tail experiments."""

from __future__ import annotations

import hashlib

from agent_defense_evals.experiments.tail_robustness.contracts import (
    TailAssignment,
    TailExperimentSpec,
    TailManifest,
    TailOutcomeArtifact,
    TailSelectionArtifact,
    TailSplit,
    content_sha256,
    spec_sha256,
)
from agent_defense_evals.experiments.tail_robustness.selectors import select_stacks
from agent_defense_evals.experiments.tail_robustness.synthetic import (
    run_synthetic_assignment,
)


def _integer_seed(*parts: object) -> int:
    digest = hashlib.sha256(":".join(map(str, parts)).encode()).digest()
    return int.from_bytes(digest[:8]) % (2**63)


def _manifest_payload(manifest: TailManifest) -> dict[str, object]:
    payload = manifest.model_dump(mode="json")
    payload.pop("manifest_sha256")
    return payload


def _outcome_payload(artifact: TailOutcomeArtifact) -> dict[str, object]:
    payload = artifact.model_dump(mode="json")
    payload.pop("artifact_sha256")
    return payload


def _selection_payload(artifact: TailSelectionArtifact) -> dict[str, object]:
    payload = artifact.model_dump(mode="json")
    payload.pop("selection_sha256")
    return payload


def build_tail_manifest(
    spec: TailExperimentSpec, implementation_revision: str
) -> TailManifest:
    """Freeze a complete stack-by-cell-by-replicate assignment matrix."""

    specification_hash = spec_sha256(spec)
    assignments: list[TailAssignment] = []
    for cell in sorted(spec.cells, key=lambda item: item.cell_id):
        for replicate in range(spec.episodes_per_cell):
            paired_seed = _integer_seed(
                spec.base_seed, spec.experiment_id, cell.cell_id, replicate
            )
            for stack in sorted(spec.stacks, key=lambda item: item.stack_id):
                execution_seed = _integer_seed(paired_seed, stack.stack_id)
                assignment_id = hashlib.sha256(
                    (
                        f"{specification_hash}:{cell.cell_id}:{stack.stack_id}:"
                        f"{replicate}:{paired_seed}:{execution_seed}"
                    ).encode()
                ).hexdigest()[:24]
                assignments.append(
                    TailAssignment(
                        assignment_id=assignment_id,
                        split=cell.split,
                        cell_id=cell.cell_id,
                        stack_id=stack.stack_id,
                        replicate=replicate,
                        paired_seed=paired_seed,
                        execution_seed=execution_seed,
                    )
                )
    unhashed = TailManifest(
        experiment_id=spec.experiment_id,
        specification_sha256=specification_hash,
        implementation_revision=implementation_revision,
        assignments=tuple(assignments),
        manifest_sha256="pending",
    )
    return unhashed.model_copy(
        update={"manifest_sha256": content_sha256(_manifest_payload(unhashed))}
    )


def validate_tail_manifest(spec: TailExperimentSpec, manifest: TailManifest) -> None:
    if manifest.experiment_id != spec.experiment_id:
        raise ValueError("manifest experiment differs from specification")
    if manifest.specification_sha256 != spec_sha256(spec):
        raise ValueError("manifest specification hash mismatch")
    if manifest.manifest_sha256 != content_sha256(_manifest_payload(manifest)):
        raise ValueError("manifest content hash mismatch")
    expected = build_tail_manifest(spec, manifest.implementation_revision)
    if expected != manifest:
        raise ValueError("manifest assignment matrix is incomplete or modified")


def validate_outcome_artifact(
    artifact: TailOutcomeArtifact, manifest: TailManifest
) -> None:
    if artifact.manifest_sha256 != manifest.manifest_sha256:
        raise ValueError("outcome artifact manifest hash mismatch")
    if artifact.specification_sha256 != manifest.specification_sha256:
        raise ValueError("outcome artifact specification hash mismatch")
    if artifact.implementation_revision != manifest.implementation_revision:
        raise ValueError("outcome artifact implementation revision mismatch")
    if artifact.artifact_sha256 != content_sha256(_outcome_payload(artifact)):
        raise ValueError("outcome artifact content hash mismatch")
    expected_ids = {
        item.assignment_id
        for item in manifest.assignments
        if item.split is artifact.split
    }
    actual_ids = [item.assignment_id for item in artifact.outcomes]
    if len(actual_ids) != len(set(actual_ids)):
        raise ValueError("outcome artifact contains duplicate assignments")
    if set(actual_ids) != expected_ids:
        raise ValueError("outcome artifact does not exactly cover its manifest split")


def validate_selection_artifact(
    selection: TailSelectionArtifact, manifest: TailManifest
) -> None:
    if selection.manifest_sha256 != manifest.manifest_sha256:
        raise ValueError("selection artifact manifest hash mismatch")
    if selection.specification_sha256 != manifest.specification_sha256:
        raise ValueError("selection artifact specification hash mismatch")
    if selection.selection_sha256 != content_sha256(_selection_payload(selection)):
        raise ValueError("selection artifact content hash mismatch")


def run_tail_split(
    spec: TailExperimentSpec,
    manifest: TailManifest,
    split: TailSplit,
    selection: TailSelectionArtifact | None = None,
) -> TailOutcomeArtifact:
    """Execute the deterministic adapter, enforcing the sealed test boundary."""

    validate_tail_manifest(spec, manifest)
    if split is TailSplit.TEST:
        if selection is None:
            raise ValueError("test execution requires a frozen selection artifact")
        validate_selection_artifact(selection, manifest)
    elif selection is not None:
        raise ValueError("validation execution must not depend on a selection artifact")

    cells = {item.cell_id: item for item in spec.cells}
    stacks = {item.stack_id: item for item in spec.stacks}
    outcomes = tuple(
        run_synthetic_assignment(item, stacks[item.stack_id], cells[item.cell_id])
        for item in manifest.assignments
        if item.split is split
        and (
            selection is None or item.stack_id in selection.authorized_stack_ids
        )
    )
    artifact = TailOutcomeArtifact(
        experiment_id=spec.experiment_id,
        evidence_scope=spec.evidence_scope,
        split=split,
        specification_sha256=manifest.specification_sha256,
        manifest_sha256=manifest.manifest_sha256,
        implementation_revision=manifest.implementation_revision,
        selection_sha256=selection.selection_sha256 if selection else None,
        outcomes=outcomes,
        artifact_sha256="pending",
    )
    artifact = artifact.model_copy(
        update={"artifact_sha256": content_sha256(_outcome_payload(artifact))}
    )
    # Exact coverage applies because the selection authorizes every candidate;
    # this deliberately permits selector comparison without using test data in
    # selection. Restricted operational manifests can authorize fewer stacks.
    if selection is None or set(selection.authorized_stack_ids) == {
        item.stack_id for item in spec.stacks
    }:
        validate_outcome_artifact(artifact, manifest)
    return artifact


def select_tail_stacks(
    spec: TailExperimentSpec,
    manifest: TailManifest,
    validation: TailOutcomeArtifact,
) -> TailSelectionArtifact:
    """Freeze five validation-only selections and test authorization."""

    validate_tail_manifest(spec, manifest)
    if validation.split is not TailSplit.VALIDATION:
        raise ValueError("selection requires a validation artifact")
    validate_outcome_artifact(validation, manifest)
    selected = select_stacks(spec, validation.outcomes)
    artifact = TailSelectionArtifact(
        experiment_id=spec.experiment_id,
        specification_sha256=manifest.specification_sha256,
        manifest_sha256=manifest.manifest_sha256,
        validation_artifact_sha256=validation.artifact_sha256,
        selectors=selected,
        authorized_stack_ids=tuple(sorted(item.stack_id for item in spec.stacks)),
        selection_sha256="pending",
    )
    return artifact.model_copy(
        update={"selection_sha256": content_sha256(_selection_payload(artifact))}
    )
