# Python RTI Backend Migration Inventory

The split package now owns the implementation under `hla2010_rti_python`.
`hla2010.backends.python` is retained as a compatibility facade during the
migration.

Moved implementation modules:

- `backend.py`
- `callbacks.py`
- `ddm.py`
- `declaration.py`
- `engine.py`
- `factory.py`
- `federation.py`
- `federation_lifecycle.py`
- `federation_sync.py`
- `fom_helpers.py`
- `mom.py`
- `mom_actions.py`
- `mom_reporting.py`
- `object.py`
- `object_delivery.py`
- `ownership.py`
- `reporting.py`
- `save_restore.py`
- `state.py`
- `subscriptions.py`
- `support.py`
- `time.py`
- `time_queue.py`
- `time_services.py`

Known import hazards:

- Relative core imports such as `from ...exceptions` must become absolute
  `from hla2010.exceptions` imports after the files move to `hla2010_rti_python`.
- Backend-contract imports such as `from ..base` must become
  `from hla2010.backends.base`.
- Java conversion imports such as `from ..java_common` must become
  `from hla2010_rti_java_common`.
- Local imports such as `from .state` can stay relative within
  `hla2010_rti_python`.
- `save_restore.py` has a non-local self import:
  `from ..python.state import FederateState, FederationState`; this should become
  `from .state import FederateState, FederationState`.

Remaining compatibility facade plan:

- Keep `hla2010.backends.python.__init__` re-exporting from `hla2010_rti_python`.
- Keep submodule facades for currently used imports.
- Keep the core registry entry point compatible with both the split package and
  source-tree fallback until the repo is fully split.
- Normal repo tests now import the pure Python backend from `hla2010_rti_python`.
  The remaining `hla2010.backends.python` imports are dedicated compatibility
  assertions in `tests/test_rti_python_split_package.py`.
