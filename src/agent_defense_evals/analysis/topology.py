"""Exact small-graph decomposition helpers for coalition experiments."""

from itertools import combinations, permutations


def all_coalitions(nodes: tuple[str, ...], max_size: int) -> tuple[frozenset[str], ...]:
    return tuple(
        frozenset(coalition)
        for size in range(1, min(max_size, len(nodes)) + 1)
        for coalition in combinations(nodes, size)
    )


def exact_elimination_bags(
    nodes: tuple[str, ...],
    edges: tuple[tuple[str, str], ...],
) -> tuple[int, tuple[frozenset[str], ...]]:
    """Return exact treewidth and bags for an optimal elimination order."""

    base = {node: set() for node in nodes}
    for left, right in edges:
        base[left].add(right)
        base[right].add(left)
    best_width = len(nodes)
    best_bags: tuple[frozenset[str], ...] = ()
    for order in permutations(nodes):
        adjacency = {node: set(neighbors) for node, neighbors in base.items()}
        bags = []
        width = 0
        for node in order:
            neighbors = adjacency[node]
            bag = frozenset({node, *neighbors})
            bags.append(bag)
            width = max(width, len(bag) - 1)
            if width > best_width:
                break
            for left, right in combinations(neighbors, 2):
                adjacency[left].add(right)
                adjacency[right].add(left)
            for neighbor in neighbors:
                adjacency[neighbor].discard(node)
            adjacency[node].clear()
        if width < best_width:
            best_width = width
            best_bags = tuple(bags)
    maximal = tuple(
        bag
        for bag in best_bags
        if not any(bag < candidate for candidate in best_bags)
    )
    return best_width, maximal


def bag_local_coalitions(
    bags: tuple[frozenset[str], ...],
    max_size: int,
) -> frozenset[frozenset[str]]:
    candidates: set[frozenset[str]] = set()
    for bag in bags:
        ordered = tuple(sorted(bag))
        candidates.update(all_coalitions(ordered, max_size))
    return frozenset(candidates)
