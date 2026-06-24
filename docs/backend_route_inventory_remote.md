# Backend Route Inventory: Remote Routes

Remote here means the Python caller talks to a transport host over `grpc` or
`rest`; it does not mean a separate vendor-specific distributed runtime API.

Current real remote routes are:

- Python RTI over `grpc`
- Python RTI over `rest`
- Python 2025 FedPro hosted route over `grpc`
- CERTI over `grpc`
- CERTI over `rest`

Important distinctions:

- `Python RTI over grpc/rest` refers to the older hosted route over the 2010
  Python in-memory backend
- `Python 2025 FedPro hosted route over grpc` refers to the bounded typed
  transport route over the main full `hla-backend-python2025` runtime lane
- `hla-backend-shim` retained only as temporary import-compatibility scaffolding and compatibility-wrapper/import-level code
- the implementation owner for 2025 remote work is `python1516_2025` /
  `hla-backend-python2025`
- `hla-backend-shim` is retained only as temporary import-compatibility scaffolding and compatibility-wrapper/import-level
  code and should not be described as the hosted runtime lane
- the operator-facing hosted 2025 lane is `python1516_2025`; do not describe
  legacy wrapper aliases as the hosted runtime owner, and do
  not use wrapper naming as the canonical route name for 2025
  transport-hosted proof
- the 2025 hosted route is real executable runtime evidence, but it is still
  tracked as a bounded runtime slice rather than a full remote-RTI semantics
  or full MOM action/request conformance pass
- the remaining proof burden on that hosted route is transport-seam proof over
  `hla-backend-python2025`, not ownership of separate core RTI semantics

Current callback contract for both remote transports:

- unary request/response transport calls
- callback polling through `evokeCallback` / `evokeMultipleCallbacks`
- no streaming callback channel yet

Route anchors:

- `docs/networked_rti_python.md`
- `packages/hla-transport-grpc/README.md`
- `tests/transport/test_grpc_transport_2025.py`
- `docs/plans/2025_requirements_finish_line.md`

Use this page when you want the transport-hosted route story and the current
distinction between the 2010 hosted Python lane and the bounded hosted 2025
FedPro lane. For 2025, read that lane as hosted evidence over the primary
`hla-backend-python2025` RTI, not as a separate runtime family.
