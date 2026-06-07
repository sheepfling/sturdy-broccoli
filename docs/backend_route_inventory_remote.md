# Backend Route Inventory: Remote Routes

Remote here means the Python caller talks to a transport host over `grpc` or
`rest`; it does not mean a separate vendor-specific distributed runtime API.

Current real remote routes are:

- Python RTI over `grpc`
- Python RTI over `rest`
- CERTI over `grpc`
- CERTI over `rest`

Current callback contract for both remote transports:

- unary request/response transport calls
- callback polling through `evokeCallback` / `evokeMultipleCallbacks`
- no streaming callback channel yet

Use this page when you want the transport-hosted route story.
