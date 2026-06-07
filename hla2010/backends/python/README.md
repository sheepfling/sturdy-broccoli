# Python Backend Layout

The pure-Python RTI backend is organized by responsibility.

- `state.py`: dataclasses and backend runtime state.
- `engine.py`: shared in-memory federation state and handle registry.
- `reporting.py`: service-report file writer support.
- `declaration.py`: publication, subscription, and advisory declaration service mixin.
- `object.py`: object instance, attribute update, delete, and interaction delivery service mixin.
- `mom.py`: MOM/MIM object refresh, request decoding, and service-reporting mixin.
- `ownership.py`: ownership-management service mixin.
- `time.py`: time-management queueing, retraction, and logical-time service mixin.
- `ddm.py`: data distribution management region and filtering service mixin.
- `backend.py`: concrete `RTIBackend` implementation.
- `factory.py`: backend and ambassador factory functions.

The older flat modules remain for compatibility. New code should prefer imports
from `hla2010.backends.python`.
