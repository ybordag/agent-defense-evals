from agent_defense_evals.analysis.topology import (
    all_coalitions,
    bag_local_coalitions,
    exact_elimination_bags,
)


def test_exact_treewidth_for_path_and_clique() -> None:
    nodes = ("a", "b", "c", "d")
    path_width, path_bags = exact_elimination_bags(
        nodes, (("a", "b"), ("b", "c"), ("c", "d"))
    )
    clique_width, _ = exact_elimination_bags(
        nodes,
        tuple(
            (left, right)
            for index, left in enumerate(nodes)
            for right in nodes[index + 1 :]
        ),
    )

    assert path_width == 1
    assert clique_width == 3
    assert frozenset({"b", "c"}) in path_bags


def test_bag_local_coalitions_reduce_path_enumeration() -> None:
    nodes = ("a", "b", "c", "d")
    all_candidates = all_coalitions(nodes, 2)
    _, bags = exact_elimination_bags(
        nodes, (("a", "b"), ("b", "c"), ("c", "d"))
    )
    local = bag_local_coalitions(bags, 2)

    assert frozenset({"b", "c"}) in local
    assert len(local) < len(all_candidates)
