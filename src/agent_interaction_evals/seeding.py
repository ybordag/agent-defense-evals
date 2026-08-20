"""Stable seed derivation independent of Python hash randomization."""

import hashlib


def derive_seed(base_seed: int, *parts: object) -> int:
    """Derive a reproducible unsigned 64-bit seed from namespaced parts."""

    material = ":".join([str(base_seed), *(str(part) for part in parts)])
    digest = hashlib.sha256(material.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)
