from agent_interaction_evals.seeding import derive_seed


def test_seed_derivation_is_stable_and_namespaced() -> None:
    first = derive_seed(1234, "episode", 1)

    assert derive_seed(1234, "episode", 1) == first
    assert derive_seed(1234, "episode", 2) != first
    assert derive_seed(1234, "monitor", 1) != first
