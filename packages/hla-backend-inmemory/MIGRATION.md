# Python RTI Backend Migration Inventory

The split package now owns the implementation under `hla.backends.inmemory`.
`hla.rti1516e.backends.python` has been removed. Use canonical
`hla.backends.inmemory` imports.

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
  `from hla.rti1516e.exceptions` imports after the files move to `hla.backends.inmemory`.
- Backend-contract imports such as `from ..base` must become
  `from hla.backends.common`.
- Java conversion imports such as `from ..java_common` must become
  `from hla.bridges.java.common`.
- Local imports such as `from .state` can stay relative within
  `hla.backends.inmemory`.
- `save_restore.py` has a non-local self import:
  `from ..python.state import FederateState, FederationState`; this should become
  `from .state import FederateState, FederationState`.

Compatibility facade status:

- `hla.rti1516e.backends.python` and its submodules are intentionally absent.
- Normal repo tests import the pure Python backend from `hla.backends.inmemory`.
- `tests/test_rti_python_split_package.py` asserts the removed legacy path does
  not import.
