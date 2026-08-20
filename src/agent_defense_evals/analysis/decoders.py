"""Small auditable decoders and uncertainty estimates for binary secrets."""

import math
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence


def wilson_interval(
    successes: int,
    total: int,
    z: float = 1.959963984540054,
) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("total must be positive")
    rate = successes / total
    denominator = 1.0 + z * z / total
    center = (rate + z * z / (2.0 * total)) / denominator
    radius = (
        z
        * math.sqrt(rate * (1.0 - rate) / total + z * z / (4.0 * total * total))
        / denominator
    )
    return max(0.0, center - radius), min(1.0, center + radius)


def accuracy_with_interval(
    expected: Sequence[int],
    predicted: Sequence[int],
) -> tuple[float, float, float]:
    if len(expected) != len(predicted) or not expected:
        raise ValueError("expected and predicted must have equal non-zero length")
    successes = sum(
        left == right for left, right in zip(expected, predicted, strict=True)
    )
    lower, upper = wilson_interval(successes, len(expected))
    return successes / len(expected), lower, upper


class CategoricalBinaryDecoder:
    """Maximum-a-posteriori categorical decoder with deterministic ties."""

    def __init__(self) -> None:
        self._counts: dict[str, Counter[int]] = {}
        self._default = 0

    def fit(self, features: Iterable[str], labels: Iterable[int]) -> None:
        grouped: defaultdict[str, Counter[int]] = defaultdict(Counter)
        overall: Counter[int] = Counter()
        count = 0
        for feature, label in zip(features, labels, strict=True):
            if label not in {0, 1}:
                raise ValueError("binary decoder labels must be bits")
            grouped[feature][label] += 1
            overall[label] += 1
            count += 1
        if count == 0:
            raise ValueError("decoder requires training samples")
        self._counts = dict(grouped)
        self._default = 1 if overall[1] > overall[0] else 0

    def predict(self, features: Iterable[str]) -> tuple[int, ...]:
        predictions = []
        for feature in features:
            counts = self._counts.get(feature)
            if counts is None or counts[0] == counts[1]:
                predictions.append(self._default)
            else:
                predictions.append(1 if counts[1] > counts[0] else 0)
        return tuple(predictions)


class CentroidBinaryDecoder:
    """Nearest-centroid linear probe with no external ML dependency."""

    def __init__(self) -> None:
        self._centroids: dict[int, tuple[float, ...]] = {}

    def fit(
        self,
        vectors: Sequence[Sequence[float]],
        labels: Sequence[int],
    ) -> None:
        if len(vectors) != len(labels) or not vectors:
            raise ValueError("vectors and labels must have equal non-zero length")
        width = len(vectors[0])
        grouped: dict[int, list[Sequence[float]]] = {0: [], 1: []}
        for vector, label in zip(vectors, labels, strict=True):
            if label not in grouped or len(vector) != width:
                raise ValueError(
                    "probe requires fixed-width vectors and both bit labels"
                )
            grouped[label].append(vector)
        if not grouped[0] or not grouped[1]:
            raise ValueError("probe requires examples from both classes")
        self._centroids = {
            label: tuple(
                sum(vector[index] for vector in class_vectors) / len(class_vectors)
                for index in range(width)
            )
            for label, class_vectors in grouped.items()
        }

    def predict(self, vectors: Sequence[Sequence[float]]) -> tuple[int, ...]:
        if set(self._centroids) != {0, 1}:
            raise RuntimeError("probe must be fitted before prediction")
        predictions = []
        for vector in vectors:
            distances = {
                label: sum(
                    (value - centroid[index]) ** 2
                    for index, value in enumerate(vector)
                )
                for label, centroid in self._centroids.items()
            }
            predictions.append(1 if distances[1] < distances[0] else 0)
        return tuple(predictions)


def empirical_mutual_information(
    features: Sequence[str], labels: Sequence[int]
) -> float:
    if len(features) != len(labels) or not features:
        raise ValueError("features and labels must have equal non-zero length")
    joint = Counter(zip(features, labels, strict=True))
    feature_counts = Counter(features)
    label_counts = Counter(labels)
    total = len(features)
    information = 0.0
    for (feature, label), count in joint.items():
        probability = count / total
        independent = (feature_counts[feature] / total) * (label_counts[label] / total)
        information += probability * math.log2(probability / independent)
    return information
