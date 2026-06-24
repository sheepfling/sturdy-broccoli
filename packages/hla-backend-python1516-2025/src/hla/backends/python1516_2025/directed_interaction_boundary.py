"""Directed-interaction runtime semantics for the dedicated Python 2025 lane."""

from __future__ import annotations

from typing import Any, Callable


def matching_directed_interaction_targets(
    federation: Any,
    *,
    source_federate_key: int,
    object_class_name: str,
    interaction_class_name: str,
    source_regions: set[int],
    region_sets_overlap: Callable[[int, set[int], int, set[int]], bool],
) -> tuple[int, ...]:
    """Return subscribed target federates that should receive a directed interaction."""
    targets: list[int] = []
    for federate_key, subscriptions in federation.subscribed_directed_interactions.items():
        if federate_key == source_federate_key:
            continue
        if interaction_class_name not in subscriptions.get(object_class_name, set()):
            continue
        gated_interactions = federation.directed_interaction_region_gates.get(federate_key, set())
        if interaction_class_name in gated_interactions:
            target_regions = federation.subscribed_interaction_regions.get(federate_key, {}).get(
                interaction_class_name,
                set(),
            )
            if not target_regions or not region_sets_overlap(
                source_federate_key,
                source_regions,
                federate_key,
                target_regions,
            ):
                continue
        targets.append(federate_key)
    return tuple(targets)


__all__ = ["matching_directed_interaction_targets"]
