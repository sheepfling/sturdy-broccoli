# Python RTI Backend Migration Inventory

The split package now owns the implementation under `hla2010_rti_python`.
`hla2010.backends.python` has been removed. Use canonical
`hla2010_rti_python` imports.

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
  `from hla2010_rti_backend_common`.
- Java conversion imports such as `from ..java_common` must become
  `from hla2010_rti_java_common`.
- Local imports such as `from .state` can stay relative within
  `hla2010_rti_python`.
- `save_restore.py` has a non-local self import:
  `from ..python.state import FederateState, FederationState`; this should become
  `from .state import FederateState, FederationState`.

Compatibility facade status:

- `hla2010.backends.python` and its submodules are intentionally absent.
- Normal repo tests import the pure Python backend from `hla2010_rti_python`.
- `tests/test_rti_python_split_package.py` asserts the removed legacy path does
  not import.
