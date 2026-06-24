"""Compatibility exports for federation-management runtime semantics."""

from __future__ import annotations

from .federation_management_runtime import (
    connect,
    create_federation_execution,
    create_federation_execution_with_mim,
    destroy_federation_execution,
    disconnect,
    force_federate_loss,
    join_federation_execution,
    list_federation_execution_members,
    list_federation_executions,
    register_federation_synchronization_point,
    resign_federation_execution,
    synchronization_point_achieved,
)

__all__ = [
    "connect",
    "create_federation_execution",
    "create_federation_execution_with_mim",
    "destroy_federation_execution",
    "disconnect",
    "force_federate_loss",
    "join_federation_execution",
    "list_federation_execution_members",
    "list_federation_executions",
    "register_federation_synchronization_point",
    "resign_federation_execution",
    "synchronization_point_achieved",
]
